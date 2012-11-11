#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.api import xmpp
from google.appengine.api import memcache
from library.XmppCore import XmppHandler

"""
Klasa obsługująca zdarzenie online użytkownika na poziomie XMPP.
Aktualizuje informacje w kolekcji Users.

"""
class AvailableHandler(XmppHandler):
	def post(self):
		# Jeżeli user był do tej pory offline, aktualizujemy info w bazie
		if None != self.data['user'].lastOnline:
			self.data['user'].lastOnline = None
			self.data['user'].put()

		status = memcache.get('xmppStatus')
		if None != status:
			xmpp.send_presence(self.data['user'].jid, status, presence_show=xmpp.PRESENCE_TYPE_AVAILABLE)
