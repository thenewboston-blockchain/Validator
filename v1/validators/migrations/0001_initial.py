# Generated by Django 3.0.6 on 2020-07-03 16:56

import django.core.validators
from django.db import migrations, models
import thenewboston.utils.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Validator',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('account_number', models.CharField(max_length=64)),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('node_identifier', models.CharField(max_length=64, unique=True)),
                ('port', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('protocol', models.CharField(choices=[('http', 'http'), ('https', 'https')], max_length=5)),
                ('version', models.CharField(max_length=32)),
                ('default_transaction_fee', models.DecimalField(decimal_places=16, default=1e-16, max_digits=32, validators=[django.core.validators.MinValueValidator(1e-16), thenewboston.utils.validators.validate_is_real_number])),
                ('registration_fee', models.DecimalField(decimal_places=16, default=1e-16, max_digits=32, validators=[django.core.validators.MinValueValidator(1e-16), thenewboston.utils.validators.validate_is_real_number])),
                ('root_account_file', models.URLField(max_length=1024)),
                ('root_account_file_hash', models.CharField(max_length=64)),
                ('seed_block_identifier', models.CharField(blank=True, max_length=64)),
                ('trust', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'default_related_name': 'validators',
            },
        ),
    ]
