# Generated by Django 2.2.14 on 2020-07-21 10:18

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('schedule', '0002_assignsubmitreport_usersubmitreport'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserSubmitReport',
            new_name='UserSubmitDetails',
        ),
    ]
