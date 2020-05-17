# Generated by Django 2.2.10 on 2020-05-17 01:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banks', '0002_bank_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='bank',
            name='protocol',
            field=models.CharField(choices=[('http', 'http'), ('https', 'https')], default='http', max_length=5),
            preserve_default=False,
        ),
    ]
