# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.XmppCore import XmppHandler
from library.XmppCommand import CommandDispatcher
from library.Message import Message

class MessageHandler(XmppHandler):
	def post(self):
		# Rejestruje nadawcę wiadomości w klasie Message (wymagane dla metody reply())
		Message.user = self.data['user']

		if self.data['body'][0] in ['\\','/']:
			# Uruchomienie komendy
			cmdString = self.data['body'][1:]
			cmdName = cmdString.split(' ')[0]
			cmdParams = cmdString.split(' ')[1:]
			CommandDispatcher.dispatch(cmdName, self.data['user'], cmdParams)
		elif '##' == self.data['body'][0:2]:
			# Wyślij wiadomość na czat główny gdy podano ##
			body = self.data['body'][2:].strip()
			Message.broadcast(body, u"global")
		elif '#' == self.data['body'][0]:
			# Wiadomość do konkretnego pokoju
			roomName = self.data['body'].split(' ')[0].replace('#','')
			Message.broadcast(self.data['body'], roomName)
		else:
			# Wiadomość globalna lub w pokoju w którym aktualnie znajduje się user
			Message.broadcast(self.data['body'], self.data['user'].currentRoom)
