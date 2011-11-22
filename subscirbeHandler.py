#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from botModels import Roster
import logging


class SubscirbeHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		logging.info('Subscribe from %s ' % (jid))

class SubscirbedHandler(webapp.RequestHandler):
	allowedUsers = frozenset(['marcin.kitowicz@gmail.com'])

	def post(self):
		jid = self.request.get('from').split('/')[0]
		logging.info("Subskrypcja od: %s", jid)
		allowedUser = False
		for item in self.allowedUsers:
			if(item == jid):
				allowedUser = True
				break
		if(allowedUser == True or jid.find('@firma.fotka.pl') > 0):
			logging.info("Sprawdzam czy uzytkownik istnieje w Rosterze")
			if(Roster.findByJid(jid) == None):
				roster = Roster(jid=jid)
				roster.put()
				logging.info("Dodalem uzytkownika")
				xmpp.send_message(jid,roster._welcomeMessage)
			else:
				logging.info("Uzytkownik juz istnieje")
		else:
			logging.info("Uzytkownik nie dozwolony")
			xmpp.send_presence(jid,'',Roster.botJid,xmpp.PRESENCE_TYPE_UNAVAILABLE,xmpp.PRESENCE_SHOW_NONE)