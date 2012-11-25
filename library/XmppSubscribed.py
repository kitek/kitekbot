#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
from library.XmppCore import XmppHandler
from library.Message import Message
from models.Users import Users
from models.UsersInvited import UsersInvited
from models.UsersSettings import UsersSettings

"""
Klasa obsługująca zaproszenia na poziomie XMPP.
Implementuje:
- Dodanie użytkownika do Roster'a (kolekcja Users)
- Usuniecie z listy zaproszeń (kolekcja UsersInvited)
- Wysłanie wiadomości powitalnej do nowego użytkownika
"""
class SubscribedHandler(XmppHandler):
	WELCOME_MESSAGE = u"Witaj %s.\nOd tej pory będziesz otrzymywał wiadomości od BOT'a.\nLista obsługiwanych komend dostępna jest po wpisaniu: '/help'."

	def post(self):
		logging.info("Subscribe confirmed (subscribed) from: %s", self.jid)

		# Tworzymy nowego usera w kolekcji
		newUser = Users(key_name=self.jid, lastOnline=None)
		newUser.put()

		# Domyślne ustawienia konta
		UsersSettings.setupDefaults(self.jid)

		if self.data.has_key('invitedUser') and isinstance(self.data['invitedUser'], UsersInvited):
			self.data['invitedUser'].delete()
			del self.data['invitedUser']
			# Broadcast do wszystkich
			Message.broadcastSystem(u"Nowy użytkownik: %s" % (self.jid), roomName='global', exceptJid=self.jid)

		Message.user = newUser
		Message.reply(self.WELCOME_MESSAGE%(self.jidName))
