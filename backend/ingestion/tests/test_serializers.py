from django.test import TestCase
from ingestion.serializers import EmissionRowSerializer
from ingestion.models import Tenant, IngestionSource
from datetime import date

class SerializerTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(slug='test', name='Test')
        self.source = IngestionSource.objects.create(tenant=self.tenant, source_type='sap_fuel', name='test')

    def test_emissionrow_requires_quantity_or_normalized(self):
        data = {
            'tenant': self.tenant.id,
            'ingestion_source': self.source.id,
            'source_row_id': '1',
            'source_category': 'fuel',
            'scope': 'scope1',
            'activity_date': date.today(),
            'activity_description': 'desc',
        }
        serializer = EmissionRowSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('either quantity or normalized_quantity is required', str(serializer.errors))

    def test_emissionrow_with_quantity_valid(self):
        data = {
            'tenant': self.tenant.id,
            'ingestion_source': self.source.id,
            'source_row_id': '2',
            'source_category': 'fuel',
            'scope': 'scope1',
            'activity_date': date.today(),
            'activity_description': 'desc',
            'quantity': 100,
            'quantity_unit': 'L'
        }
        serializer = EmissionRowSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
