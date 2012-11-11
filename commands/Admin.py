# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from google.appengine.api import xmpp
from google.appengine.api import memcache
from google.appengine.api import capabilities
from models.Users import Users
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class QuotaCommand(Command):
	aclRole = 'admin'
	description = u"Informacje statusie wykorzystywanych usług."
	help = u"Informacje statusie wykorzystywanych usług. Więcej info: https://developers.google.com/appengine/docs/quotas"
	def run(self, user, params):
		response = u"Usługi:\n";
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
		status = params[0].strip()
		memcache.set('xmppStatus', status)
		Message.reply(u"Status został zaaktualizowany.")
		# Rozeslij do wszystkich online swoj status
		usersAll = Users.getAll()
		for item in usersAll:
			if item.lastOnline == None:
				xmpp.send_presence(item.jid, status, presence_show=xmpp.PRESENCE_TYPE_AVAILABLE)

CommandDispatcher.register('quota', QuotaCommand)
CommandDispatcher.register('setstatus', SetStatusCommand)

