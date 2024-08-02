from django.db import migrations, models
import uuid


def generate_unique_csn_number(apps, schema_editor):
    Encounter = apps.get_model('dashboard', 'Encounter')
    existing_csn_numbers = set(Encounter.objects.exclude(csn_number__isnull=True).exclude(
        csn_number='').values_list('csn_number', flat=True))

    for encounter in Encounter.objects.filter(csn_number__isnull=True) | Encounter.objects.filter(csn_number=''):
        unique_csn_number = str(uuid.uuid4())[:10]
        while unique_csn_number in existing_csn_numbers or unique_csn_number == '':
            unique_csn_number = str(uuid.uuid4())[:10]
        encounter.csn_number = unique_csn_number
        existing_csn_numbers.add(unique_csn_number)
        try:
            encounter.save()
        except Exception as e:
            print(f"Error saving Encounter with ID {encounter.id}: {e}")


class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='encounter',
            name='csn_number',
            field=models.CharField(
                max_length=10, unique=True, null=True, blank=True, verbose_name='CSN Number'),
        ),
        migrations.RunPython(generate_unique_csn_number),
    ]
