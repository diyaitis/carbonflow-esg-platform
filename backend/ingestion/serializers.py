from rest_framework import serializers
from .models import Tenant, IngestionSource, EmissionRow

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'slug', 'name']

class IngestionSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionSource
        fields = ['id', 'tenant', 'source_type', 'name', 'external_id', 'origin_file_name', 'uploaded_at']

class EmissionRowSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)
    ingestion_source = IngestionSourceSerializer(read_only=True)

    class Meta:
        model = EmissionRow
        fields = [
            'id', 'tenant', 'ingestion_source', 'source_row_id', 'source_category', 'scope',
            'activity_date', 'period_start', 'period_end', 'activity_description', 'original_properties',
            'quantity', 'quantity_unit', 'normalized_quantity', 'normalized_unit',
            'emission_factor', 'emissions_kg_co2e', 'suspicious_reason', 'status',
            'reviewed_by', 'reviewed_at', 'edited_by', 'edited_at', 'note',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['tenant', 'ingestion_source', 'emissions_kg_co2e', 'suspicious_reason', 'created_at', 'updated_at']

    def validate(self, data):
        if data.get('quantity') is None and data.get('normalized_quantity') is None:
            raise serializers.ValidationError('either quantity or normalized_quantity is required')
        return data


class EmissionFactorSerializer(serializers.ModelSerializer):
    tenant = TenantSerializer(read_only=True)

    class Meta:
        model = __import__('ingestion.models', fromlist=['EmissionFactor']).EmissionFactor
        fields = ['id', 'tenant', 'key', 'factor', 'effective_date', 'created_at']
        read_only_fields = ['tenant', 'created_at']
