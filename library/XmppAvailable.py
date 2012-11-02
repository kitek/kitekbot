#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
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
