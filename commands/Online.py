# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from models.Users import Users
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class OnlineCommand(Command):
	description = u"Lista użytkowników online."
	help = u"Wyświetla listę z użytkownikami online. Komenda nie posiada parametrów. Zobacz również '/offline'."
	def run(self, user, params):
		# Zapytanie o użytkowników online
		response = u"Osoby online [%s/%s]:\n"
		onlineCount = 0
		allUsers = Users.getAll(user.jid)
		for item in allUsers:
			if None == item.lastOnline:
				response+=re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',item.jid)+'\n'
				onlineCount+=1
		response = response % (onlineCount,len(allUsers))
		if 0 == onlineCount:
			response+=u"brak osób"
		Message.reply(response)

CommandDispatcher.register('online', OnlineCommand)
