# Generated by Django 5.0.6 on 2024-06-12 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20240612_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shifts',
            field=models.ManyToManyField(to='api.shift'),
        ),
    ]
