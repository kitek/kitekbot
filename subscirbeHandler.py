#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from botModels import Roster
import logging
import settings


class SubscirbeHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		logging.info('Subscribe from %s ' % (jid))

class SubscirbedHandler(webapp.RequestHandler):

	def post(self):
		jid = self.request.get('from').split('/')[0]
		logging.info("Subskrypcja od: %s", jid)
		allowedUser = False
		for item in settings.ALLOWED_USERS:
			if(item == jid):
				allowedUser = True
				break
		if(allowedUser == True or jid.find('@'+settings.ALLOWED_DOMAIN) > 0):
			if(Roster.findByJid(jid) == None):
				roster = Roster(jid=jid)
				roster.put()
				xmpp.send_message(jid,settings.WELCOME_MESSAGE)
		else:
			logging.warn("Uzytkownik niedozwolony: %s", jid)
			xmpp.send_presence(jid,'',settings.BOT_JID,xmpp.PRESENCE_TYPE_UNAVAILABLE,xmpp.PRESENCE_SHOW_NONE)
