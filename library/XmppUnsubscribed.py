#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
from google.appengine.ext import db
from library.XmppCore import XmppHandler
from models.Users import Users
from models.UsersSettings import UsersSettings

"""
Klasa obsługująca usunięcie kontaktu na poziomie XMPP.
Implementuje:
- usnięcie użytkownika z Roster'a (kolekcja Users)
- usnięcie ustawień użytkownika
@todo - wysłanie wiadomość do pozostałych użytkowników o usuniętej subskrybcji

"""
class UnsubscribedHandler(XmppHandler):
	def post(self):
		logging.info("Unsibscribe confirmed (unubscribed) from: %s", self.jid)

		if self.data.has_key('user') and isinstance(self.data['user'], Users):
			settings = UsersSettings.all()
			settings.filter('user =', user)
			items = settings.fetch(limit=1000,keys_only=True)
			if len(items):
				db.delete(items)

			self.data['user'].delete()
			del self.data['user']


