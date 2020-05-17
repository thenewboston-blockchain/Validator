# Generated by Django 2.2.10 on 2020-05-17 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bankregistration',
            name='port',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bankregistration',
            name='protocol',
            field=models.CharField(choices=[('http', 'http'), ('https', 'https')], default='http', max_length=5),
            preserve_default=False,
        ),
    ]
