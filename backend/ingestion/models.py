from django.db import models

SOURCE_TYPES = [
    ('sap_fuel', 'SAP Fuel / Procurement'),
    ('utility_electricity', 'Utility Electricity'),
    ('travel', 'Corporate Travel'),
]

ROW_STATUS = [
    ('pending', 'Pending Review'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

SCOPE_CHOICES = [
    ('scope1', 'Scope 1'),
    ('scope2', 'Scope 2'),
    ('scope3', 'Scope 3'),
]

class Tenant(models.Model):
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class IngestionSource(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='sources')
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPES)
    name = models.CharField(max_length=128)
    external_id = models.CharField(max_length=256, blank=True, null=True)
    raw_payload = models.JSONField(blank=True, null=True)
    origin_file_name = models.CharField(max_length=256, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.source_type})'

class EmissionRow(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='emissions')
    ingestion_source = models.ForeignKey(IngestionSource, on_delete=models.SET_NULL, null=True, related_name='rows')
    source_row_id = models.CharField(max_length=128, blank=True, null=True)
    source_category = models.CharField(max_length=128)
    scope = models.CharField(max_length=16, choices=SCOPE_CHOICES)
    activity_date = models.DateField(blank=True, null=True)
    period_start = models.DateField(blank=True, null=True)
    period_end = models.DateField(blank=True, null=True)
    activity_description = models.CharField(max_length=256, blank=True)
    original_properties = models.JSONField(default=dict)
    quantity = models.FloatField(blank=True, null=True)
    quantity_unit = models.CharField(max_length=32, blank=True)
    normalized_quantity = models.FloatField(blank=True, null=True)
    normalized_unit = models.CharField(max_length=32, blank=True)
    emission_factor = models.FloatField(blank=True, null=True)
    emissions_kg_co2e = models.FloatField(blank=True, null=True)
    suspicious_reason = models.CharField(max_length=256, blank=True)
    status = models.CharField(max_length=16, choices=ROW_STATUS, default='pending')
    reviewed_by = models.CharField(max_length=128, blank=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    edited_by = models.CharField(max_length=128, blank=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.source_category} {self.activity_description or self.source_row_id}'

class EmissionRowAudit(models.Model):
    emission_row = models.ForeignKey(EmissionRow, on_delete=models.CASCADE, related_name='audits')
    change_type = models.CharField(max_length=64)
    changed_by = models.CharField(max_length=128, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict)

    class Meta:
        ordering = ['-changed_at']


class EmissionFactor(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='emission_factors')
    key = models.CharField(max_length=64, help_text='Lookup key, e.g. diesel_l, electricity_kwh, flight_economy_km')
    factor = models.FloatField(help_text='kg CO2e per unit')
    effective_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'key')

    def __str__(self):
        return f'{self.tenant.slug} {self.key}={self.factor}'
