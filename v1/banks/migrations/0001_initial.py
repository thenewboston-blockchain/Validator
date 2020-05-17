# Generated by Django 2.2.10 on 2020-05-17 01:16

import django.core.validators
from django.db import migrations, models
import v1.network.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=256)),
                ('ip_address', models.GenericIPAddressField(unique=True)),
                ('port', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('protocol', models.CharField(choices=[('http', 'http'), ('https', 'https')], max_length=5)),
                ('version', models.CharField(max_length=32)),
                ('default_transaction_fee', models.DecimalField(decimal_places=16, default=0, max_digits=32, validators=[django.core.validators.MinValueValidator(0), v1.network.utils.validators.validate_is_real_number])),
                ('registration_fee', models.DecimalField(decimal_places=16, default=0, max_digits=32, validators=[django.core.validators.MinValueValidator(0), v1.network.utils.validators.validate_is_real_number])),
                ('trust', models.DecimalField(decimal_places=2, default=0, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
            options={
                'default_related_name': 'banks',
            },
        ),
    ]
