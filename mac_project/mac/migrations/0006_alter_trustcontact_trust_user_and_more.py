# Generated by Django 5.0.1 on 2024-01-30 12:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mac', '0005_trustcontact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trustcontact',
            name='trust_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trust_contact_trust_user', to='mac.appuser'),
        ),
        migrations.AlterField(
            model_name='trustcontact',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='trust_contact_user', to='mac.appuser'),
        ),
    ]