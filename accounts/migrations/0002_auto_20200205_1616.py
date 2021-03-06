# Generated by Django 2.1.2 on 2020-02-05 15:16

import accounts.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import lib.storage
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0003_taggeditem_add_unique_index'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaggedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='user',
            name='location',
            field=models.CharField(blank=True, max_length=300, verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='user',
            name='location_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Location ID'),
        ),
        migrations.AddField(
            model_name='user',
            name='short_description',
            field=models.TextField(blank=True, max_length=300, verbose_name='Short description'),
        ),
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, null=True, storage=lib.storage.OverwriteStorage(), upload_to=accounts.models.upload_path_handler_avatar, verbose_name='avatar'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=50, verbose_name='Last Name'),
        ),
        migrations.AddField(
            model_name='taggeduser',
            name='content_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='taggeduser',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts_taggeduser_items', to='taggit.Tag'),
        ),
        migrations.AddField(
            model_name='user',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='accounts.TaggedUser', to='taggit.Tag', verbose_name='tags'),
        ),
    ]
