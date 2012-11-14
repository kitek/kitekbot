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
			u"'/help online'. W przypadku gdy podana komenda nie istnieje zostanie wyświetlona lista wszystkich poleceń."

	def run(self, user, params):
		if len(params) == 1:
			aliases = []
			commandName = params[0].lower().strip()
			# Sprawdz czy nie jest to alias
			if CommandDispatcher.commandAliases.has_key(commandName):
				commandName = CommandDispatcher.commandAliases[commandName]
				aliases.append(u"'%s'" % commandName)

			if CommandDispatcher.commandNames.has_key(commandName):
				response = u"Komenda '/%s':\n%s" % (commandName,CommandDispatcher.commandNames[commandName].help)
				
				# Szukamy aliasow
				for item in CommandDispatcher.commandAliases:
					if CommandDispatcher.commandAliases[item] == commandName and item != params[0].lower().strip():
						aliases.append(u"'%s'" % item)
				if len(aliases):
					response+= u"\nInne aliasy: %s." % (u", ".join(aliases))
				
				response+= u"\nDostęp do komendy posiada: '%s'." % (CommandDispatcher.commandNames[commandName].aclRole)
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

CommandDispatcher.register(['help','pomoc'], HelpCommand)
