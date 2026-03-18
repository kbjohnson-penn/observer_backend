from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("research", "0002_remove_visitoccurrence_tier_id_and_more"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            # Column already exists in the DB — no DDL needed
            database_operations=[],
            state_operations=[
                migrations.AddField(
                    model_name="visitoccurrence",
                    name="department",
                    field=models.CharField(blank=True, default="", max_length=255),
                ),
            ],
        )
    ]
