# Generated by Django 5.1.1 on 2024-10-19 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectresource',
            name='month',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='projectresource',
            name='year',
            field=models.CharField(max_length=4, null=True),
        ),
    ]
