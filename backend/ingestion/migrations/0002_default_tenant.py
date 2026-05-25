from django.db import migrations


def create_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('ingestion', 'Tenant')
    Tenant.objects.get_or_create(slug='example-client', defaults={'name': 'Example Client'})


def reverse_default_tenant(apps, schema_editor):
    Tenant = apps.get_model('ingestion', 'Tenant')
    Tenant.objects.filter(slug='example-client').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('ingestion', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_tenant, reverse_default_tenant),
    ]
