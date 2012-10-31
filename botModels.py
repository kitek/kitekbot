#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.api import memcache
import random, settings, re
import logging as console


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

class Rooms(NamedModel):
	KEY_NAME = '%(name)s'
	name = db.StringProperty(required=True)
	count = db.IntegerProperty(default=1,required=False)
	author = db.StringProperty(required=True)
	password = db.StringProperty(required=False)
	last = db.DateTimeProperty(auto_now_add=True)

	@staticmethod
	def invite(jid,to,roomName):
		valid = Rooms(name='Rooms',author=jid)._checkRoomName(roomName)
		if valid != True:
			xmpp.send_message(jid,valid)
			return False
		if len(to) == 0:
			xmpp.send_message(jid,u"Podaj poprawną nazwę użytkownika")
			return False
		sub = RoomSubscriptions.all(keys_only=True)
		sub.filter("name =",roomName)
		sub.filter("jid =",jid)
		sub = sub.fetch(1)
		if len(sub) == 0:
			xmpp.send_message(jid,u"Nie możesz zaprosić '%s' do pokoju '%s' ponieważ nie posiadasz aktywnej subskrypcji. Wpisz /join %s by dołączyć do pokoju." % (to, roomName, roomName))
			return False
		if re.match('([\w\.-]+)@([\w\.-]+)',to) == None:
			to+=u"@"+settings.ALLOWED_DOMAIN
		if Roster.check_jid(to) == False:
			xmpp.send_message(jid,u"Brak użytkownika: %s" % (to))
			return False
		sub = RoomSubscriptions.all(keys_only=True)
		sub.filter("name =",roomName)
		sub.filter("jid =",to)
		sub = sub.fetch(1)
		if len(sub) == 1:
			xmpp.send_message(jid,u"Użytkownik '%s' posiada już subskrypcję pokoju '%s'." % (to,roomName))
			return False
		room = Rooms(name=roomName,author=jid).get_by_key_name(roomName)
		if room <> None:
			count = room.count
			author = room.author
			room = Rooms(name=roomName,author=author,count=room.count+1)
			room.put()
			
			sub = RoomSubscriptions.all()
			sub.filter("name =",roomName)
			sub = sub.fetch(settings.ROOMS_USERS_MAX)
			if len(sub) > 0:
				t = []
				for user in sub:
					if user.jid != jid: t.append(user.jid)
				if len(t): xmpp.send_message(t,u"[%s] %s został zaproszony do pokoju przez %s." % (roomName, to.replace("@"+settings.ALLOWED_DOMAIN,''), jid.replace("@"+settings.ALLOWED_DOMAIN,'')))
			sub = RoomSubscriptions(name=roomName,jid=to)
			sub.put()

			xmpp.send_message(jid,u"Użytkownik '%s' został zaproszony do pokoju '%s'." % (to,roomName))
			xmpp.send_message(to,u"Zostałeś zaproszony do pokoju '%s' przez '%s'." % (roomName,jid))

	@staticmethod
	def show(jid,roomName):
		name = re.sub('[^'+settings.ROOMS_NAME_PATT+']+','',roomName)
		if len(name) and roomName == name:
			sub = RoomSubscriptions.all()
			sub.filter("name =",roomName)
			sub = sub.fetch(settings.ROOMS_USERS_MAX)
			if len(sub) == 0:
				xmpp.send_message(jid,u"Brak informacji o pokoju '%s'. Możesz go utworzyć wpisując /join %s" % (roomName,roomName))
				return False
			info = u"Osoby w pokoju '%s':\n" % (roomName)
			for user in sub:
				if user.jid == jid:
					info+="Ja\n"
				else:
					info+=user.jid.replace("@"+settings.ALLOWED_DOMAIN,'')+"\n"
			xmpp.send_message(jid,info)
			return True
		rooms = Rooms(name='Rooms',author=jid).all()
		rooms.order("-count")
		rooms = rooms.fetch(settings.ROOMS_LIMIT)
		if len(rooms) == 0:
			xmpp.send_message(jid,u"Brak dostępnych pokoi. Możesz utworzyć pokój wpisując /join nazwaPokoju")
			return False
		# Wyciagnij moje subskrypcje
		sub = RoomSubscriptions.all()
		sub.filter("jid =",jid)
		sub = sub.fetch(settings.ROOMS_USERS_MAX)
		mySub = dict();
		if len(sub):
			for item in sub:
				mySub[item.name] = 1
		info = u"Dostępne pokoje:\n"
		for room in rooms:
			if mySub.has_key(room.name):
				room.count-=1
			ext = u""
			if room.count > 0:
				ext = u"osoba"
				if room.count > 1 and room.count < 5:
					ext = u"osoby"
				if room.count > 4:
					ext = u"osób"
				info+=room.name+" ("+("Ja + " if mySub.has_key(room.name) else "")+str(room.count)+" "+ext+")\n"
			else:
				info+=room.name+" (tylko Ja)\n"
		xmpp.send_message(jid,info+u"Możesz dołączyć do dowolnego pokoju wpisując /join nazwaPokoju")
		return True

	@staticmethod
	def join(jid,roomName):
		valid = Rooms(name='Rooms',author=jid)._checkRoomName(roomName)
		if valid != True:
			xmpp.send_message(jid,valid)
			return False
		sub = RoomSubscriptions.all(keys_only=True)
		sub.filter("jid =",jid)
		sub.filter("name =",roomName)
		sub = sub.fetch(1)
		if len(sub):
			xmpp.send_message(jid,u"Posiadasz już subskrypcję w tym pokoju. Zawsze możesz opuścić pokój wpisując /leave %s" % (roomName))
			return False
		room = Rooms(name=roomName,author=jid).get_by_key_name(roomName)
		if room <> None:
			count = room.count
			author = room.author
			room = Rooms(name=roomName,author=author,count=room.count+1)
			room.put()

			sub = RoomSubscriptions.all()
			sub.filter("name =",roomName)
			sub = sub.fetch(settings.ROOMS_USERS_MAX)
			if len(sub) > 0:
				to = []
				for user in sub:
					if user.jid != jid: to.append(user.jid)
				if len(to): xmpp.send_message(to,u"[%s] %s dołączył do pokoju." % (roomName, jid.replace("@"+settings.ALLOWED_DOMAIN,'')))
		else:
			room = Rooms(author=jid,name=roomName)
			room.put()
		sub = RoomSubscriptions(name=roomName,jid=jid)
		sub.put()
		xmpp.send_message(jid,u"Od tej pory będziesz otrzymywał wiadomości z pokoju '%s'. Zawsze możesz opuścić pokój wpisując /leave %s Aby wyświetlić wszystkie osoby w pokoju wpisz /rooms %s" % (roomName,roomName,roomName))
		return True

	@staticmethod
	def leave(jid,roomName):
		valid = Rooms(name='Rooms',author=jid)._checkRoomName(roomName)
		if valid != True:
			xmpp.send_message(jid,valid)
			return False
		sub = RoomSubscriptions.all(keys_only=True)
		sub.filter("jid =",jid)
		sub.filter("name =",roomName)
		sub = sub.fetch(1)
		if len(sub) == 0:
			xmpp.send_message(jid,u"Od tej pory nie będziesz otrzymywał wiadomości z pokoju '%s'. Zawsze możesz powrócić do pokoju wpisując /join %s" % (roomName,roomName))
			return False
		sub = RoomSubscriptions(name=roomName,jid=jid)
		sub.delete()

		sub = RoomSubscriptions.all()
		sub.filter("name =",roomName)
		sub = sub.fetch(settings.ROOMS_USERS_MAX)
		
		room = Rooms(name=roomName,author=jid)
		if len(sub) == 0:
			room.delete()
		else:
			room.count = len(sub)
			room.put()
			to = []
			for user in sub:
				if user.jid != jid: to.append(user.jid)
			if len(to): xmpp.send_message(to,u"[%s] %s opuścił pokój." % (roomName, jid.replace("@"+settings.ALLOWED_DOMAIN,'')))
		xmpp.send_message(jid,u"Od tej pory nie będziesz otrzymywał wiadomości z pokoju '%s'. Zawsze możesz powrócić do pokoju wpisując /join %s" % (roomName,roomName))
		return True

	@staticmethod
	def switch(jid,roomName):
		valid = Rooms(name='Rooms',author=jid)._checkRoomName(roomName)
		if valid != True:
			xmpp.send_message(jid,valid)
			return False
		if roomName != "global":
			sub = RoomSubscriptions.all(keys_only=True)
			sub.filter("jid =",jid)
			sub.filter("name =",roomName)
			sub = sub.fetch(1)
			if len(sub) == 0:
				xmpp.send_message(jid,u"Nie możesz przepiąć się do pokoju '%s' ponieważ nie posiadasz aktywnej subskrypcji. Wpisz /join %s by dołączyć do pokoju." % (roomName, roomName))
				return False
		DbSettings.set(jid,"currentRoom",roomName)
		xmpp.send_message(jid,u"Od tej chwili będziesz pisał w pokoju '%s'. Aby przełączyć się do innego pokoju wpisz /switch global" % (roomName))
		return True

	@staticmethod
	def send(jid,message):
		roomName = re.search("^#(["+settings.ROOMS_NAME_PATT+"]+)",message)
		roomName = roomName.group(1)
		if len(roomName) < settings.ROOMS_MIN_LEN:
			return False
		info = message.replace("#"+roomName,"").strip()
		if len(info) < settings.MESSAGE_MIN_LEN:
			xmpp.send_message(jid,u"Wpisz dłuższą wiadomość (minimum to %s znaki)." % settings.MESSAGE_MIN_LEN)
			return False
		sub = RoomSubscriptions.all()
		sub.filter("name =",roomName)
		sub = sub.fetch(settings.ROOMS_USERS_MAX)
		if len(sub) == 0:
			xmpp.send_message(jid,u"Brak pokoju o nazwie: '%s'. Listę dostępnych pokoi uzyskasz wpisując /rooms" % (roomName))
			return False
		to = []
		have_sub = False
		for user in sub:
			if user.jid == jid:
				have_sub = True
			else:
				to.append(user.jid)
		if have_sub == False:
			xmpp.send_message(jid,u"Nie możesz pisać w tym pokoju ponieważ nie posiadasz aktywnej subskrypcji. Wpisz /join %s by dołączyć do pokoju." % (roomName))
			return False
		if len(to):
			xmpp.send_message(jid,u"Wiadomość została wysłana do pokoju '%s'." % (roomName))
			xmpp.send_message(to,u"[%s] %s: %s" % (roomName, re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',jid),info))
		else:
			xmpp.send_message(jid,u"Brak osób w pokoju o nazwie: '%s'. Listę dostępnych pokoi uzyskasz wpisując /rooms" % (roomName))
		return True

	@staticmethod
	def _checkRoomName(name):
		roomName = re.sub('[^'+settings.ROOMS_NAME_PATT+']+','',name)
		if roomName <> name:
			return u"Nazwa pokoju '%s' może składać się tylko ze zbioru znaków: [%s]+\n" % (name,settings.ROOMS_NAME_PATT)
		if len(roomName) < settings.ROOMS_MIN_LEN:
			return u"Nazwa pokoju musi posiadać minimum %s znaki." % (settings.ROOMS_MIN_LEN)
		return True

class RoomSubscriptions(NamedModel):
	KEY_NAME = '%(name)s-%(jid)s'
	name = db.StringProperty(required=True)
	jid = db.StringProperty(required=True)

class DbSettings(NamedModel):
	KEY_NAME = '%(jid)s-%(name)s'
	MEM_NAME = u"settings_%s"
	jid = db.StringProperty(required=True)
	name = db.StringProperty(required=True)
	value = db.StringProperty()

	@staticmethod
	def get(jid,name):
		data = memcache.get(DbSettings.MEM_NAME % (jid))
		if data == None:
			s = DbSettings.all()
			s.filter("jid =",jid)
			s = s.fetch(settings.SETTINGS_PER_USER)
			data = dict()
			for item in s:
				data[item.name] = item.value
			memcache.add(DbSettings.MEM_NAME % (jid), data)
		if data.has_key(name):
			return data[name]
		else:
			return None
	
	@staticmethod
	def set(jid,name,value):
		s = DbSettings(jid=jid,name=name,value=value)
		s.put()
		memcache.delete(DbSettings.MEM_NAME % (jid))
	
	@staticmethod
	def remove(jid,name):
		s = DbSettings(jid=jid,name=name)
		s.delete()
		memcache.delete(DbSettings.MEM_NAME % (jid))

class InfoMessages(db.Model):
	jid = db.StringProperty(required=True)
	created = db.DateTimeProperty(auto_now_add=True)
	message = db.TextProperty(required=True)
	room = db.StringProperty(required=True,default='global')
	
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
		data = memcache.get(jid)
		if data is not None:
			return data
		else:
			q = Roster.all()
			q.filter("jid =", jid)
			item = q.fetch(1)
			if len(item) == 0:
				return None
			else:
				memcache.add(jid, item[0])
				return item[0]
			
	@staticmethod
	def deleteByJid(jid):
		item = Roster.findByJid(jid)
		if item != None:
			memcache.delete(jid)
			db.delete(item.key())
		return True

class LogsLogin(db.Model):
	userRef = db.ReferenceProperty(Roster,required=True)
	created = db.DateTimeProperty(auto_now_add=True)

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