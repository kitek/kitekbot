# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import webapp2
from google.appengine.api import xmpp
from models.UsersInvited import UsersInvited
from models.Users import Users

"""
Klasa bazowa dla kontrolerow obsługujących żądania XMPP.
Implementuje:
- sprawdzanie uprawnień (osoby spoza rostera)
- dispatch'owanie odpowiednich komend (@todo)
- dodatkowe medoty dla klas dzieci

"""
class XmppHandler(webapp2.RequestHandler):
	jid = ''
	jidName = ''
	handlerName = ''
	data = {'user':False,'body':''}

	def dispatch(self):
		self.jid = self.request.get('from').split('/')[0]
		self.jidName = self.jid.split('@')[0]
		self.handlerName = type(self).__name__.replace('Handler','').lower()
		if not self.jid:
			return
		# Sprawdzam uprawnienia
		# Jezeli jest to subskrybcja to sprawdz czy jid jest: na liscie zaproszen, w rosterze
		if self.handlerName in ['subscribed','subscribe']:
			invitedUser = UsersInvited.get_by_key_name(self.jid)
			if None == invitedUser and False == self.isInRoster():
				logging.info('Uninvited user %s' % (self.jid))
				self.sendUnavailable()
				self.abort(403)
				return
			self.data['invitedUser'] = invitedUser
		else:
			self.data['user'] = self.isInRoster()
			if False == self.data['user']:
				logging.info('Access forbidden for %s' % (self.jid))
				self.sendUnavailable()
				self.abort(403)
				return
		# Wyrożniamy trzy typy wiadomosci (command, message, roomMessage)
		if 'message' == self.handlerName and self.request.get('body'):
			self.data['body'] = self.request.get('body').strip()

		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
		finally:
			pass

	# Sprawdza czy podany jid znajduje się już w Rosterze
	def isInRoster(self, jid=None):
		if None == jid:
			jid = self.jid
		user = Users.getByJid(jid)
		if None == user:
			return False
		return user

	# Wysyła XMPP status nieobecny
	def sendUnavailable(self, jid=None):
		if None == jid:
			jid = self.jid
		xmpp.send_presence(self.jid,None,None,xmpp.PRESENCE_TYPE_UNAVAILABLE,xmpp.PRESENCE_SHOW_NONE)

	# Prosta implementacja wysylki XMPP wiadomosci do podanego jid
	def sendMessage(self, message, jid=None):
		if None == jid:
			jid = self.jid
		xmpp.send_message(jid,message)

		
