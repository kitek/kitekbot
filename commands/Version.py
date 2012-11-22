# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import logging
from datetime import datetime
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class VersionCommand(Command):
	description = u"Aktualna kompilacja Bot'a."
	help = u"Wyświetla aktualną wersję kompilacji Bot'a."
	def run(self, user, params):
		# Zapytanie o użytkowników online
		version = os.environ["CURRENT_VERSION_ID"].split('.')
		timestamp = long(version[1]) / pow(2,28) 

		response = u"Wersja: %s\nData kompilacji: %s" % (version[0], datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"))
		response+= u"\n\nhttps://github.com/kitek/kitekbot\n"
		Message.reply(response)

CommandDispatcher.register('version', VersionCommand)
