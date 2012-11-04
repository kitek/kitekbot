# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher
from library.Message import Message

class Help(Command):
	def run(self, user, params):
		Message.reply('Oto pomoc')

CommandDispatcher.register('help', Help)
