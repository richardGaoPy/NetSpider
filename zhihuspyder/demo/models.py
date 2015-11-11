# -*- coding:utf-8 -*-
"""
    models.py
    ~~~~~~~~~
    zhi hu database models.
"""
from django.db import models

TRUE = 1
FALSE = 0

choices_status = (
        (TRUE, u'deleted'),
        (FALSE, u'not deleted')
)


class Topics(models.Model):
    """father topic model"""
    data_id = models.IntegerField(verbose_name=u'data_id')
    topic_name = models.CharField(verbose_name=u'topic name', max_length=64)
    user_counts = models.IntegerField(verbose_name=u'user counts', default=0)
    is_deleted = models.IntegerField(verbose_name=u'whether delete', choices=choices_status, default=FALSE)
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'topics'
        ordering = ('-last_update', )

    def __unicode__(self):
        return u"father topic name is {}".format(self.topic_name)


class SubclassTopics(models.Model):
    """subclass topic model"""
    father_topic_id = models.ForeignKey(Topics)
    # user_id = models.ManyToManyField(Users)
    topic_id = models.IntegerField(verbose_name=u'topic id.')
    sub_topic_name = models.CharField(verbose_name=u'subclass topic name', max_length=64)
    description = models.CharField(verbose_name=u'topic description', max_length=256, default='')
    user_counts = models.IntegerField(verbose_name=u'topic follow user number')
    is_self = models.IntegerField(verbose_name=u'whether is father topic', default=FALSE)
    is_deleted = models.IntegerField(verbose_name=u'whether delete', choices=choices_status, default=FALSE)
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subclass_topics'
        ordering = ('-last_update', )

    def __unicode__(self):
        return u'subclass topic name is {}'.format(self.sub_topic_name)


class Users(models.Model):
    """users base info."""
    topic_id = models.ManyToManyField(SubclassTopics)
    user_number = models.CharField(verbose_name=u'user mi id.', max_length=64)
    user_name = models.CharField(verbose_name=u'user name', max_length=64)
    user_account = models.CharField(verbose_name=u'user_name', max_length=128)
    is_queried = models.IntegerField(verbose_name=u'whether query people', choices=choices_status, default=FALSE)
    is_deleted = models.IntegerField(choices=choices_status, default=FALSE)
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        ordering = ('-last_update', )

    def __unicode__(self):
        return u'user name is {}'.format(self.user_name)

M = 1
L = 0
U = 2


class UserInfo(models.Model):
    """user info"""
    choices_sex = (
        (M, u'man'),
        (L, u'lady'),
        (U, u'un_define')
    )
    user_id = models.ForeignKey(Users)
    sex = models.IntegerField(choices=choices_sex, default=U)
    fans_number = models.IntegerField(verbose_name=u'fans number count')
    follows_number = models.IntegerField(verbose_name=u'follows number count')
    social_contact = models.CharField(verbose_name=u'social contact', max_length=128, default='')
    location_by_self = models.CharField(verbose_name=u'coordinating yourself', max_length=64, default='')
    abstract = models.CharField(verbose_name=u'abstract', max_length=256, default='')
    employment = models.CharField(verbose_name=u'employment', max_length=64, default='')
    domicile = models.CharField(verbose_name=u'live city', max_length=32, default='')
    # occupations = models.CharField(verbose_name=u'occupations information', max_length=128, default='')
    educational = models.CharField(verbose_name=u'educational information', max_length=128, default='')
    # nick_topics = models.CharField(verbose_name=u'hot topics', max_length=64, default='')
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'info'
        ordering = ('-last_update', )

    def __unicode__(self):
        return u'{} \n {} \n {} \n'.format([self.location_self, self.abstract, self.industry])

