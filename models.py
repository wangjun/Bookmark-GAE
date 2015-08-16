#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lian'

from google.appengine.ext import ndb


class Site(ndb.Model):
    title = ndb.TextProperty(indexed=False, verbose_name=u"标题")
    url = ndb.TextProperty(indexed=False, verbose_name=u"地址")
    imgurl = ndb.TextProperty(indexed=False, verbose_name=u"图片地址")
    count = ndb.IntegerProperty(default=0, verbose_name=u"计数")
    imgkey = ndb.BlobKeyProperty(verbose_name=u"源图片")
    thumbnail_uri = ndb.TextProperty(verbose_name=u"缩略图的Base64")