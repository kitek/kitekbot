#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
from library.XmppCore import XmppHandler
from models.Users import Users
from models.UsersInvited import UsersInvited

"""
Klasa obsługująca zaproszenia na poziomie XMPP.
Implementuje:
- Dodanie użytkownika do Roster'a (kolekcja Users)
- Usuniecie z listy zaproszeń (kolekcja UsersInvited)
- Wysłanie wiadomości powitalnej do nowego użytkownika
@todo - Wysłanie wiadomości do pozostałych osób o dołączeniu

"""
class SubscribedHandler(XmppHandler):
	WELCOME_MESSAGE = 'Witaj %s.' # @todo Przygotować lepszy komunikat

	def post(self):
		logging.info("Subscribe confirmed (subscribed) from: %s", self.jid)

		newUser = Users(key_name=self.jid,lastOnline=datetime.datetime.now())
		newUser.put()

		if self.data.has_key('invitedUser') and isinstance(self.data['invitedUser'], UsersInvited):
			self.data['invitedUser'].delete()
			del self.data['invitedUser']

		self.sendMessage(self.WELCOME_MESSAGE%(self.jidName))
