# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-03-05 12:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stroyprombeton', '0019_catalog_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='option',
            name='diameter_in',
        ),
        migrations.RemoveField(
            model_name='option',
            name='diameter_out',
        ),
        migrations.RemoveField(
            model_name='option',
            name='height',
        ),
        migrations.RemoveField(
            model_name='option',
            name='length',
        ),
        migrations.RemoveField(
            model_name='option',
            name='specification',
        ),
        migrations.RemoveField(
            model_name='option',
            name='volume',
        ),
        migrations.RemoveField(
            model_name='option',
            name='weight',
        ),
        migrations.RemoveField(
            model_name='option',
            name='width',
        ),
        migrations.RemoveField(
            model_name='product',
            name='code',
        ),
        migrations.RemoveField(
            model_name='product',
            name='date_price_updated',
        ),
        migrations.RemoveField(
            model_name='product',
            name='diameter_in',
        ),
        migrations.RemoveField(
            model_name='product',
            name='diameter_out',
        ),
        migrations.RemoveField(
            model_name='product',
            name='height',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_new_price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='length',
        ),
        migrations.RemoveField(
            model_name='product',
            name='mark',
        ),
        migrations.RemoveField(
            model_name='product',
            name='specification',
        ),
        migrations.RemoveField(
            model_name='product',
            name='volume',
        ),
        migrations.RemoveField(
            model_name='product',
            name='weight',
        ),
        migrations.RemoveField(
            model_name='product',
            name='width',
        ),
    ]
