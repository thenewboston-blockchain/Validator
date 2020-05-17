# Generated by Django 2.2.10 on 2020-05-17 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_configurations', '0005_selfconfiguration_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='selfconfiguration',
            name='protocol',
            field=models.CharField(choices=[('http', 'http'), ('https', 'https')], default='http', max_length=5),
            preserve_default=False,
        ),
    ]
