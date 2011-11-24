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

class NamedModel(db.Model):
    """A Model subclass for entities which automatically generate their own key
    names on creation. See documentation for _generate_key function for
    requirements."""

    def __init__(self, *args, **kwargs):
        kwargs['key_name'] = _generate_key(self, kwargs)
        super(NamedModel, self).__init__(*args, **kwargs)
def _generate_key(entity, kwargs):
	"""Generates a key name for the given entity, which was constructed with
	the given keyword args.  The entity must have a KEY_NAME property, which
	can either be a string or a callable.

	If KEY_NAME is a string, the keyword args are interpolated into it.  If
	it's a callable, it is called, with the keyword args passed to it as a
	single dict."""

	# Make sure the class has its KEY_NAME property set
	if not hasattr(entity, 'KEY_NAME'):
		raise RuntimeError, '%s entity missing KEY_NAME property' % (
			entity.entity_type())

	# Make a copy of the kwargs dict, so any modifications down the line don't
	# hurt anything
	kwargs = dict(kwargs)

	# The KEY_NAME must either be a callable or a string.  If it's a callable,
	# we call it with the given keyword args.
	if callable(entity.KEY_NAME):
		return entity.KEY_NAME(kwargs)

	# If it's a string, we just interpolate the keyword args into the string,
	# ensuring that this results in a different string.
	elif isinstance(entity.KEY_NAME, basestring):
		# Try to create the key name, catching any key errors arising from the
		# string interpolation
		try:
			key_name = entity.KEY_NAME % kwargs
		except KeyError:
			raise RuntimeError, 'Missing keys required by %s entity\'s KEY_NAME '\
				'property (got %r)' % (entity.entity_type(), kwargs)

		# Make sure the generated key name is actually different from the
		# template
		if key_name == entity.KEY_NAME:
			raise RuntimeError, 'Key name generated for %s entity is same as '\
				'KEY_NAME template' % entity.entity_type()

		return key_name

	# Otherwise, the KEY_NAME is invalid
	else:
		raise TypeError, 'KEY_NAME of %s must be a string or callable' % (
			entity.entity_type())



# Struktura przechowująca informacje o osobach online
class PresenceStatus(NamedModel):
	KEY_NAME = '%(name)s'
	AVAILABLE = True
	UNAVAILABLE = False
	name = db.StringProperty()
	online = db.BooleanProperty(default=True,indexed=True)
	last = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def count_online():
		p = PresenceStatus.all(keys_only=True)
		p.filter("online =",True)
		return p.count()

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