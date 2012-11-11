#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from google.appengine.api import memcache
from models.Users import Users


class UsersSettings(db.Model):
	DEFAULTS = {'globalChat':'enabled','offlineChat':'enabled'}
	DEFAULTS_HELP = {'globalChat':u"Otrzymywanie wiadomości z czatu globalnego.",\
					'offlineChat':u"Otrzymywanie wiadomości gdy jesteśmy offline."}
	DEFAULTS_VALUES = {'globalChat':['enabled','disabled'],'offlineChat':['enabled','disabled']}

	jid = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	value = db.StringProperty()

	@staticmethod
	def getDefaults():
		return UsersSettings.DEFAULTS

	@staticmethod
	def setupDefaults(jid):
		for item in UsersSettings.getDefaults():
			UsersSettings.set(jid, item, UsersSettings.DEFAULTS[item])

	@staticmethod
	def set(jid,name,value=''):
		keyName = '%s/%s' % (jid, name)
		UsersSettings(key_name=keyName,jid=jid,name=name,value=str(value)).put()
		memcache.delete(UsersSettings.getCacheName(jid))

	@staticmethod
	def get(jids,name=None):
		if 'list' == type(jids).__name__:
			# Pobieramy ustawienia od wielu użytkowników
			settings = memcache.get_multi(jids,key_prefix=UsersSettings.getCacheName(''))
			for item in jids:
				if False == settings.has_key(item) or 0 == len(settings[item]):
					# Dopełniamy listę brakującymi danymi
					settings[item] = UsersSettings.getFromDbAndCache(item)
			if None != name:
				# Filtrujemy wyniki do okreslonej nazwy ustawienia
				results = {}
				for item in settings:
					if settings[item].has_key(name):
						results[item] = settings[item][name]
					else:
						results[item] = None
				return results
			else:
				return settings
		else:
			# Pobieramy ustawienia tylko od jednego użytkownika
			settings = memcache.get(UsersSettings.getCacheName(jids))
			if settings is None:
				settings = UsersSettings.getFromDbAndCache(jids)
			if None != name:
				if settings.has_key(name):
					return settings[name]
				else:
					return None
			return settings

	@staticmethod
	def getFromDbAndCache(jid):
		settings = UsersSettings.all()
		settings.filter('jid =', jid)
		settings = settings.fetch(limit=1000)
		# Nie chcemy przechowywac calego obiektu, tylko wartosci klucz:wartosc
		items = {}
		for item in settings:
			items[item.name] = item.value
		memcache.set(UsersSettings.getCacheName(jid), items)
		return items

	@staticmethod
	def getCacheName(jid):
		""" Buduje nazwe kesza dla podanego jid'a (jednego użytkownika). """
		return 'Settings_%s' % (jid)
