#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from models.Users import Users


class UsersSettings(db.Model):
	user = db.ReferenceProperty(Users, collection_name='settings')
	name = db.StringProperty(required=True)
	value = db.StringProperty()

	@staticmethod
	def set(user,name,value=''):
		keyName = '%s/%s' % (user.jid, name)
		UsersSettings(key_name=keyName,user=user,name=name,value=str(value)).put()

	@staticmethod
	def get(user,name=None):
		pass
