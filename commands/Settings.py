# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from models.UsersSettings import UsersSettings
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class SettingsCommand(Command):
	description = u"Wyświetla lub zmienia ustawienia użytkownika."
	help = u"Przykład użycia: '/set globalChat enabled'."

	def run(self, user, params):
		# Gdy nie podano parametru zwróc aktualne ustawienia (wraz z domyślnymi)
		if len(params) == 0:
			response = u"Twoje obecne ustawienia:\n"
			settings = UsersSettings.get(user.jid)
			if len(settings) > 0:
				for item in settings:
					response+= u"* '"+item+"': "+settings[item]+"\n"
			else:
				response+= u"Brak ustawień\n"
			response+= u"\nOpis ustawień:\n"
			for item in UsersSettings.DEFAULTS_HELP:
				response+= u"'"+item+" ["+u"|".join(UsersSettings.DEFAULTS_VALUES[item])+"]' - "+UsersSettings.DEFAULTS_HELP[item]+"\n"
			Message.reply(response)
			return
		# Sprawdzamy poprawnosc parametrow
		if len(params) != 2:
			Message.reply(u"Błędna konstrukcja komendy. Podaj nazwę ustawienia, a następnie jego wartość np.: '/set globalChat enabled'.")
			return
		name = params[0].strip()
		value = params[1].strip()
		if False == UsersSettings.DEFAULTS.has_key(name):
			Message.reply(u"Brak klucza o nazwie '%s'. Wpisz '/set' by Wyświetlić dostępne ustawienia." % (name))
			return
		if value not in UsersSettings.DEFAULTS_VALUES[name]:
			Message.reply(u"Wartość '%s' jest błędna. Możliwe elementy to: %s." % (value, u"|".join(UsersSettings.DEFAULTS_VALUES[name])))
			return
		UsersSettings.set(user.jid, name, value)
		Message.reply("Ustawiono '%s':%s" % (name, value))

CommandDispatcher.register(['set','ustaw'], SettingsCommand)
