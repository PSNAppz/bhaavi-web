# Generated by Django 3.0.7 on 2020-07-01 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_auto_20200630_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mentorcallrequest',
            name='report_submitted',
            field=models.BooleanField(default=1),
        ),
    ]
