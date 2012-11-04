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
	- currentRoom

"""
class Users(db.Model):
	created = CetDateTimeProperty(auto_now_add=True)
	lastOnline = CetDateTimeProperty()
	aclRole = db.StringProperty(choices=('owner', 'admin', 'user'),default='user')
	currentRoom = db.StringProperty(default='global')

	@property
	def jid(self):
		""" Wirtualna własność obiektu budowana na podstawie nazwy klucza. """
		return self.key().name()

	def put(self, deadline=60):
		""" Aktualizacja kesza z danymi użytkownika. """
		memcache.delete_multi([Users.getCacheName(self.jid),Users.getCacheNameAll()])
		super(Users, self).put()

	def delete(self):
		""" Aktualizacja kesza z danymi użytkownika. """
		memcache.delete_multi([Users.getCacheName(self.jid),Users.getCacheNameAll()])
		super(Users, self).delete()		

	# Zwraca użytkownika jeżeli taki istnieje w kolekcji (dane są keszowane).
	# Metoda wykorzystywana przy sprawdzaniu uprawnień w dispatch'u.
	@staticmethod
	def getByJid(jid):
		cacheName = Users.getCacheName(jid)
		user = memcache.get(cacheName)
		if user is None:
			user = Users.get_by_key_name(jid)
			memcache.set(cacheName, user)
		return user

	@staticmethod
	def getCacheName(jid):
		""" Buduje nazwe kesza dla podanego jid'a (jednego użytkownika). """
		return 'Users_%s' % (jid)

	@staticmethod
	def getCacheNameAll():
		""" Zwraca nazwe kesza dla kontenera przechowującego wszystkich użytkowników. """
		return 'Users'

	@staticmethod
	def getAll(exceptJid=None):
		cacheName = Users.getCacheNameAll()
		allUsers = memcache.get(cacheName)
		if allUsers is None:
			allUsers = Users.all().fetch(limit=1000)
			memcache.set(cacheName, allUsers)
		if exceptJid is not None:
			# Filtrujemy uzytkownika o podanym jid
			for item in allUsers:
				if item.jid == exceptJid:
					allUsers.remove(item)
					break
		return allUsers








		
