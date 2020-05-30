# Generated by Django 3.0.6 on 2020-05-30 21:13

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import thenewboston.utils.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('banks', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankRegistration',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, db_index=True, null=True)),
                ('modified_date', models.DateTimeField(auto_now=True, db_index=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('fee', models.DecimalField(decimal_places=16, default=1e-16, max_digits=32, validators=[django.core.validators.MinValueValidator(1e-16), thenewboston.utils.validators.validate_is_real_number])),
                ('status', models.CharField(choices=[('ACCEPTED', 'ACCEPTED'), ('DECLINED', 'DECLINED'), ('PENDING', 'PENDING')], default='PENDING', max_length=8)),
                ('account_number', models.CharField(max_length=256)),
                ('ip_address', models.GenericIPAddressField()),
                ('port', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(65535)])),
                ('protocol', models.CharField(choices=[('http', 'http'), ('https', 'https')], max_length=5)),
                ('bank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bank_registrations', to='banks.Bank')),
            ],
            options={
                'default_related_name': 'bank_registrations',
            },
        ),
    ]
