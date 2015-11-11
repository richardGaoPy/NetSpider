# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LiveHouse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('h_title', models.CharField(max_length=128, verbose_name='\u540d\u79f0')),
                ('h_type', models.CharField(max_length=16, verbose_name='\u5206\u7c7b')),
                ('h_price', models.CharField(max_length=128, verbose_name='\u4ef7\u683c')),
                ('h_content', models.TextField(verbose_name='\u4ecb\u7ecd')),
                ('is_deleted', models.IntegerField(default=0, verbose_name='\u662f\u5426\u5220\u9664', choices=[(0, '\u672a\u5220\u9664'), (1, '\u5df2\u5220\u9664')])),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
            ],
            options={
                'ordering': ('-created_at',),
                'db_table': 'live_house',
                'verbose_name': '\u6f14\u5531\u4f1a\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='LiveHouseCity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('h_city', models.CharField(default='\u5317\u4eac', max_length=48, verbose_name='\u57ce\u5e02')),
                ('h_room', models.CharField(max_length=64, verbose_name='\u573a\u9986')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('lid', models.ForeignKey(to='entertainmentoa.LiveHouse')),
            ],
            options={
                'ordering': ('-lid',),
                'db_table': 'live_house_city',
                'verbose_name': '\u6f14\u5531\u4f1a\u5730\u5740\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='LiveHouseDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('h_date', models.CharField(max_length=256, verbose_name='\u6f14\u5531\u4f1a\u65e5\u671f')),
                ('h_time', models.CharField(max_length=128, verbose_name='\u6f14\u5531\u4f1a\u65f6\u95f4')),
                ('created_at', models.DateTimeField(auto_now=True, verbose_name='\u521b\u5efa\u65f6\u95f4')),
                ('lid', models.ForeignKey(to='entertainmentoa.LiveHouse')),
            ],
            options={
                'db_table': 'live_house_date',
                'verbose_name': '\u6f14\u5531\u4f1a\u65e5\u671f',
            },
        ),
        migrations.CreateModel(
            name='LiveHouseName',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('h_name', models.CharField(max_length=128, verbose_name='\u6f14\u51fa\u6f14\u5458')),
                ('lid', models.ForeignKey(to='entertainmentoa.LiveHouse')),
            ],
            options={
                'db_table': 'live_house_name',
                'verbose_name': '\u6f14\u51fa\u6f14\u5458',
            },
        ),
    ]
