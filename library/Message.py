# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from google.appengine.api import xmpp
from models.UsersSettings import UsersSettings
from models.Users import Users
from models.Chats import Chats

"""
Realizuje:
- wysyłka wiadomości do jednej osoby
	musi spradzac czy osoba jest online, jezeli jest offline powinna sprawdza ustawienia
- wysyłka wiadomości do wszystkich (na zasadach jw.)
- wysyłka wiadomości do konkretnego pokoju (na zasadach jw.)


"""

class Message(object):
	user = None

	@staticmethod
	def broadcast(body, roomName = 'global'):
		""" Wysyła wiadomość do wszystkich użytkowników w danym pokoju (currentRoom). """
		# @todo implementacja pokoi - pewnie ten kod bedzie wymagal refaktoryzacji
		jidsTo = {}

		if 'global' == roomName:
			allUsers = Users.getAll(Message.user.jid)
			if 0 == len(allUsers):
				Message.reply('Twoja wiadomość nie może zostać dostarczona. Brak osób, które mogłyby na nią odpowiedzieć.')
				return False
			# Budujemy kolekcję odbiorców wiadomości
			for item in allUsers:
				jidsTo[item.jid] = item.lastOnline
			# Sprawdzamy kto nie chce otrzymywac wiadomosci z global'a - tych odrzucamy (globalChat = disabled)
			settings = UsersSettings.get(jidsTo.keys())
			jidsToCopy = jidsTo.copy()
			for item in settings:
				if settings[item].has_key('globalChat') and 'disabled' == settings[item]['globalChat']:
					del jidsToCopy[item]
			jidsTo = jidsToCopy.copy()
			del jidsToCopy
			if 0 == len(jidsTo):
				Message.reply('Twoja wiadomość nie może zostać dostarczona. Wszystkie dostępne osoby wyłączyły otrzymywanie wiadomości z czatu globalnego.')
				return False
			# sprawdzamy kto jest offline i czy ma wyłaczone otrzymywanie wiadomości gdy jesteś offline - tych odrzucamy (offlineChat = disabled)
			jidsToCopy = jidsTo.copy()
			for item in jidsTo:
				if jidsTo[item] != None and settings[item].has_key('offlineChat') and 'disabled' == settings[item]['offlineChat']:
					del jidsToCopy[item]
			jidsTo = jidsToCopy.copy()
			del jidsToCopy
			if 0 == len(jidsTo):
				Message.reply('Twoja wiadomość nie może zostać dostarczona. Brak osób, które mogłyby na nią odpowiedzieć.')
				return False
			Message.send(jidsTo, body, roomName)

	@staticmethod
	def reply(body):
		""" Wysyła odpowiedź zwrotną do użytkownika (jednego). """
		return Message.send(Message.user.jid, body, recordChat = False)

	@staticmethod
	def send(jids, body, roomName = 'global', recordChat = True):
		body = Message.format(body)
		if False == Message.isValid(body):
			Message.reply('Wpisz dłuższą wiadomość.')
			return False
		# Wyślij wiadomości
		SentResult = xmpp.send_message(jids, u'%s: %s' % (re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',Message.user.jid),body))
		# Zapisz infomacje w bazie
		if True == recordChat:
			try:
				Chats(body=body,jid=Message.user.jid,message=body,roomName=roomName).put()
			except:
				logging.error('Error while inserting message: "%s"' % (body))
		if SentResult != xmpp.NO_ERROR:
			logging.error('Error while sending message: "%s" from %s' % (body, Message.user.jid))
			return False
		return True

	@staticmethod
	def format(body):
		return body.strip()

	@staticmethod
	def isValid(body):
		if 0 == len(body):
			return False
		return True

