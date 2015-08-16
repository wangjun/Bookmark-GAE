#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lian'
__email__ = "liantian@188.com"

import os
import webapp2
import urllib
from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
from google.appengine.api import memcache

from models import *


class Index(webapp2.RequestHandler):
    def get(self):
        content = memcache.get("index")
        if content is not None:
            pass
        else:
            q = Site.query().order(-Site.count).fetch(keys_only=True)
            all_site = ndb.get_multi(q)
            template_values = {
                "logout": users.create_logout_url('/'),
                "login": users.create_login_url('/'),
                'all_site': all_site,
            }
            path = os.path.join(os.path.dirname(__file__) + '/templates/', 'index.html')
            content = template.render(path, template_values)
            memcache.add("index", content, 3600)
        self.response.out.write(content)


class NewSite(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        template_values = {
            'user': user,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
        }
        path = os.path.join(os.path.dirname(__file__) + '/templates/', 'new.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        obj = Site(
            title=self.request.get('InputTitle'),
            url=self.request.get('InputURL')
        )
        obj.put()
        memcache.delete("index")
        self.redirect('/new/')


class UploadPic(blobstore_handlers.BlobstoreUploadHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/upload_pic/')
        user = users.get_current_user()
        url_string = self.request.get('key')
        key = ndb.Key(urlsafe=url_string)
        site = key.get()
        template_values = {
            'upload_url': upload_url,
            'site': site,
            'user': user,
            "logout": users.create_logout_url('/'),
            "login": users.create_login_url('/'),
        }

        path = os.path.join(os.path.dirname(__file__) + '/templates/', 'upload_pic.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        url_string = self.request.get('key')
        key = ndb.Key(urlsafe=url_string)
        site = key.get()

        origin_img = self.get_uploads("img")[0]
        origin_key = origin_img.key()

        origin_img = images.Image(blob_key=origin_img.key())
        origin_img.resize(width=150)
        origin_img.im_feeling_lucky()
        thumbnail = origin_img.execute_transforms(output_encoding=images.PNG)

        site.imgkey = origin_key
        site.imgurl = images.get_serving_url(origin_key)
        site.thumbnail_uri = thumbnail.encode("base64").replace("\n", "")
        site.put()
        memcache.delete("index")
        self.redirect('/')


class Redirect2Site(webapp2.RequestHandler):
    def get(self, resource):
        site = ndb.Key(urlsafe=resource)
        site = site.get()
        url = site.url
        site.count = site.count + 1
        site.put()
        self.redirect(url.encode('utf8'))


class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)
        # self.response.out.write(resource)


class Thumbnail(webapp2.RequestHandler):
    def get(self, resource):
        if self.request.headers.get('If-Modified-Since'):
            self.error(304)
            return
        thumbnail = self.key2thumbnail(resource)
        # site = ndb.Key(urlsafe=resource)
        # site = site.get()
        # thumbnail = site.thumbnail_uri.decode("base64")
        self.response.headers['Content-Type'] = 'image/png'
        self.response.headers['Last-Modified'] = 'Thu, 19 Feb 2009 16:00:07 GMT'
        self.response.headers['Cache-Control'] = 'public, max-age=315360000'
        self.response.out.write(thumbnail)

    @staticmethod
    def key2thumbnail(key):
        thumbnail = memcache.get(key)
        if thumbnail is not None:
            return thumbnail
        else:
            site = ndb.Key(urlsafe=key).get()
            thumbnail = site.thumbnail_uri.decode("base64")
            memcache.add(key, thumbnail, 86400)
            return thumbnail

    def output_content(self, content, serve=True):
        if serve:
            self.response.out.write(content.body)
        else:
            self.response.set_status(304)

