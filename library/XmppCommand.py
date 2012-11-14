# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from library.Acl import Acl
from library.Message import Message

class Command(object):
	"""
	Abstrakcyjna klasa bazowa dla obsługiwanych przez bot'a komend.
	Każda komenda musi implementować metodę 'run(self, user, params)'. 
	Przy uruchomieniu danej komendy metoda run otrzymje dwa parametry: 
	* user (dict) - obiekt użytkownika który uruchomił komendę
	* params (list) - parametry komendy

	Dodatkowo istnieje możliwość podania:
	* aclRole (string: user, admin, owner) - nazwa wymaganej roli do uruchomienia komendy
	* description (string) - krótki opis komendy
	* help (string) - pomoc, przykłady wywołania lub dokładny opis parametrów
	"""
	# Określa poziom dostępu do wykonania usługi.
	aclRole = 'user'
	# Dodatkowy krótki opis komendy.
	description = ''
	# Dodatkowa pomoc komendy.
	help = ''
	def run(self, user, params):
		""" Implementuje logikę komendy """
		raise NotImplementedError("Should have implemented this")


class CommandDispatcher(object):
	# Słownik z dostępnymi komendami i klasami implementującymi ich obsługę
	commandNames = {}
	commandAliases = {}

	# @todo Obsługa aliasów
	@staticmethod
	def register(commandName, commandClass):
		""" Rejestruje nową komendę. """
		aliases = None
		if 'list' == type(commandName).__name__:
			aliases = commandName[1:]
			commandName = commandName[0].lower().strip()
		else:
			commandName = commandName.lower().strip()

		if False == isinstance(commandClass(), Command):
			logging.error('Passed commandClass is not instance of Command class.' % (commandName))
			return
		if CommandDispatcher.commandNames.has_key(commandName):
			logging.error('Passed commandName "%s" is already in use.' % (commandName))
			return
		if commandClass.aclRole not in Acl.getRoles():
			logging.error('Passed aclRole "%s" for "%s" command is incorrect.' % (commandClass.aclRole, commandName))
			return
		
		CommandDispatcher.commandNames[commandName] = commandClass
		
		# Dodanie aliasow
		if None != aliases and len(aliases):
			for item in aliases:
				# Sprawdz czy podany alias juz nie istnieje lub czy nie ma komendy o takiej nazwie
				if False == CommandDispatcher.commandNames.has_key(item) and False == CommandDispatcher.commandAliases.has_key(item):
					CommandDispatcher.commandAliases[item] = commandName


	@staticmethod
	def dispatch(commandName, user, params):
		""" Importuje wszystkie komendy, a następnie uruchamia żądaną przez użytkownika. """
		# Importuj dostępne komendy
		import commands

		# Trim + zamień na małe literki
		commandName = commandName.lower().strip()

		# Rejestruje nadawcę wiadomości w klasie Message (wymagane dla metody reply())
		Message.user = user

		# Sprawdzamy czy istnieje alias o podanej nazwie
		if CommandDispatcher.commandAliases.has_key(commandName):
			commandName = CommandDispatcher.commandAliases[commandName]

		# Sprawdzam czy komenda zostala zarejestrowana
		if CommandDispatcher.commandNames.has_key(commandName):

			if False == Acl.isAllowed(user, CommandDispatcher.commandNames[commandName].aclRole):
				logging.error('Permission denied to run "%s"(%s) by "%s"(%s)' % (commandName, CommandDispatcher.commandNames[commandName].aclRole, user.jid, user.aclRole))
				Message.reply(u"Nie posiadasz wystarczających uprawnień do wykonania tej komendy.\nWymagana rola to: '%s', natomiast Twoja to: '%s'." % (CommandDispatcher.commandNames[commandName].aclRole, user.aclRole))
				return

			# Dispatch
			command = CommandDispatcher.commandNames[commandName]()
			command.run(user, params)
		else:
			# Unhandled command
			# @todo Można pokusić się o podpowiadanie w stylu: "Czy chodziło Ci o..."
			Message.reply('Komenda "%s" nie istnieje.' % (commandName))

