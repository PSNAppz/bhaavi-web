# Generated by Django 3.0.7 on 2020-07-16 05:27

import accounts.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.CharField(default=accounts.models.id_gen, editable=False, max_length=32, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('full_name', models.CharField(max_length=255)),
                ('customer', models.BooleanField(default=False, verbose_name='customer')),
                ('jyolsyan', models.BooleanField(default=False, verbose_name='jyolsyan ')),
                ('mentor', models.BooleanField(default=False, verbose_name='mentor')),
                ('admin', models.BooleanField(default=False, verbose_name='admin')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_active', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.CharField(blank=True, max_length=11, null=True)),
                ('birthtime', models.CharField(blank=True, max_length=255, null=True)),
                ('dst', models.CharField(blank=True, max_length=255, null=True)),
                ('birthplace', models.CharField(blank=True, max_length=255, null=True)),
                ('latlong', models.CharField(blank=True, max_length=255, null=True)),
                ('mobile', models.CharField(blank=True, max_length=15)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('pincode', models.CharField(max_length=6, null=True, validators=[django.core.validators.RegexValidator('^\\d{1,10}$')])),
                ('qualification', models.CharField(blank=True, max_length=255)),
                ('stream', models.CharField(blank=True, max_length=255)),
                ('institute', models.CharField(blank=True, max_length=255)),
                ('mark', models.CharField(blank=True, max_length=6)),
                ('gender', models.CharField(blank=True, max_length=255, null=True)),
                ('siblings', models.CharField(blank=True, max_length=255, null=True)),
                ('contact', models.CharField(blank=True, max_length=255, null=True)),
                ('hobbies', models.CharField(blank=True, max_length=255, null=True)),
                ('guardian_name', models.CharField(blank=True, max_length=255, null=True)),
                ('career_concern', models.CharField(blank=True, max_length=255, null=True)),
                ('personal_concern', models.CharField(blank=True, max_length=255, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
