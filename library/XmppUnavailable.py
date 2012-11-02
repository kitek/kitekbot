#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import datetime
from library.XmppCore import XmppHandler

"""
Klasa obsługująca zdarzenie offline użytkownika na poziomie XMPP.
Aktualizuje informacje w kolekcji Users.

"""
class UnavailableHandler(XmppHandler):
	def post(self):
		if None == self.data['user'].lastOnline:
			self.data['user'].lastOnline = datetime.datetime.now()
			self.data['user'].put()
