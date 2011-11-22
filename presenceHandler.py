#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from botModels import Roster, Presence
import logging


class AvailableHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		logging.info('STATUS: Available from %s ' % (jid))

		# Szukaj usera
		user = Roster.findByJid(jid)
		
		# Sprawdz czy ostatnie presence jest takei samo
		p = Presence.all()
		p.filter('userRef =',user)
		p.order('-__key__')
		p = p.fetch(1)
		if len(p) == 1 and p[0].type == Presence.AVAILABLE:
			logging.info('Presence: Available - to samo w bazie nie dodaje rekordu.')
			return True
		
		# Dodaj nowe presence
		presence = Presence(userRef=user,type=Presence.AVAILABLE)
		presence.put()
		
class UnavailableHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		logging.info('STATUS: Unavailable from %s ' % (jid))
		
		user = Roster.findByJid(jid)
		p = Presence.all()
		p.filter('userRef =',user)
		p.order('-__key__')
		p = p.fetch(1)
		if len(p) == 1 and p[0].type == Presence.UNAVAILABLE:
			logging.info('Presence: Unavailable - to samo w bazie nie dodaje rekordu.')
			return True
		
		presence = Presence(userRef=user,type=Presence.UNAVAILABLE)
		presence.put()
		
class ProbeHandler(webapp.RequestHandler):
	def post(self):
		jid = self.request.get('from').split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		else:
			xmpp.send_presence(jid, status='Online')