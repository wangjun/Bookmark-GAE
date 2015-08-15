#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lian'
__email__ = "liantian@188.com"

import os
import webapp2
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import memcache

from models import *


class Index(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        q = Site.query().order(-Site.count).fetch(keys_only=True)
        all_site = ndb.get_multi(q)
        template_values = {
            'user': user,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
            'all_site':all_site,
        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'index.html')
        self.response.out.write(template.render(path, template_values))


class NewSite(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
            'user': user,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
        }
        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):

        obj = Site(
            title=self.request.get('InputTitle'),
            url=self.request.get('InputURL')
        )
        obj.put()
        self.redirect('/')


class UploadPic(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_pic/')
        user = users.get_current_user()
        url_string = self.request.get('key')
        key = ndb.Key(urlsafe=url_string)
        site = key.get()
        template_values = {
            'upload_url':upload_url,
            'site':site,
            'user': user,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
        }

        path = os.path.join(os.path.dirname(__file__)+'/templates/', 'upload_pic.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        upload = self.get_uploads("img")[0]
        url_string = self.request.get('key')
        key = ndb.Key(urlsafe=url_string)
        site = key.get()
        site.imgurl = images.get_serving_url(upload.key())
        site.put()

        self.redirect('/')


class Redirect2Site(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        site = ndb.Key(urlsafe=key)
        site = site.get()
        url = site.url
        site.count = site.count + 1
        site.put()
        # url = self.key2url(key)
        self.redirect(url.encode('utf8'))
        # self.response.out.write(url)

    @staticmethod
    def key2url(key):
        url = memcache.get('key')
        if url is not None:
            return url
        else:
            site = ndb.Key(urlsafe=key).get()
            url = site.imgurl
            memcache.add('key', url, 86400)
            return url
