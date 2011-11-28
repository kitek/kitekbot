#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Globalne ustawienia aplikacji.
Nadpisanie ustawien odbywa się poprzez stworzenie pliku settings_local.py i redeklarację zmiennej
"""
import os

# MessageHandler
ROOMS_LIMIT = 10
ROOMS_MIN_LEN = 2
ROOMS_USERS_MAX = 100
ROOMS_NAME_PATT = "a-zA-Z0-9\_\-"

MESSAGE_MIN_LEN = 2

SETTINGS_PER_USER = 100

SYNC_LIMIT_MIN = 5
BROADCAST_USERS_LIMIT = 100

COMMANDS_DESC = dict({
		'help':'Wyświetla informacje o dostępnych komendach systemu',
		'help nazwaPolecenia':'Wyświetla szczegółową pomoć dla podanego polecenia',
		'sync plik1...plikN':'Wysyła informacje o plikach do synchronizacji',
		'sync on|off':'Włącza/Wyłącza otrzymywanie informacji o synchronizowanych plikach',
		'info TwojaWiadomość':'Wysyła dowolną wiadomość do osób, które chcą otrzymywać tego rodzaju komunikaty',
		'info on|off':'Włącza/Wyłącza otrzymywanie informacji od użytkowników systemu',
		'online':'Wyświetla  wszystkich użytkowników wraz ich statusami',
		'join nazwaPokoju':'Tworzy i subskrybuje podany pokój',
		'leave nazwaPokoju':'Opuszcza wybrany pokój',
		'rooms':'Wyświetla listę wszystkich dostępnych pokoi',
		'rooms nazwaPokoju':'Wyświetla informacje o wybranym pokoju',
		'invite user nazwaPokoju':'Zaprasza użytkownika do wybranego pokoju',
		'switch nazwaPokoju':'Umożliwia przełączanie się pomiędzy pokojami'		
	})
COMMANDS_HELP = dict({
		'sync':'Lorem ipsum for sync',
		'info':'Lorem ipsum for info'
	})

# SubscirbeHandler
ALLOWED_USERS = frozenset([])
ALLOWED_DOMAIN = ''

# BotModels
WEBGUI_URL = ''
BOT_JID = ''
WELCOME_MESSAGE = 'Welcome'



# Nadpisz ustawienia
if os.path.exists('./settings_local.py'):
	from settings_local import *
