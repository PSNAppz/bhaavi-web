# Generated by Django 3.0.7 on 2020-06-24 11:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0003_auto_20200623_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(blank=True, max_length=255)),
                ('strongly_agree', models.IntegerField(default=4)),
                ('agree', models.IntegerField(default=3)),
                ('disagree', models.IntegerField(default=2)),
                ('strongly_disagree', models.IntegerField(default=1)),
                ('category', models.CharField(blank=True, max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pragmatic_score', models.CharField(blank=True, max_length=5)),
                ('industrious_score', models.CharField(blank=True, max_length=5)),
                ('creative_score', models.CharField(blank=True, max_length=5)),
                ('socialite_score', models.CharField(blank=True, max_length=5)),
                ('explorer_score', models.CharField(blank=True, max_length=5)),
                ('traditional_score', models.CharField(blank=True, max_length=5)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='result_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.IntegerField(default=2)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('purchase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='picset_purchase', to='accounts.UserPurchases')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='picset.Question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answer_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]