# Generated by Django 5.0.4 on 2024-12-29 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_gennie', '0006_alter_lawyermetadata_registration_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyermetadata',
            name='call_fee',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='lawyermetadata',
            name='consultation_fee',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True),
        ),
    ]
