# Generated by Django 5.0.1 on 2024-01-29 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_user', models.CharField(max_length=120, verbose_name='From')),
                ('to_user', models.CharField(max_length=120, verbose_name='To')),
                ('amount', models.CharField(max_length=120, verbose_name='Amount')),
                ('is_validated', models.BooleanField(default=False, verbose_name='Tranzactie validata')),
            ],
        ),
    ]
