# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from models.Users import Users
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class OnlineCommand(Command):
	description = 'Wyświetla listę z użytkownikami online.'
	help = 'Wyświetla listę z użytkownikami online.'
	def run(self, user, params):
		# Zapytanie o użytkowników online
		response = 'Osoby online [%s/%s]:\n'
		onlineCount = 0
		allUsers = Users.getAll(user.jid)
		for item in allUsers:
			if None == item.lastOnline:
				response+=re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',item.jid)+'\n'
				onlineCount+=1
		response = response % (onlineCount,len(allUsers))
		if 0 == onlineCount:
			response+='brak osób'
		Message.reply(response)

CommandDispatcher.register('online', OnlineCommand)
