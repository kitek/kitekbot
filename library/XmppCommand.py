# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging

class CommandDispatcher:
	commandNames = {}

	@staticmethod
	def register(commandName, commandClass):
		logging.info('Registered new command "%s"' % (commandName))
		CommandDispatcher.commandNames[commandName] = commandClass

	@staticmethod
	def dispatch(commandName, user, params):
		# Importuj dostępne komendy
		import commands

		if CommandDispatcher.commandNames.has_key(commandName):
			# Dispatch
			command = CommandDispatcher.commandNames[commandName]()
			command.run(user, params)
		else:
			# Unhandled command
			pass
