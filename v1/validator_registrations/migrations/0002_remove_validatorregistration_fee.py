# Generated by Django 3.0.6 on 2020-07-03 22:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('validator_registrations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='validatorregistration',
            name='fee',
        ),
    ]
