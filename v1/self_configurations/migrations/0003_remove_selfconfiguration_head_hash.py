# Generated by Django 3.0.6 on 2020-06-13 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('self_configurations', '0002_auto_20200612_0001'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='selfconfiguration',
            name='head_hash',
        ),
    ]
