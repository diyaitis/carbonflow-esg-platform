import csv
import io
import re
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from rest_framework import status, views, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Tenant, IngestionSource, EmissionRow, EmissionRowAudit, SOURCE_TYPES
from .serializers import TenantSerializer, EmissionRowSerializer, IngestionSourceSerializer
from .serializers import EmissionFactorSerializer
from .models import EmissionFactor

SAMPLE_TRAVEL_DATA = [
    {
        'record_id': 'TRV-001',
        'category': 'flight',
        'description': 'Round-trip airfare from JFK to LHR',
        'start_date': '2026-04-12',
        'end_date': '2026-04-13',
        'origin': 'JFK',
        'destination': 'LHR',
        'distance_km': 5540,
        'passenger_count': 1,
        'class': 'economy',
    },
    {
        'record_id': 'TRV-002',
        'category': 'hotel',
        'description': 'Three-night stay at London conference hotel',
        'start_date': '2026-04-12',
        'end_date': '2026-04-15',
        'location': 'London',
        'room_nights': 3,
        'hotel_rating': 4,
    },
    {
        'record_id': 'TRV-003',
        'category': 'ground',
        'description': 'Ride share from office to airport',
        'start_date': '2026-04-12',
        'origin': 'New York, NY',
        'destination': 'JFK',
        'distance_km': 25,
        'vehicle_type': 'sedan',
    },
]

EMISSION_FACTORS = {
    'diesel_l': 2.68,
    'gasoline_l': 2.31,
    'electricity_kwh': 0.43,
    'flight_economy_km': 0.18,
    'hotel_room_night': 31.0,
    'ground_km': 0.21,
}

SOURCE_HEADER_MAP = {
    'plant': ['plant', 'werk'],
    'material': ['material', 'material number', 'material number', 'material description'],
    'quantity': ['quantity', 'menge', 'qty'],
    'unit': ['unit', 'einheit'],
    'amount_eur': ['amount', 'betrag in eur', 'betrag'],
    'posting_date': ['posting date', 'document date', 'posting_date', 'document_date', 'date'],
}

def parse_number(value):
    if value is None:
        return None
    cleaned = re.sub(r"[^0-9.,-]", '', str(value)).strip()
    if not cleaned:
        return None
    if cleaned.count(',') > 0 and cleaned.count('.') > 0:
        if cleaned.rfind(',') > cleaned.rfind('.'):
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
    else:
        cleaned = cleaned.replace(',', '.')
    try:
        return float(cleaned)
    except ValueError:
        return None

DATE_FORMATS = ['%Y-%m-%d', '%m/%d/%Y', '%d.%m.%Y', '%Y%m%d']

def parse_date(value):
    if not value:
        return None
    text = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None

def normalize_header(row):
    return {k.strip().lower(): v for k, v in row.items()}

class TenantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tenant.objects.all().order_by('name')
    serializer_class = TenantSerializer

class HealthView(views.APIView):
    def get(self, request):
        return Response({'status': 'ok'})


class IngestionView(views.APIView):
    parser_classes = [MultiPartParser, FormParser]
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024

    def post(self, request):
        tenant_id = request.data.get('tenant_id')
        source_type = request.data.get('source_type')
        name = request.data.get('name') or 'Uploaded source'
        file = request.FILES.get('file')

        if not tenant_id:
            return Response({'error': 'tenant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response({'error': 'tenant not found'}, status=status.HTTP_404_NOT_FOUND)

        if not file:
            return Response({'error': 'file upload required'}, status=status.HTTP_400_BAD_REQUEST)
        if file.size > self.MAX_UPLOAD_SIZE:
            return Response({'error': 'file too large'}, status=status.HTTP_400_BAD_REQUEST)
        if not (file.content_type and 'csv' in file.content_type) and not file.name.lower().endswith('.csv'):
            return Response({'error': 'file must be CSV'}, status=status.HTTP_400_BAD_REQUEST)

        valid_source_types = {choice[0] for choice in SOURCE_TYPES}
        if source_type not in valid_source_types:
            return Response({'error': f'unsupported source_type {source_type}'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = file.read().decode(errors='ignore')
        except Exception:
            return Response({'error': 'unable to read file'}, status=status.HTTP_400_BAD_REQUEST)

        source = IngestionSource.objects.create(
            tenant=tenant,
            source_type=source_type,
            name=name,
            origin_file_name=file.name,
            raw_payload={'mime_type': file.content_type, 'size': file.size},
        )

        try:
            if source_type == 'sap_fuel':
                rows = self._parse_sap_csv(tenant, source, payload)
            elif source_type == 'utility_electricity':
                rows = self._parse_utility_csv(tenant, source, payload)
            else:
                return Response({'error': f'unsupported source_type {source_type}'}, status=status.HTTP_400_BAD_REQUEST)
        except csv.Error as e:
            return Response({'error': 'csv parse error', 'details': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = EmissionRowSerializer(rows, many=True)
        return Response({'rows': serializer.data, 'source_id': source.id}, status=status.HTTP_201_CREATED)

    def _parse_sap_csv(self, tenant, source, payload):
        reader = csv.DictReader(io.StringIO(payload))
        rows = []
        for idx, raw in enumerate(reader, start=1):
            values = normalize_header(raw)
            quantity = parse_number(self._lookup_field(values, SOURCE_HEADER_MAP['quantity']))
            unit = self._lookup_field(values, SOURCE_HEADER_MAP['unit']) or 'L'
            amount = parse_number(self._lookup_field(values, SOURCE_HEADER_MAP['amount_eur']))
            date = parse_date(self._lookup_field(values, SOURCE_HEADER_MAP['posting_date']))
            material = self._lookup_field(values, SOURCE_HEADER_MAP['material']) or 'unknown'
            category = 'fuel' if 'diesel' in material.lower() or 'gasoline' in material.lower() or 'fuel' in material.lower() else 'procurement'
            scope = 'scope1' if category == 'fuel' else 'scope3'
            normalized_quantity, normalized_unit, emission_factor = self._normalize_sap_values(tenant, quantity, unit, category)
            emissions = normalized_quantity * emission_factor if normalized_quantity is not None and emission_factor is not None else None
            suspicious = self._assess_suspicious(category, quantity, unit, amount, emissions)
            row = EmissionRow.objects.create(
                tenant=tenant,
                ingestion_source=source,
                source_row_id=str(idx),
                source_category=category,
                scope=scope,
                activity_date=date,
                activity_description=f"SAP {category} row {idx}",
                original_properties=raw,
                quantity=quantity,
                quantity_unit=unit,
                normalized_quantity=normalized_quantity,
                normalized_unit=normalized_unit,
                emission_factor=emission_factor,
                emissions_kg_co2e=emissions,
                suspicious_reason=suspicious,
            )
            rows.append(row)
        return rows

    def _parse_utility_csv(self, tenant, source, payload):
        reader = csv.DictReader(io.StringIO(payload))
        rows = []
        for idx, raw in enumerate(reader, start=1):
            values = normalize_header(raw)
            start_date = parse_date(values.get('billing start') or values.get('start date') or values.get('period start'))
            end_date = parse_date(values.get('billing end') or values.get('end date') or values.get('period end'))
            usage = parse_number(values.get('total usage (kwh)') or values.get('usage_kwh') or values.get('usage'))
            unit = 'kWh'
            category = 'electricity'
            scope = 'scope2'
            normalized_quantity = usage
            emission_factor = self._get_factor(tenant, 'electricity_kwh') if normalized_quantity is not None else None
            emissions = normalized_quantity * emission_factor if normalized_quantity is not None else None
            suspicious = 'billing period longer than 35 days' if start_date and end_date and (end_date - start_date).days > 35 else ''
            row = EmissionRow.objects.create(
                tenant=tenant,
                ingestion_source=source,
                source_row_id=str(idx),
                source_category=category,
                scope=scope,
                period_start=start_date,
                period_end=end_date,
                activity_description=f"Electricity billing row {idx}",
                original_properties=raw,
                quantity=usage,
                quantity_unit=unit,
                normalized_quantity=normalized_quantity,
                normalized_unit=unit,
                emission_factor=emission_factor,
                emissions_kg_co2e=emissions,
                suspicious_reason=suspicious,
            )
            rows.append(row)
        return rows

    def _normalize_sap_values(self, tenant, quantity, unit, category):
        if quantity is None:
            return None, None, None
        key = None
        if category == 'fuel':
            if 'l' in unit.lower() or 'liter' in unit.lower():
                key = 'diesel_l'
                normalized = quantity
                unit_name = 'L'
            else:
                key = 'diesel_l'
                normalized = quantity
                unit_name = unit or 'L'
        else:
            normalized = quantity
            unit_name = unit or 'EA'
            key = None
        # look up tenant-specific factor if available
        factor = self._get_factor(tenant, key) if key else None
        return normalized, unit_name, factor

    def _get_factor(self, tenant, key):
        if not key:
            return None
        try:
            ef = EmissionFactor.objects.filter(tenant=tenant, key=key).first()
            if ef:
                return ef.factor
        except Exception:
            pass
        return EMISSION_FACTORS.get(key)

    def _assess_suspicious(self, category, quantity, unit, amount, emissions):
        if quantity is None:
            return 'missing quantity'
        if category == 'procurement' and amount and quantity and amount / quantity > 1000:
            return 'high unit price suggests invoice line vs inventory item'
        if unit and unit.lower() not in ['l', 'kg', 'ea', 'kwh']:
            return 'unknown unit'
        return ''

    def _lookup_field(self, values, candidates):
        for candidate in candidates:
            if candidate in values:
                return values[candidate]
        return None

class TravelFetchView(views.APIView):
    def post(self, request):
        tenant_id = request.data.get('tenant_id')
        name = request.data.get('name', 'Travel API import')
        if not tenant_id:
            return Response({'error': 'tenant_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tenant = Tenant.objects.get(pk=tenant_id)
        except Tenant.DoesNotExist:
            return Response({'error': 'tenant not found'}, status=status.HTTP_404_NOT_FOUND)
        source = IngestionSource.objects.create(
            tenant=tenant,
            source_type='travel',
            name=name,
            raw_payload={'records': SAMPLE_TRAVEL_DATA},
        )
        rows = []
        for raw in SAMPLE_TRAVEL_DATA:
            category = raw['category']
            scope = 'scope3'
            normalized_quantity, normalized_unit, emission_factor = self._normalize_travel(tenant, raw)
            emissions = normalized_quantity * emission_factor if normalized_quantity is not None and emission_factor is not None else None
            suspicious = 'estimated distance from airport codes' if category == 'flight' and raw.get('distance_km') is None else ''
            row = EmissionRow.objects.create(
                tenant=tenant,
                ingestion_source=source,
                source_row_id=raw['record_id'],
                source_category=category,
                scope=scope,
                activity_date=parse_date(raw.get('start_date')),
                activity_description=raw.get('description', ''),
                original_properties=raw,
                quantity=raw.get('distance_km') or raw.get('room_nights'),
                quantity_unit=normalized_unit,
                normalized_quantity=normalized_quantity,
                normalized_unit=normalized_unit,
                emission_factor=emission_factor,
                emissions_kg_co2e=emissions,
                suspicious_reason=suspicious,
            )
            rows.append(row)
        serializer = EmissionRowSerializer(rows, many=True)
        return Response({'rows': serializer.data, 'source_id': source.id}, status=status.HTTP_201_CREATED)

    def _normalize_travel(self, tenant, raw):
        category = raw.get('category')
        if category == 'flight':
            distance = raw.get('distance_km') or 1000
            cls = raw.get('class') or 'economy'
            key = 'flight_economy_km' if cls == 'economy' else 'flight_economy_km'
            factor = self._get_factor(tenant, key)
            return distance, 'km', factor
        if category == 'hotel':
            nights = raw.get('room_nights') or 1
            factor = self._get_factor(tenant, 'hotel_room_night')
            return nights, 'room_night', factor
        if category == 'ground':
            distance = raw.get('distance_km') or 10
            factor = self._get_factor(tenant, 'ground_km')
            return distance, 'km', factor
        return None, None, None

class EmissionRowViewSet(viewsets.ModelViewSet):
    queryset = EmissionRow.objects.all().select_related('tenant', 'ingestion_source')
    serializer_class = EmissionRowSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status')
        source_type = self.request.query_params.get('source_type')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if source_type:
            queryset = queryset.filter(ingestion_source__source_type=source_type)
        return queryset.order_by('-created_at')


class EmissionFactorViewSet(viewsets.ModelViewSet):
    queryset = EmissionFactor.objects.all().select_related('tenant')
    serializer_class = EmissionFactorSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        return qs.order_by('key')
    
