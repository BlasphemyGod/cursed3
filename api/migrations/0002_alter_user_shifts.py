# Generated by Django 5.0.6 on 2024-06-12 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='shifts',
            field=models.ManyToManyField(blank=True, to='api.shift'),
        ),
    ]