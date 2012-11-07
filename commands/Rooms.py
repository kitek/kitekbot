# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher
from models.Rooms import Rooms
from models.RoomSubscriptions import RoomSubscriptions

class RoomsCommand(Command):
	""" /rooms [nazwaPokoju]- wyświetla listę wszystkich dostępnych pokoi lub informacje o wybranym """
	LIMIT = 1000
	def run(self, user, params):
		if len(params) == 0:
			# Wyswietl wszystkie dostępne pokoje
			rooms = Rooms.all().order("-count").fetch(limit=self.LIMIT)
			if len(rooms) == 0:
				response = u"Brak dostępnych pokoi. Możesz utworzyć nowy pokój wpisując: '/join nazwaPokoju'."
			else:
				mySubs = {}
				myRoomSubscriptions = RoomSubscriptions.all().filter("jid =",user.jid).fetch(limit=self.LIMIT)
				if len(myRoomSubscriptions):
					for item in myRoomSubscriptions:
						mySubs[item.name] = item.name
				response = u"Dostępne pokoje:\n"
				for room in rooms:
					if mySubs.has_key(room.name):
						room.count-=1
					ext = u""
					if room.count > 0:
						ext = u"osoba"
						if room.count > 1 and room.count < 5:
							ext = u"osoby"
						if room.count > 4:
							ext = u"osób"
						response+="* "+room.name+" ("+("Ja + " if mySubs.has_key(room.name) else "")+str(room.count)+" "+ext+")\n"
					else:
						response+="* "+room.name+" (tylko Ja)\n"
			Message.reply(response)
		else:
			# Wyswietl o podanej nazwie
			roomName = params[0]
			roomSubscriptions = RoomSubscriptions.all().filter("name =",roomName).fetch(limit=self.LIMIT)
			if len(roomSubscriptions) == 0:
				Message.reply(u"Brak informacji o pokoju '%s'. Możesz go utworzyć wpisując '/join %s'." % (roomName,roomName))
				return False
			response = u"Osoby w pokoju '%s':\n" % (roomName)
			for item in roomSubscriptions:
				if user.jid == item.jid:
					response+="* Ja\n"
				else:
					response+="* "+item.jid+"\n"
			Message.reply(response)
		return True

class JoinCommand(Command):
	""" /join nazwaPokoju - subskrybuje podany pokój (tworzy w przypadku gdy ten nie istnieje) """
	def run(self, user, params):
		roomName = ''
		if len(params) > 0:
			roomName = params[0]
		isValidName = Rooms.isValidName(roomName)
		if True != isValidName:
			Message.reply(isValidName)
			return False

		mySubName = '%s/%s' % (roomName, user.jid)
		myRoomSubscriptions = RoomSubscriptions.get_by_key_name(mySubName)
		if None != myRoomSubscriptions:
			Message.reply(u"Posiadasz już subskrypcję w tym pokoju. Zawsze możesz opuścić pokój wpisując /leave %s" % (roomName))
			return False
		room = Rooms.get_by_key_name(roomName)
		if None == room:
			Rooms(key_name=roomName, name=roomName, authorJid=user.jid).put()
		else:
			room.count = room.count + 1
			room.put()
			# Wysylamy wiadomosc do innych osob w danym pokoju
			Message.broadcast(u"[%s] %s dołączył do pokoju." % (user.jid, roomName), roomName)
		RoomSubscriptions(key_name=mySubName, name=roomName, jid=user.jid).put()

		response = u"Od tej pory będziesz otrzymywał rozmowy z pokoju '%s', aby wysłać wiadomość do osób w tym pokoju wpisz: '#%s treść wiadomości'. " % (roomName,roomName)
		response+= u"Zawsze możesz opuścić pokój wpisując '/leave %s'. Do wyświetlenia osób w pokoju użyj '/rooms %s'" % (roomName,roomName)
		Message.reply(response)



CommandDispatcher.register('rooms', RoomsCommand)
CommandDispatcher.register('join', JoinCommand)



