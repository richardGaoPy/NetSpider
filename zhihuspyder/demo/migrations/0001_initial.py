# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SubclassTopics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('topic_id', models.IntegerField(verbose_name='topic id.')),
                ('sub_topic_name', models.CharField(max_length=64, verbose_name='subclass topic name')),
                ('description', models.CharField(default=b'', max_length=256, verbose_name='topic description')),
                ('user_counts', models.IntegerField(verbose_name='topic follow user number')),
                ('is_self', models.IntegerField(default=0, verbose_name='whether is father topic')),
                ('is_deleted', models.IntegerField(default=0, verbose_name='whether delete', choices=[(1, 'deleted'), (0, 'not deleted')])),
                ('last_update', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-last_update',),
                'db_table': 'subclass_topics',
            },
        ),
        migrations.CreateModel(
            name='Topics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_id', models.IntegerField(verbose_name='data_id')),
                ('topic_name', models.CharField(max_length=64, verbose_name='topic name')),
                ('user_counts', models.IntegerField(default=0, verbose_name='user counts')),
                ('is_deleted', models.IntegerField(default=0, verbose_name='whether delete', choices=[(1, 'deleted'), (0, 'not deleted')])),
                ('last_update', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-last_update',),
                'db_table': 'topics',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sex', models.IntegerField(default=2, choices=[(1, 'man'), (0, 'lady'), (2, 'un_define')])),
                ('fans_number', models.IntegerField(verbose_name='fans number count')),
                ('follows_number', models.IntegerField(verbose_name='follows number count')),
                ('social_contact', models.CharField(default=b'', max_length=128, verbose_name='social contact')),
                ('location_by_self', models.CharField(default=b'', max_length=64, verbose_name='coordinating yourself')),
                ('abstract', models.CharField(default=b'', max_length=256, verbose_name='abstract')),
                ('employment', models.CharField(default=b'', max_length=64, verbose_name='employment')),
                ('domicile', models.CharField(default=b'', max_length=32, verbose_name='live city')),
                ('educational', models.CharField(default=b'', max_length=128, verbose_name='educational information')),
                ('last_update', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-last_update',),
                'db_table': 'info',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_number', models.CharField(max_length=64, verbose_name='user mi id.')),
                ('user_name', models.CharField(max_length=64, verbose_name='user name')),
                ('user_account', models.CharField(max_length=128, verbose_name='user_name')),
                ('is_queried', models.IntegerField(default=0, verbose_name='whether query people', choices=[(1, 'deleted'), (0, 'not deleted')])),
                ('is_deleted', models.IntegerField(default=0, choices=[(1, 'deleted'), (0, 'not deleted')])),
                ('last_update', models.DateTimeField(auto_now_add=True)),
                ('topic_id', models.ManyToManyField(to='demo.SubclassTopics')),
            ],
            options={
                'ordering': ('-last_update',),
                'db_table': 'users',
            },
        ),
        migrations.AddField(
            model_name='userinfo',
            name='user_id',
            field=models.ForeignKey(to='demo.Users'),
        ),
        migrations.AddField(
            model_name='subclasstopics',
            name='father_topic_id',
            field=models.ForeignKey(to='demo.Topics'),
        ),
    ]
