# Generated by Django 3.0.6 on 2020-05-28 02:08

import django.core.validators
from django.db import migrations, models
import thenewboston.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Validator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(max_length=64)),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('network_identifier', models.CharField(max_length=64, unique=True)),
                ('port', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('protocol', models.CharField(choices=[('http', 'http'), ('https', 'https')], max_length=5)),
                ('version', models.CharField(max_length=32)),
                ('default_transaction_fee', models.DecimalField(decimal_places=16, default=0, max_digits=32, validators=[django.core.validators.MinValueValidator(0), thenewboston.utils.validators.validate_is_real_number])),
                ('registration_fee', models.DecimalField(decimal_places=16, default=0, max_digits=32, validators=[django.core.validators.MinValueValidator(0), thenewboston.utils.validators.validate_is_real_number])),
                ('trust', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'default_related_name': 'validators',
            },
        ),
    ]
