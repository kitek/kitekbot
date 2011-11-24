#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from botModels import Roster, PresenceStatus
import logging as console


class AvailableHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		console.info('STATUS: Available from %s ' % (jid))

		presence = PresenceStatus(name=jid)
		presence.put()
		
class UnavailableHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		console.info('STATUS: Unavailable from %s ' % (jid))

		presence = PresenceStatus(name=jid,online=False)
		presence.put()
		
class ProbeHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		else:
			xmpp.send_presence(jid, status='Online')