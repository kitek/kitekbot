# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from google.appengine.api import xmpp
from google.appengine.api import mail
from google.appengine.api import memcache
from google.appengine.api import capabilities
from google.appengine.api import app_identity
from models.Users import Users
from models.UsersInvited import UsersInvited
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

""" Komendy dostępne dla administratora lub owner'a. """

class QuotaCommand(Command):
	aclRole = 'admin'
	description = u"Informacje statusie wykorzystywanych usług."
	help = u"Informacje statusie wykorzystywanych usług. Więcej info: https://developers.google.com/appengine/docs/quotas"
	def run(self, user, params):
		response = u"Status usług:\n";
		services = {'Datastore reads':'datastore_v3','XMPP':'xmpp','Memcache': 'memcache','URL Fetch':'urlfetch'}
		
		response+=u"* Datastore writes:"
		if capabilities.CapabilitySet("datastore_v3", ["write"]).is_enabled():
			response+=u"OK"
		else:
			response+=u"ERROR"
		response+="\n"

		for item in services:
			response+=u"* "+item+": "
			if capabilities.CapabilitySet(services[item]).is_enabled():
				response+=u"OK"
			else:
				response+=u"ERROR"
			response+="\n"
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


# Register commands

CommandDispatcher.register('quota', QuotaCommand)
CommandDispatcher.register('setstatus', SetStatusCommand)
CommandDispatcher.register('inviteuser', InviteUserCommand)

