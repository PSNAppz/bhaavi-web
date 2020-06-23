# Generated by Django 3.0.7 on 2020-06-23 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_productpackages'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='father',
            new_name='institute',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='mother',
            new_name='qualification',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mark',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mobile',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='stream',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.DeleteModel(
            name='AcademicProfile',
        ),
    ]
