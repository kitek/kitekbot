#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from library.DbProperty import CetDateTimeProperty

class RoomSubscriptions(db.Model):
	LIMIT = 1000

	name = db.StringProperty(required=True)
	jid = db.StringProperty(required=True)
	created = CetDateTimeProperty(auto_now_add=True)

	def put(self, deadline=60):
		""" Aktualizacja kesza z danymi użytkownika. """
		memcache.delete(RoomSubscriptions.getCacheName(self.name))
		super(RoomSubscriptions, self).put()

	def delete(self):
		""" Aktualizacja kesza z danymi użytkownika. """
		memcache.delete(RoomSubscriptions.getCacheName(self.name))
		super(RoomSubscriptions, self).delete()		

	@staticmethod
	def getByName(name):
		cacheName = RoomSubscriptions.getCacheName(name)
		subs = memcache.get(cacheName)
		if None == subs:
			roomSubs = RoomSubscriptions.all().filter('name =',name).fetch(limit=RoomSubscriptions.LIMIT)
			subs = []
			for item in roomSubs:
				subs.append(item.jid)
			if len(subs) > 0:
				memcache.set(cacheName, subs)
		return subs

	@staticmethod
	def getCacheName(name):
		""" Buduje nazwe kesza dla podanej nazwy pokoju."""
		return 'RoomSubscriptions_%s' % (name)
