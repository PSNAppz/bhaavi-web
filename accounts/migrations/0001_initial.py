# Generated by Django 3.0.6 on 2020-06-15 11:53

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
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('discount_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('count', models.IntegerField(default=1)),
                ('multiple_usage', models.BooleanField(default=0)),
                ('active', models.BooleanField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MentorCallRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('responded', models.BooleanField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='MentorProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tags', models.CharField(max_length=255)),
                ('experience', models.IntegerField(default=0)),
                ('mentor_type', models.CharField(choices=[('J', 'Jyolsyan'), ('C', 'Councellor')], max_length=1)),
                ('active', models.BooleanField(default=1)),
                ('verified', models.BooleanField(default=0)),
                ('mentor_channel', models.IntegerField(default=accounts.models.channel_gen)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.IntegerField()),
                ('active', models.BooleanField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserRedeemCoupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('discount_percent', models.DecimalField(decimal_places=2, max_digits=5)),
                ('usage', models.IntegerField(default=1)),
                ('active', models.BooleanField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupon_details', to='accounts.Coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_details', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPurchases',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.BooleanField(default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Product')),
                ('users', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_products', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField(blank=True, null=True)),
                ('address', models.CharField(blank=True, max_length=255)),
                ('state', models.CharField(blank=True, max_length=255)),
                ('pincode', models.CharField(max_length=6, null=True, validators=[django.core.validators.RegexValidator('^\\d{1,10}$')])),
                ('father', models.CharField(blank=True, max_length=255)),
                ('mother', models.CharField(blank=True, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='RequestedSchedules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.DateTimeField()),
                ('accepted', models.BooleanField(default=0)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.MentorProfile')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_request_schedule', to='accounts.MentorCallRequest')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='schedule_times', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='mentorcallrequest',
            name='mentor_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.Product'),
        ),
        migrations.AddField(
            model_name='mentorcallrequest',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_request', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='coupon',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_coupon', to='accounts.Product'),
        ),
        migrations.CreateModel(
            name='AcceptedCallSchedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slot', models.DateTimeField()),
                ('completed', models.BooleanField(default=0)),
                ('token', models.CharField(blank=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('mentor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.MentorProfile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accepted_call', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AcademicProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dob', models.DateField()),
                ('qualification', models.CharField(max_length=255)),
                ('stream', models.CharField(max_length=255)),
                ('institute', models.CharField(max_length=255)),
                ('mark', models.CharField(max_length=6, validators=[django.core.validators.RegexValidator('^\\d{1,10}$')])),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='academic', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
