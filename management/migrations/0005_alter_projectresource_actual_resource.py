# Generated by Django 5.1.1 on 2024-10-19 03:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_alter_projectresource_actual_resource'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectresource',
            name='actual_resource',
            field=models.FloatField(default=0.0),
        ),
    ]
