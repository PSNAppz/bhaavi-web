# Generated by Django 3.0.7 on 2020-06-26 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('picset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='attendee_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
