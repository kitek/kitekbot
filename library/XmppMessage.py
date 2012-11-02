# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.XmppCore import XmppHandler
from library.XmppCommand import CommandDispatcher

class MessageHandler(XmppHandler):
	def post(self):
		logging.info('message: "%s" from %s' % (self.data['body'], self.jid))

		# Jeżeli wiadomość to polecenie (zaczyna się od / lub \) to staramy się znaleźć i dispatch'ować
		# odpowiednią klasę przekazując do niej dane użytkownika + parametry
		if self.data['body'][0] in ['\\','/']:
			cmdString = self.data['body'][1:]
			cmdName = cmdString.split(' ')[0]
			cmdParams = cmdString.split(' ')[1:]

			CommandDispatcher.dispatch(cmdName, self.data['user'], cmdParams)

			#logging.info('Command %s' % (cmdName))
			#logging.info('Params %s' % (cmdParams))

		#logging.info(self.request.get('body')[0])