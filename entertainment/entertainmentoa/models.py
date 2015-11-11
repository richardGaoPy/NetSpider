# -*- coding:utf-8 -*-

from django.db import models

NOT_DELETED = 0
DELETED = 1


class LiveHouse(models.Model):
    """table of vocal concert."""
    choice_status = (
        (NOT_DELETED, u'未删除'),
        (DELETED, u'已删除')
    )
    h_title = models.CharField(verbose_name=u'名称', max_length=128)
    h_type = models.CharField(verbose_name=u'分类', max_length=16)
    h_price = models.CharField(verbose_name=u'价格', max_length=128)
    h_content = models.TextField(verbose_name=u'介绍')
    is_deleted = models.IntegerField(verbose_name=u'是否删除', choices=choice_status, default=NOT_DELETED)
    created_at = models.DateTimeField(verbose_name=u'创建时间', auto_now=True)

    class Meta:
        db_table = 'live_house'
        ordering = ('-created_at', )
        verbose_name = u'演唱会信息'

    def __unicode__(self):
        return u'演唱会：%s\n分类：%s' % (self.title, self.type)


class LiveHouseCity(models.Model):
    """table of vocal concert's city"""
    h_city = models.CharField(verbose_name=u'城市', max_length=48, default=u"北京")
    h_room = models.CharField(verbose_name=u'场馆', max_length=64)
    lid = models.ForeignKey(LiveHouse)
    created_at = models.DateTimeField(verbose_name=u'创建时间', auto_now=True)

    class Meta:
        db_table = 'live_house_city'
        ordering = ('-lid', )
        verbose_name = u'演唱会地址信息'

    def __unicode__(self):
        return u'演唱会地址：\n%s\n%s\n' % (self.city, self.room)


class LiveHouseDate(models.Model):
    """table of vocal concert's date"""
    h_date = models.CharField(verbose_name=u'演唱会日期', max_length=512)
    h_time = models.CharField(verbose_name=u'演唱会时间', max_length=128)
    lid = models.ForeignKey(LiveHouse)
    created_at = models.DateTimeField(verbose_name=u'创建时间', auto_now=True)

    class Meta:
        db_table = 'live_house_date'
        verbose_name = u'演唱会日期'


class LiveHouseName(models.Model):
    """table of vocal concert's master"""
    h_name = models.CharField(verbose_name=u'演出演员', max_length=128)
    lid = models.ForeignKey(LiveHouse)

    class Meta:
        db_table = 'live_house_name'
        verbose_name = u'演出演员'