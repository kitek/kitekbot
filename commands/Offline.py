# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from models.Users import Users
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class OfflineCommand(Command):
	description = u"Lista użytkowników offline."
	help = u"Wyświetla listę z użytkownikami offline. Komenda nie posiada parametrów. Zobacz również '/online'."
	def run(self, user, params):
		# Zapytanie o użytkowników online
		response = u"Osoby offline [%s z %s]:\n"
		offlineCount = 0
		allUsers = Users.getAll(user.jid)
		for item in allUsers:
			if None != item.lastOnline:
				response+=u"* "+re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',item.jid)+" ("+item.lastOnline.strftime('%Y-%m-%d %H:%M:%S')+")\n"
				offlineCount+=1
		response = response % (offlineCount,len(allUsers))
		if 0 == offlineCount:
			response+=u"brak osób"
		Message.reply(response)

CommandDispatcher.register('offline', OfflineCommand)
