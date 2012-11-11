# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from google.appengine.api import xmpp
from models.UsersSettings import UsersSettings
from models.Users import Users
from models.Chats import Chats
from models.RoomSubscriptions import RoomSubscriptions

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
		jidsTo = []
		jidsOffline = []
		settings = None

		# Jeżeli wysylamy wiadomosc do danego pokoju musimy sprawdzic kto go subskrybuje
		if 'global' != roomName:
			if '#' == body[0]:
				body = body[len(roomName)+1:].strip()
			jidsTo = RoomSubscriptions.getByName(roomName)
			if len(jidsTo) == 0:
				Message.reply(u"Twoja wiadomość nie może zostać dostarczona. Brak osób, które subskrybują ten pokój.")
				return 	False
			if Message.user.jid not in jidsTo:
				# Sprawdz czy subskrybujesz dany pokoj
				Message.reply(u"Nie możesz pisać wiadomości w pokoju '%s' ponieważ nie posiadasz aktywnej subskrypcji. Wpisz '/join %s' by dołączyć do pokoju." % (roomName, roomName))
				return False
			# Unsetnij mnie i zobacz czy ktos został
			for item in reversed(jidsTo):
				if item == Message.user.jid:
					jidsTo.remove(item)
			if len(jidsTo) == 0:
				Message.reply(u"Twoja wiadomość nie może zostać dostarczona. Brak osób, które subskrybują ten pokój.")
				return False
			# Sprawdz kto jest offline
			allUsers = Users.getAll(Message.user.jid)
			for item in allUsers:
				if item.lastOnline != None and item.jid in jidsTo:
					jidsOffline.append(item.jid)
			del allUsers
		else:
			allUsers = Users.getAll(Message.user.jid)
			if 0 == len(allUsers):
				Message.reply(u"Twoja wiadomość nie może zostać dostarczona. Brak osób, które mogłyby na nią odpowiedzieć.")
				return False
			# Budujemy kolekcję odbiorców wiadomości
			for item in allUsers:
				jidsTo.append(item.jid)
				if item.lastOnline != None:
					jidsOffline.append(item.jid)
			del allUsers
			# Sprawdzamy kto nie chce otrzymywac wiadomosci z global'a - tych odrzucamy (globalChat = disabled)
			settings = UsersSettings.get(jidsTo)
			for item in settings:
				if settings[item].has_key('globalChat') and 'disabled' == settings[item]['globalChat']:
					jidsTo = filter(lambda name: name != item, jidsTo)
			if 0 == len(jidsTo):
				Message.reply(u"Twoja wiadomość nie może zostać dostarczona. Wszystkie dostępne osoby wyłączyły otrzymywanie wiadomości z czatu globalnego.")
				return False

		if len(jidsOffline) > 0:
			# sprawdzamy kto jest offline i czy ma wyłaczone otrzymywanie wiadomości gdy jesteś offline - tych odrzucamy (offlineChat = disabled)
			if None == settings:
				settings = UsersSettings.get(jidsOffline)
			for item in settings:
				if item in jidsOffline and settings[item].has_key('offlineChat') and 'disabled' == settings[item]['offlineChat']:
					jidsTo = filter(lambda name: name != item, jidsTo)
		if 0 == len(jidsTo):
			Message.reply(u"Twoja wiadomość nie może zostać dostarczona. Brak osób, które mogłyby na nią odpowiedzieć.")
			return False
		return Message.send(jidsTo, body, roomName)

	@staticmethod
	def broadcastSystem(body, roomName, exceptJid = None):
		""" Wysyła wiadomość do wszystkich użytkowników w danym pokoju jako wiadomość systemowa """
		jidsTo = RoomSubscriptions.getByName(roomName)
		jidsOffline = []

		if len(jidsTo) == 0:
			return False
		if None != exceptJid:
			if 'list' == type(exceptJid).__name__:
				for item in exceptJid:
					jidsTo = filter(lambda name: name != item, jidsTo)
			elif 'str' == type(exceptJid).__name__:
				jidsTo = filter(lambda name: name != exceptJid, jidsTo)
		if len(jidsTo) == 0:
			return False
		allUsers = Users.getAll()
		for item in allUsers:
			if item.jid in jidsTo and item.lastOnline != None:
				jidsOffline.append(item.jid)
		del allUsers
		if len(jidsOffline) > 0:
			# sprawdzamy kto jest offline i czy ma wyłaczone otrzymywanie wiadomości gdy jesteś offline - tych odrzucamy (offlineChat = disabled)
			settings = UsersSettings.get(jidsOffline)
			for item in settings:
				if settings[item].has_key('offlineChat') and 'disabled' == settings[item]['offlineChat']:
					jidsTo = filter(lambda name: name != item, jidsTo)
		if len(jidsTo) == 0:
			return False
		return Message.send(jidsTo, body, recordChat = False, sendJid = False)
		
	@staticmethod
	def reply(body):
		""" Wysyła odpowiedź zwrotną do użytkownika (jednego). """
		return Message.send(Message.user.jid, body, recordChat = False, sendJid = False)

	@staticmethod
	def send(jids, body, roomName = 'global', recordChat = True, sendJid = True):
		body = Message.format(body)
		if False == Message.isValid(body):
			Message.reply(u"Wpisz dłuższą wiadomość.")
			return False
		# Zapisz infomacje w bazie
		if True == recordChat:
			try:
				Chats(body=body,jid=Message.user.jid,message=body,roomName=roomName).put()
			except:
				logging.error(u'Error while inserting message: "%s"' % (body))
		# Wyślij wiadomości
		if sendJid:
			body = u"%s: %s" % (re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',Message.user.jid),body)
		SentResult = xmpp.send_message(jids, body)
		if SentResult != xmpp.NO_ERROR:
			logging.error(u'Error while sending message: "%s" from %s' % (body, Message.user.jid))
			return False
		if 'global' != roomName:
			Message.reply(u"Wiadomość została wysłana do pokoju '%s'." % (roomName))
		return True

	@staticmethod
	def format(body):
		return body.strip()

	@staticmethod
	def isValid(body):
		if 0 == len(body):
			return False
		return True

