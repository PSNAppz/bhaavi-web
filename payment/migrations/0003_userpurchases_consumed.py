# Generated by Django 2.2.14 on 2020-08-25 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_userpurchases_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpurchases',
            name='consumed',
            field=models.BooleanField(default=0),
        ),
    ]
