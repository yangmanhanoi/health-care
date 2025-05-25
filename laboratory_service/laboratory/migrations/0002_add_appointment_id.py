# Generated migration for adding appointment_id to LabTestOrder

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('laboratory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='labtestorder',
            name='appointment_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
