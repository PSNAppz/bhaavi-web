# Generated by Django 2.2.14 on 2020-07-24 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_auto_20200723_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='astrologercareerreport',
            name='submitted',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
