# Generated by Django 5.0.1 on 2024-01-30 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mac', '0009_alter_transaction_pin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='unlock_pin',
            field=models.TextField(blank=True, verbose_name='PIN'),
        ),
    ]
