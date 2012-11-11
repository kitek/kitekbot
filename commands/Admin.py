# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
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
		logging.info(response)

CommandDispatcher.register('quota', QuotaCommand)
