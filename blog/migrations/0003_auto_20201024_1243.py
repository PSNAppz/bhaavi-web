# Generated by Django 2.2.14 on 2020-10-24 07:13

from django.db import migrations
import wagtail.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_postpage_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postpage',
            name='excerpt',
            field=wagtail.core.fields.RichTextField(blank=True, verbose_name='Short description'),
        ),
    ]
