# Generated by Django 5.2 on 2025-04-24 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking_app', '0011_insurance_loan_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='pin',
            field=models.CharField(max_length=6, null=True),
        ),
    ]
