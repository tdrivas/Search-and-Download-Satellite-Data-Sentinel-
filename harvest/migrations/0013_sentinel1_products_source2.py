# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2019-03-02 21:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('harvest', '0012_auto_20190219_0652'),
    ]

    operations = [
        migrations.AddField(
            model_name='sentinel1_products',
            name='source2',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.CASCADE, to='harvest.hubs'),
        ),
    ]