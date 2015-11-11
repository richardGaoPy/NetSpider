# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entertainmentoa', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livehousedate',
            name='h_date',
            field=models.CharField(max_length=512, verbose_name='\u6f14\u5531\u4f1a\u65e5\u671f'),
        ),
    ]
