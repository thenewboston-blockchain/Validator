# Generated by Django 3.0.6 on 2020-06-27 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_configurations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='selfconfiguration',
            name='seed_block_identifier',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
