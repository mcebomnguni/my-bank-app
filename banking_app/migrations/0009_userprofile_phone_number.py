# Generated by Django 5.2 on 2025-04-24 07:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking_app', '0008_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default='', max_length=15),
        ),
    ]
