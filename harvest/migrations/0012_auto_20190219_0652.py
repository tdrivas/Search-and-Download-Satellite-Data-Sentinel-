# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-02-19 06:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0011_remove_sentinel2_products_geom_footprint'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sentinel2_products',
            old_name='geom_footprint2',
            new_name='geom_footprint',
        ),
    ]
