# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-05 22:42
from __future__ import unicode_literals

import dam.models
import dam.validators
import django.contrib.postgres.fields.hstore
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dam', '0006_auto_20170504_1332'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='caption',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='photo',
            name='proxy_height',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='photo',
            name='proxy_width',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='exif_tags',
            field=django.contrib.postgres.fields.hstore.HStoreField(blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='format',
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AlterField(
            model_name='photo',
            name='galleries',
            field=models.ManyToManyField(blank=True, related_name='photos', to='dam.Gallery'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='height',
            field=models.IntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image_data',
            field=models.ImageField(height_field='height', upload_to=dam.models._gen_image_filename, validators=[dam.validators.file_size], width_field='width'),
        ),
        migrations.AlterField(
            model_name='photo',
            name='original_filename',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='proxy_data',
            field=models.ImageField(blank=True, null=True, upload_to=dam.models._gen_thumbs_filename),
        ),
        migrations.AlterField(
            model_name='photo',
            name='width',
            field=models.IntegerField(blank=True),
        ),
    ]