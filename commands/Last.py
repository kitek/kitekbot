# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher
from library.Message import Message
from models.Chats import Chats

class LastCommand(Command):
	LIMIT_MAX = 100
	description = u"Lista ostatnich rozmów."
	help = u"Dodatkowe parametry to: nazwa pokoju i limit rozmów np.: '/last pomoc 15'."
	def run(self, user, params):
		roomName = 'global'
		limit = 15

		if len(params) > 0:
			roomName = params[0].lower().strip()
		if len(params) > 1:
			try:
				limit = int(params[1])
			except ValueError:
				pass
		if limit > self.LIMIT_MAX:
			limit = self.LIMIT_MAX

		chats = Chats.all().filter('roomName =',roomName).order('-created').fetch(limit=limit)
		if len(chats) == 0:
			Message.reply(u"Brak ostatnich rozmów.")
		else:
			response = u"Historia wiadomości:\n"
			for item in chats:
				response+="[%s] %s: %s\n" % (item.created.strftime('%Y-%m-%d %H:%M:%S'), item.jid, item.message)
			Message.reply(response)

CommandDispatcher.register('last', LastCommand)
