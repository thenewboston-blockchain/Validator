# Generated by Django 3.0.6 on 2020-06-18 00:45

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('validators', '0003_remove_validator_head_hash'),
    ]

    operations = [
        migrations.AlterField(
            model_name='validator',
            name='port',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
    ]
