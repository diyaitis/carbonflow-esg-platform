from django.core.management.base import BaseCommand
from pathlib import Path
from ingestion.views import SAMPLE_TRAVEL_DATA
from ingestion.models import Tenant, IngestionSource
from ingestion.views import IngestionView

class Command(BaseCommand):
    help = 'Run sample ingests using samples in repo'

    def handle(self, *args, **options):
        base = Path(__file__).resolve().parents[4]
        tenant, _ = Tenant.objects.get_or_create(slug='example-client', defaults={'name': 'Example Client'})
        view = IngestionView()

        sap_path = base / 'samples' / 'sap-fuel-sample.csv'
        if sap_path.exists():
            with sap_path.open('r', encoding='utf-8') as f:
                payload = f.read()
            source = IngestionSource.objects.create(tenant=tenant, source_type='sap_fuel', name='sample-sap', raw_payload={'sample': True})
            rows = view._parse_sap_csv(tenant, source, payload)
            self.stdout.write(self.style.SUCCESS(f'Parsed {len(rows)} SAP rows'))
        else:
            self.stdout.write(self.style.WARNING('sap sample not found'))

        util_path = base / 'samples' / 'utility-electricity-sample.csv'
        if util_path.exists():
            with util_path.open('r', encoding='utf-8') as f:
                payload = f.read()
            source = IngestionSource.objects.create(tenant=tenant, source_type='utility_electricity', name='sample-utility', raw_payload={'sample': True})
            rows = view._parse_utility_csv(tenant, source, payload)
            self.stdout.write(self.style.SUCCESS(f'Parsed {len(rows)} utility rows'))
        else:
            self.stdout.write(self.style.WARNING('utility sample not found'))

        # Travel data (sample)
        source = IngestionSource.objects.create(tenant=tenant, source_type='travel', name='sample-travel', raw_payload={'sample': True})
        created = 0
        for raw in SAMPLE_TRAVEL_DATA:
            # replicate logic in TravelFetchView
            created += 1
        self.stdout.write(self.style.SUCCESS(f'Pretend-created {created} travel sample rows'))
