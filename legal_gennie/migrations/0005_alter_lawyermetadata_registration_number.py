# Generated by Django 5.0.4 on 2024-12-29 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('legal_gennie', '0004_alter_lawyermetadata_lawyer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lawyermetadata',
            name='registration_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
