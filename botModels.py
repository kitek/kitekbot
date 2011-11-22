#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.api import memcache
import random
import settings

# Utilities models

class Acl():
	GUEST = 0x0
	MEMBER = 0x10
	OPERATOR = 0x20
	ADMIN = 0x30
	
	@staticmethod
	def get_roles():
		return [Acl.GUEST,Acl.MEMBER,Acl.OPERATOR,Acl.ADMIN]
	

class Version():
	_versionMajor = '1.0'
	@staticmethod
	def getMajorVersion():
		return Version._versionMajor

# DB models

class Menu(db.Model):
	data = db.DateProperty(required=True)
	name = db.StringProperty(required=True)

class RescueQuestion(db.Model):
	jid = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	message = db.TextProperty(required=True)
	
class RescueAnswers(db.Model):
	rescueId = db.IntegerProperty(required=True)
	jid = db.StringProperty(required=True)
	syncCmd = db.BooleanProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class InfoMessages(db.Model):
	jid = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	message = db.TextProperty(required=True)
	
class Sync(db.Model):
	jid = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	files = db.TextProperty(required=True)
	done = db.BooleanProperty(required=False,default=False)

class SyncAnswers(db.Model):
	syncId = db.IntegerProperty(required=True)
	jid = db.StringProperty(required=True)
	syncCmd = db.BooleanProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)

class Roster(db.Model):
	"""key name = user id"""
	jid = db.StringProperty(required=True)
	password = db.StringProperty(required=False)
	created = db.DateTimeProperty(auto_now_add=True)
	acl = db.IntegerProperty(required=False, choices=set(Acl.get_roles()), default=Acl.MEMBER)
	
	# @todo Ustawienia trzeba przeniesc do innej tabelki
	syncCmd = db.BooleanProperty(default=True)
	infoCmd = db.BooleanProperty(default=True)

	@staticmethod
	def check_jid(jid):
		r = Roster.findByJid(jid)
		if r <> None:
			return True
		else:
			xmpp.send_presence(jid,'',settings.BOT_JID,xmpp.PRESENCE_TYPE_UNAVAILABLE,xmpp.PRESENCE_SHOW_NONE)
			return False

	@staticmethod
	def findByJid(jid):
		q = Roster.all()
		q.filter("jid =", jid)
		item = q.fetch(1)
		if len(item) == 0:
			return None
		else:
			return item[0]
			
	@staticmethod
	def deleteByJid(jid):
		item = Roster.findByJid(jid)
		if item != None:
			db.delete(item.key())
		return True

class Presence(db.Model):
	AVAILABLE = 1
	UNAVAILABLE = 2
	userRef = db.ReferenceProperty(Roster)
	created = db.DateTimeProperty(auto_now_add=True)
	type = db.IntegerProperty(required=True, choices=set([1,2]))

class LogsLogin(db.Model):
	userRef = db.ReferenceProperty(Roster,required=True)
	created = db.DateTimeProperty(auto_now_add=True)

"""
- autor
- title
- body
- datetime
- language [ txt, php, js, as, other ]

"""
class Solution(db.Model):
	languages = {1:'other',2:'php',3:'js',4:'as'}
	
	title = db.StringProperty(required=True)
	body = db.TextProperty(required=True)
	author = db.ReferenceProperty(Roster,required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	language = db.IntegerProperty(required=True, choices=set([1,2,3,4]))
			
# Liczniki

class GeneralCounterShardConfig(db.Model):
	"""Tracks the number of shards for each named counter."""
	name = db.StringProperty(required=True)
	num_shards = db.IntegerProperty(required=True, default=20)


class GeneralCounterShard(db.Model):
	"""Shards for each named counter"""
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(required=True, default=0)
	
	@staticmethod	
	def get_count(name):
		"""Retrieve the value for a given sharded counter.

		Parameters:
		  name - The name of the counter
		"""
		total = memcache.get(name)
		if total is None:
			total = 0
			for counter in GeneralCounterShard.all().filter('name = ', name):
				total += counter.count
			memcache.add(name, str(total), 60)
		return total

	@staticmethod
	def increment(name):
		"""Increment the value for a given sharded counter.

		Parameters:
		name - The name of the counter
		"""
		config = GeneralCounterShardConfig.get_or_insert(name, name=name)
		def txn():
			index = random.randint(0, config.num_shards - 1)
			shard_name = name + str(index)
			counter = GeneralCounterShard.get_by_key_name(shard_name)
			if counter is None:
				counter = GeneralCounterShard(key_name=shard_name, name=name)
			counter.count += 1
			counter.put()
		db.run_in_transaction(txn)
		memcache.incr(name, initial_value=0)

	@staticmethod
	def increase_shards(name, num):
		"""Increase the number of shards for a given sharded counter.
		Will never decrease the number of shards.

		Parameters:
			name - The name of the counter
			num - How many shards to use
			
		"""
		config = GeneralCounterShardConfig.get_or_insert(name, name=name)
		def txn():
			if config.num_shards < num:
				config.num_shards = num
				config.put()
		db.run_in_transaction(txn)