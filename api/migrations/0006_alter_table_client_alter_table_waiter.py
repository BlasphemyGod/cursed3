# Generated by Django 5.0.6 on 2024-06-12 17:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_user_shifts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='table',
            name='client',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tables', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='table',
            name='waiter',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigns', to=settings.AUTH_USER_MODEL),
        ),
    ]
