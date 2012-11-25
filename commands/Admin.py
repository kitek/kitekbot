# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import logging
import re
from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import capabilities
from google.appengine.api import app_identity
from models.Users import Users
from models.UsersInvited import UsersInvited
from models.ApiAccess import ApiAccess
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

""" Komendy dostępne dla administratora lub owner'a. """

class QuotaCommand(Command):
	aclRole = 'admin'
	description = u"Informacje o statusie wykorzystywanych przez Bot'a usług."
	help = u"Informacje statusie wykorzystywanych usług. Więcej info: https://developers.google.com/appengine/docs/quotas"

	""" 
	dokumentacja twierdzi ze mamy tylko jedna metode - is_enabled() :
		- https://developers.google.com/appengine/docs/python/capabilities/capabilitysetclass
	ale wiekszy listing metod jest w zrodle (trunk): 
		- http://code.google.com/p/googleappengine/source/browse/trunk/python/google/appengine/api/capabilities/__init__.py 
	"""

	def run(self, user, params):
		response = u"Status usług:\n";
		services = {'Datastore reads':'datastore_v3','XMPP':'xmpp','Memcache': 'memcache','URL Fetch':'urlfetch'}
		
		response+=u"* Datastore writes: "
		if capabilities.CapabilitySet("datastore_v3", ["write"]).is_enabled():
			response+=u"OK"
		else:
			response+=u"ERROR: " + capabilities.CapabilitySet(services[item]).admin_message() + "\n"
		response+="\n"

		for item in services:
			response+=u"* "+item+": "
			if capabilities.CapabilitySet(services[item]).is_enabled():
				if capabilities.CapabilitySet(services[item]).will_remain_enabled_for(86400):
					response+=u"OK"
				else:
					response+=u"OK, ale planowany downtime w ciągu doby"
			else:
				response+=u"ERROR: " + capabilities.CapabilitySet(services[item]).admin_message()
			response+="\n"
		response+="\nhttp://code.google.com/status/appengine\n"
		Message.reply(response)

class SetStatusCommand(Command):
	aclRole = 'admin'
	description = u"Ustawia XMPP status dla bot'a."
	help = u"Ustawia XMPP status dla bot'a."
	def run(self, user, params):
		if len(params) == 0:
			Message.reply(u"Podaj status.")
			return
		status = u" ".join(params).strip()
		memcache.set('xmppStatus', status)
		Message.reply(u"Status został zaaktualizowany.")
		# Rozeslij do wszystkich online swoj status
		usersAll = Users.getAll()
		for item in usersAll:
			if item.lastOnline == None:
				xmpp.send_presence(item.jid, status, presence_show=xmpp.PRESENCE_TYPE_AVAILABLE)

class InviteUserCommand(Command):
	aclRole = 'owner'
	description = u"Zaprasza nowego użytkownika do systemu."
	help = u"Wymaga podania adresu email nowego użytkownika. Uruchomiona bez parametrów zwraca oczekujące zaproszenia."
	def run(self, user, params):
		if 0 == len(params):
			invited = UsersInvited.all().order('-__key__').fetch(limit=1000)
			if 0 == len(invited):
				response = u"Brak oczekujących zaproszeń."
			else:
				response = u"Oczekujące zaproszenia:\n"
				for item in invited:
					response+= u"* '%s'\n" % (item.jid)
			Message.reply(response)
			return

		jid = params[0].lower().strip()
		isValid = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',jid)
		if None == isValid:
			Message.reply(u"Błędny adres email. Proszę spróbować raz jeszcze.")
			return
		currentUser = Users.getByJid(jid)
		if currentUser is not None:
			Message.reply(u"Podany użytkownik już istnieje. Proszę podać innego.")
			return
		UsersInvited(key_name=jid,invitedBy=user.jid).put()
		Message.reply(u"Użytkownik '%s' został zaproszony." % (jid))

		# Wyślij zaproszenie na XMPP
		xmpp.send_invite(jid)

		botJid = app_identity.get_application_id()+'@appspot.com' # @todo custom domain? move to settings
		botMail = u""

		# Wyslij emaila do usera z info by dodal sobie kontakt
		msg = u"""
Otrzymałeś możliwość korzystania z BOT'a: %s. Zaakceptuj go na swoim komunikatorze.
Zaproszenie wysłane przez %s.
""" % (botJid, user.jid)
		#mail.send_mail(botMail, jid, u"Zaproszenie do %s" % (botJid), msg) 
		# @todo Jak ogarnąć botMail'a (ustawienia w samej appki - jak to przechowywac?)



class ApiCommand(Command):
	"""
	Zarejestrowane aplikacje przechowywane są w kolekcji: ApiAccess.

	"""
	aclRole = 'owner'
	description = u"Umożliwia zarządzanie dostępem do Bot'a przez API HTTP."
	help = u"Uruchomiona bez parametrów wyświetla zarejestrowane klucze dostępu. Umożliwia wygenerowanie nowego klucza przez wywołanie: '/api add nazwaAplikacji'."
	limit = 1000
	def run(self, user, params):
		# Check if provided correct params
		if len(params) == 2 and params[0] in ['add', 'del']:
			# Add or delete
			appName = params[1].lower().strip()
			app = ApiAccess.all(keys_only=True).filter('appName =',appName).fetch(1)
			if 'add' == params[0]:
				if len(app):
					Message.reply(u"Dostęp o nazwie '%s' już istnieje podaj inny." % (appName))
				else:
					apiKey = os.urandom(16).encode('hex')
					ApiAccess(key_name=apiKey,appName=appName,authorJid=user.jid).put()
					Message.reply(u"Klucz API dla '%s' to: '%s'. Więcej informacji na: https://github.com/kitek/kitekbot" % (appName, apiKey))
			elif 'del' == params[0]:
				# Remove key
				if len(app):
					db.delete(app[0])
					Message.reply(u"Dostęp o nazwie '%s' został usunięty." % (appName))
				else:
					Message.reply(u"Brak dostępu o nazwie '%s'. Podaj inny." % (appName))
			return
		# Listujemy wszystkie dostępy wraz z dodatkowymi informacjami	
		apiList = ApiAccess.all().fetch(self.limit)
		response = u"Klucze do API:\n"
		if len(apiList):
			for item in apiList:
				response+=u"* %s - %s \n" % (item.appName, item.key().name())
		else:
			response+= u"brak."
		Message.reply(response)



# Register commands

CommandDispatcher.register('quota', QuotaCommand)
CommandDispatcher.register('setstatus', SetStatusCommand)
CommandDispatcher.register('inviteuser', InviteUserCommand)
CommandDispatcher.register('api', ApiCommand)
