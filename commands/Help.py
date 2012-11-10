# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher
from library.Message import Message
from library.Acl import Acl

class HelpCommand(Command):
	""" 
	Lista dostępnych komend [3]:
	* /online - wyświetla trele morele
	* /rooms - trele morele
	* /
	"""
	description = u"Informacje o dostępnych komendach bot'a. "
	help = u"Wyświetla informacje o dostępnych komendach systemu. " \
			u"Jeżeli podano parametr z nazwą komendy wyświetlona zostanie szczegółowa pomoc np.: " \
			u"'/help online'. W przypadku gdy podana nazwa komendy nie istnieje zostanie wyświetlona lista wszystkich poleceń."

	def run(self, user, params):
		if len(params) == 1 and CommandDispatcher.commandNames.has_key(params[0]):
			response = u"Komenda '/%s':\n%s" % (params[0],CommandDispatcher.commandNames[params[0]].help)
			response+= u"\nDostęp do komendy posiada: '%s'." % (CommandDispatcher.commandNames[params[0]].aclRole)
			Message.reply(response)
			return

		response = u"Lista dostępnych komend [%s]:\n"
		counter = 0
		for item in CommandDispatcher.commandNames:
			# Sprawdzamy czy posiadamy uprawnienia, jezeli tak to umieszczamy komende na liscie
			if Acl.isAllowed(user, CommandDispatcher.commandNames[item].aclRole):
				response+= u"* '/%s' - %s\n" % (item, CommandDispatcher.commandNames[item].description)
				counter+=1
		response = response % (counter)
		response+= u"Zawsze możesz dowiedzieć się więcej na temat komendy wpisując '/help nazwa komendy'."
		Message.reply(response)

CommandDispatcher.register('help', HelpCommand)
