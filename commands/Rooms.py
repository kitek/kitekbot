# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import re
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher
from models.Users import Users
from models.Rooms import Rooms
from models.Sequence import *
from models.RoomSubscriptions import RoomSubscriptions

class RoomsCommand(Command):
	""" /rooms [nazwaPokoju]- wyświetla listę wszystkich dostępnych pokoi lub informacje o wybranym """
	LIMIT = 1000
	description = u"Lista dostępnych pokoi utworzonych przez użytkowników."
	help = u"Wyświetla listę wszystkich dostępnych pokoi utworzonych przez użytkowników."
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
						if mySubs.has_key(room.name):
							ext = u"Ja + %s %s" % (room.count, ext)
						else:
							ext = "%s %s" % (room.count, ext)
						response+=u"* #%s (Id: %s) - %s\n" % (room.name, room.seqId, ext)
					else:
						response+=u"* #"+room.name+" (Id: %s) - tylko Ja\n" % (room.seqId)
			Message.reply(response)
		else:
			# Wyswietl o podanej nazwie
			roomName = params[0].lower().strip()
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
	description = u"Subskrybuje podany pokój. Jeżeli taki nie istnieje również go tworzy."
	help = u"Komenda wymaga parametru określającego nazwę pokoju np.: '/join graficy'. " \
			u"Nazwa pokoju może składac się tylko z liter, cyfr, podkreślników i myślników. " \
			u"Minimalna długość nazwy pokoju to 3 znaki. Pokój główny ma nazwę 'global' i wszyscy użytkownicy automatycznie " \
			u"go subskrybują. Zobacz również inne powiązane komendy: '/rooms', '/leave' lub '/invite'."
	
	def run(self, user, params):
		roomName = ''
		if len(params) > 0:
			roomName = params[0].lower().strip()
		isValidName = Rooms.isValidName(roomName)
		if True != isValidName:
			Message.reply(isValidName)
			return False

		mySubName = '%s/%s' % (roomName, user.jid)
		myRoomSubscriptions = RoomSubscriptions.get_by_key_name(mySubName)
		if None != myRoomSubscriptions:
			Message.reply(u"Posiadasz już subskrypcję w tym pokoju. Zawsze możesz opuścić pokój wpisując '/leave %s'." % (roomName))
			return False
		room = Rooms.get_by_key_name(roomName)
		if None == room:
			# Pobierz kolejny numer z sekwencji i wpisz do kolekcji
			seqName = 'rooms'
			currentSeq = None
			try:
				currentSeq = get_numbers(seqName, 1)[0]
			except Exception, e:
				# Utworz nowa sekwencje jezeli jej nie ma
				init_sequence(seqName, start=1, end=0xffffffff)
				currentSeq = get_numbers(seqName, 1)[0]

			Rooms(key_name=roomName, name=roomName, authorJid=user.jid, seqId=currentSeq).put()
		else:
			room.count = room.count + 1
			room.put()
			# Wysylamy wiadomosc do innych osob w danym pokoju
			Message.broadcastSystem(u"%s dołączył do pokoju." % (user.jid), roomName, user.jid)
		RoomSubscriptions(key_name=mySubName, name=roomName, jid=user.jid).put()

		# Wiadomość dla usera
		response = u"Od tej pory będziesz otrzymywał rozmowy z pokoju '%s', aby wysłać wiadomość do osób w tym pokoju wpisz: '#%s treść wiadomości'.\n" % (roomName,roomName)
		response+= u"Zawsze możesz opuścić pokój wpisując '/leave %s'.\nDo wyświetlenia osób w pokoju użyj '/rooms %s'." % (roomName,roomName)
		Message.reply(response)

class SwitchCommand(Command):
	description = u"Zmienia pokój w którym domyślnie piszemy."
	help = u"Wymaga parametru określającego nazwę pokoju. Umożliwia przełączanie się pomiędzy pokojami. " \
			u"Jeżeli komenda zostanie uruchomiona bez parametru wyświetlona zostanie nazwa pokoju w którym aktualnie piszemy."

	def run(self, user, params):
		roomName = 'global'
		if len(params) == 0:
			Message.reply(u"Aktualnie piszesz w pokoju: '%s'." % (user.currentRoom))
		else:	
			roomName = params[0].lower().strip()
			if roomName != user.currentRoom:
				# Sprawdz czy posiadasz subskrybcje w tym pokoju
				if 'global' != roomName:
					subs = RoomSubscriptions.getByName(roomName)
					if len(subs) == 0:
						Message.reply(u"Brak pokoju o nazwie: '%s'. Listę dostępnych pokoi uzyskasz wpisując '/rooms'." % (roomName))
						return False
					if user.jid not in subs:
						Message.reply(u"Nie możesz pisać w tym pokoju ponieważ nie posiadasz aktywnej subskrypcji. Wpisz '/join %s' by dołączyć do pokoju." % (roomName))
						return False
				# Aktualizacja w bazie
				user.currentRoom = roomName
				user.put()
			Message.reply(u"Od tej chwili będziesz pisał w pokoju '%s'. Aby przełączyć się do innego pokoju wpisz '/switch nazwaPokoju'." % (roomName))
		return True

class LeaveCommand(Command):
	description = u"Usuwa subskrypcję z danego pokoju."
	help = "Umożliwia opuszczenie danego pokoju i zaprzestanie przysyłania z niego wiadomości."
	def run(self, user, params):
		if len(params) == 0:
			Message.reply(u"Podaj nazwę pokoju wpisując np.: '/leave pomoc'.")
			return False
		roomName = params[0].lower().strip()
		isValidName = Rooms.isValidName(roomName)
		if True != isValidName:
			Message.reply(isValidName)
			return False
		# Sprawdzamy czy posiadamy suba
		subs = RoomSubscriptions.getByName(roomName)
		if len(subs) == 0:
			Message.reply(u"Brak pokoju o nazwie: '%s'. Listę dostępnych pokoi uzyskasz wpisując '/rooms'." % (roomName))
			return False
		if user.jid in subs:
			mySubName = '%s/%s' % (roomName, user.jid)
			myRoomSubscriptions = RoomSubscriptions.get_by_key_name(mySubName)
			if myRoomSubscriptions != None:
				myRoomSubscriptions.delete()

				# Aktualizacja licznikow
				room = Rooms.get_by_key_name(roomName)
				if None != room:
					if room.count <= 1:
						# Została ostatnia osoba usuwamy pokoj
						room.delete()
						pass
					else:
						# Ktos jescze został, zaaktualizuj liczniki
						room.count = room.count - 1
						room.put()

			if user.currentRoom == roomName:
				# aktualizacja currentRoom w przypadku gdy ustawiony był na opuszczany pokoj
				user.currentRoom = 'global'
				user.put()
			Message.reply(u"Od tej pory nie będziesz otrzymywał wiadomości z pokoju '%s'. Zawsze możesz powrócić do pokoju wpisując '/join %s'." % (roomName,roomName))
			Message.broadcastSystem(u"%s opuścił pokój." % (user.jid), roomName)
			return True
		Message.reply(u"Nie posiadasz subskrypcji pokoju '%s'." % (roomName))
		return False

class InviteCommand(Command):
	description = u"Zaprasza danego użytkownika do wybranego pokoju."
	help = u"Komenda wymaga dwóch parametrów: nazwy użytkownika i pokoju. Zapraszający musi sam posiadać subskrypcję w danym pokoju."
	def run(self, user, params):
		if len(params) != 2:
			Message.reply(u"Błędna konstrukcja komendy. Podaj nazwę użytkownika, a następnie nazwę pokoju do którego zapraszasz np.: '/intite piotr@domena.pl pomoc'.")
			return
		jid = params[0].strip()
		roomName = params[1].lower().strip()
		logging.info('invite %s to %s' % (jid, roomName))

		if user.jid == jid:
			Message.reply(u"Zaproś kogoś innego.")
			return
		# Sprawdzamy czy user istnieje
		invitedUser = Users.getByJid(jid)
		if None == invitedUser:
			Message.reply(u"Użytkownik %s nie istnieje. Podaj kogoś innego." % (jid))
			return
		isValidName = Rooms.isValidName(roomName)
		if True != isValidName:
			Message.reply(isValidName)
			return 
		# Sprawdzamy czy posiadam subskrybcję do podanego pokoju
		mySubName = '%s/%s' % (roomName, user.jid)
		myRoomSubscriptions = RoomSubscriptions.get_by_key_name(mySubName)
		if None == myRoomSubscriptions:
			Message.reply(u"Pokój '%s' nie istnieje lub nie posiadasz do niego subskrypcji." % (roomName))
			return
		# Sprawdzamy czy zapraszany posiada juz subskrybcje
		mySubName = '%s/%s' % (roomName, jid)
		myRoomSubscriptions = RoomSubscriptions.get_by_key_name(mySubName)
		if None != myRoomSubscriptions:
			Message.reply(u"%s posiada już subskrypcję pokoju '%s'." % (jid, roomName))
			return
		RoomSubscriptions(key_name=mySubName,name=roomName,jid=jid).put()
		Message.broadcastSystem(u"'%s' dołączył do pokoju." % (jid), roomName, jid)
		Message.SendToUser(jid, u"Zostałeś zaproszony do pokoju '%s' przez '%s'." % (roomName, user.jid))

# Register commands
CommandDispatcher.register(['rooms','pokoje'], RoomsCommand)
CommandDispatcher.register(['join','dolacz'], JoinCommand)
CommandDispatcher.register('switch', SwitchCommand)
CommandDispatcher.register(['leave', 'opusc'], LeaveCommand)
CommandDispatcher.register(['invite', 'zapros'], InviteCommand)
