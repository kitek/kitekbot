#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from library.DbProperty import CetDateTimeProperty

"""
Model Użytkownika (element roster'a).
Users:
	- key_name (jid)
	- created
	- lastOnline
	- aclRole

"""
class Users(db.Model):
	created = CetDateTimeProperty(auto_now_add=True)
	lastOnline = CetDateTimeProperty()
	aclRole = db.StringProperty(choices=('owner', 'admin', 'user'),default='user')

	@property
	def jid(self):
		return self.key().name()

	def put(self,deadline=60):
		memcache.delete(Users.getCacheName(self.jid))
		super(Users, self).put()

	def delete(self):
		memcache.delete(Users.getCacheName(self.jid))
		super(Users, self).delete()		

	# Zwraca użytkownika jeżeli taki istnieje w kolekcji (dane są keszowane).
	# Metoda wykorzystywana przy sprawdzaniu uprawnień w dispatch'u.
	@staticmethod
	def getByJid(jid):
		cacheName = Users.getCacheName(jid)
		user = memcache.get(cacheName)
		if user is None:
			user = Users.get_by_key_name(jid)
			memcache.set(cacheName,user)
		return user

	# Buduje nazwe kesza dla podanego jid'a.
	@staticmethod
	def getCacheName(jid):
		return 'Users_%s' % (jid)

		
