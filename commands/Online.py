# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
- ładowanie wszystkich plików modułu tylko w przypadku dispatch'owania polecenia
	przy zwykłych wiadomościach nie ma sensu tego odpalać

- definicja ciała komendy
	- dostęp do modelu użytkownika
	- dostęp do parametrów polecenia
- uprawnienia użytkownika do wykonania polecenia (default=user)
- krótki opis komendy
- pomoc komendy (ewentualnie przykład)
- możliwość zarejestrowania komendy w systemie (ewentualne aliasy)


import BaseCommand

class Online(object):
	det costam(self):
		wynik = 2 * 2


/online 5
/sleep 10


BaseCommand.registerCommand('online',callback)

"""

import logging
from library.XmppCommand import CommandDispatcher

class Online:
	def run(self, user, params):
		logging.info('executing Online.run()')

CommandDispatcher.register('online', Online)