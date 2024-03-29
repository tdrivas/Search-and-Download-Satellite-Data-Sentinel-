# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-02-09 09:36
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0002_sentinel2_products_geom_footprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentinel1_products',
            name='geom_footprint',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326),
        ),
        migrations.AddField(
            model_name='sentinel3_products',
            name='geom_footprint',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326),
        ),
    ]
