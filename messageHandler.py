#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.api import xmpp
from google.appengine.ext import db
from google.appengine.ext.webapp import xmpp_handlers
from datetime import datetime
from botModels import Version, Sync, Roster, SyncAnswers, InfoMessages, PresenceStatus, RoomSubscriptions, Rooms, DbSettings
import logging, re, time, datetime, settings, re
import hashlib

class MessageHandler(xmpp_handlers.CommandHandler):
	
	def text_message(self, message=None):
		if '/' == message.arg.strip()[0]:
			self.unhandled_command(message)
			return False
		if '#' == message.arg.strip()[0]:
			self.send_to_room(message)
			return False
		self.info_command(message)
		
	def unhandled_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		message.reply("Nieznana komenda. Wpisz \help by wyświetlić pomoc.")
	
	# Umożliwia zaproszenie osoby do pokoju /invite piwo radek.gniado
	def invite_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		info = message.arg.strip().replace("\r","")
		info = re.sub('\n','',info)
		params = info.split(' ');
		try:
			Rooms(name='Rooms',author=jid).invite(jid,params[0],params[1])	
		except IndexError:
			message.reply(u'Poprawna składnia to /invite kto nazwaPokoju')
		
	
	# /switch piwo
	def switch_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		info = message.arg.strip().replace("\r","")
		info = re.sub('\n','',info)
		Rooms(name='Rooms',author=jid).switch(jid,info)
		pass

	# Wysyła wiadomość do wszystkich użytkowników w pokoju
	def send_to_room(self,message=None,roomName=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		if roomName != None:
			info = u"#"+roomName+u" "+info
		return Rooms(name='Rooms',author=jid).send(jid,info)

	# Wyświetla informacje o dostępnych pokojach, wraz z liczbą użytkowników
	def rooms_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		Rooms(name='Rooms',author=jid).show(jid,message.arg.strip())

	# Umożliwia utworzenie / podłączenie się do pokoju (/join roomName)
	def join_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		Rooms(name='Rooms',author=jid).join(jid,message.arg.strip())
		
	# Umożliwia wypisanie / usunięcie pokoju (/leave roomName)
	def leave_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		Rooms(name='Rooms',author=jid).leave(jid,message.arg.strip())

	# Wyświetla użytkowników ktorzy sa online
	def online_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		p = PresenceStatus.all()
		p = p.fetch(settings.BROADCAST_USERS_LIMIT)
		if len(p) == 0:
			message.reply("Brak danych o użytkownikach")
		else:
			reply = 'Online [$ile/$all]:\n'
			ile = 0
			all = 0
			for item in p:
				if item.online:
					item.name = item.name.replace("@"+settings.ALLOWED_DOMAIN,"").replace('.',' ').title()
					reply+=item.name+'\n'
					ile = ile + 1
				all = all + 1
			if ile == 0:
				reply+='brak\n'
			reply = reply.replace('$ile', str(ile)).replace('$all', str(all))
			message.reply(reply)

	# Wyświetla użytkowników ktorzy sa offline + daty kiedy ostatni raz byli online
	def offline_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		p = PresenceStatus.all()
		p = p.fetch(settings.BROADCAST_USERS_LIMIT)
		if len(p) == 0:
			message.reply("Brak danych o użytkownikach")
		else:
			reply='\nOffline [$ile/$all]:\n'
			ile = 0
			all = 0
			for item in p:
				if item.online == False:
					item.name = item.name.replace("@"+settings.ALLOWED_DOMAIN,"").replace('.',' ').title()
					reply+=item.name+' ('+item.last.strftime("%Y-%m-%d %H:%I:%S")+')\n'
					ile = ile + 1
				all = all + 1
			if ile == 0:
				reply+='brak\n'
			reply = reply.replace('$ile', str(ile)).replace('$all', str(all))
			message.reply(reply)

	def info_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		if(len(info) <= 1):
			message.reply('Wpisz dłuższą wiadomość (minimum to 2 znaki).')
			return False
		if info in ['off','on']:
			infoCmd = False;
			if info == 'on':
				infoCmd = True
			r = Roster.findByJid(jid)
			if r <> None:
				r.infoCmd = infoCmd
				r.put()
			if infoCmd:
				message.reply('Od tej chwili będziesz otrzymywał informacje od użytkowników systemu. Zawsze możesz to zmienić wpisująć /info off')
			else:
				message.reply('Informacje od użytkowników systemu nie będą już więcej wysyłane do Ciebie. Zawsze możesz to zmienić wpisująć /info on')
			return True
		
		# Sprawdz na jakim pokoju pisze user
		currentRoom = DbSettings.get(jid,"currentRoom")
		if currentRoom != None and currentRoom != "global":
			self.send_to_room(message,currentRoom)
			return True

		r = Roster.all()
		r.filter("jid !=",jid)
		r.filter("infoCmd =",True)
		items = r.fetch(settings.BROADCAST_USERS_LIMIT)
		if len(items) == 0:
			message.reply('Brak osób które mogłyby odpowiedzieć na Twoją wiadomość (wszyscy wyłączyli sobie chęć odbierania tego typu powiadomień?).')
			return False
		jids = []
		for item in items:
			jids.append(item.jid)
		xmpp.send_message(jids,u'%s: %s' % (re.sub(r'([\w\.-]+)@([\w\.-]+)', r'\1',jid),info))
		try:
			mes = InfoMessages(jid=jid,message=info)
			mes.put()
		except:
			message.reply('Hurray! BOT exceeded quota limit. Thx You :)	');
	
	def sync_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		
		pliki = message.arg.strip().replace("\r"," ")
		pliki = re.sub('\n',' ',pliki)
		logging.info('SYNC: %s from %s' % (pliki,jid))
		cmd = pliki.split(' ')
		
		if(len(pliki) == 0):
			message.reply('Podaj listę plików, które chesz synchronizować - wpisz np.: /sync mojPlik.php robertaPlik.php')
		#elif(len(pliki) < 5):
		elif (len(cmd) > 0 and cmd[0] in ['off','on','ok','yes','tak','nie','no']):
			# /sync off
			if pliki == 'off':
				r = Roster.findByJid(jid)
				if r <> None:
					r.syncCmd = False
					r.put()
				message.reply('Informacje o plikach do synchronizacji nie będą już więcej wysyłane do Ciebie. Zawsze możesz to zmienić wpisująć /sync on')
				logging.info('SYNC OFF: %s' % (jid))
				return True
			# /sync on
			if pliki == 'on':
				r = Roster.findByJid(jid)
				if r <> None:
					r.syncCmd = True
					r.put()
				message.reply('Od tej chwili będziesz otrzymywał informacje o plikach do synchronizacji. Zawsze możesz to zmienić wpisująć /sync off')
				logging.info('SYNC ON: %s' % (jid))
				return True
			# /sync ok | yes | tak
			# /sync ok 1234
			if len(cmd) > 0 and cmd[0] in ['ok','yes','tak','nie','no']:
				syncOdp = False
				if cmd[0] in ['ok','yes','tak']:
					syncOdp = True
				#Sprawdz czy ktos pyta o synchro
				sync = Sync.all()
				sync.filter('done =',False)
				sync.order("-__key__")
				item = sync.fetch(10)
				# Brak sync
				if len(item) == 0:
					message.reply('W tej chwili nikt nie synchronizuje plików. Jeżeli sam chcesz coś synchronizować wpisz np.: /sync plik1.php')
					return False
				# Więcej niż 1
				elif len(item) > 1:
					multiSync = []
					for i in item:
						if i.jid == jid:
							continue
						if self._checkSyncTime(i):
							multiSync.append(i)
					if len(multiSync) > 0:
						if len(cmd) > 1 and cmd[1] != None:
							try:
								idSync = int(cmd[1])
								# Sprawdz czy id sync istnieje, jak tak to oznacz
								logging.info('Sprawdzam czy istnieje sync %s' % (idSync))
								for i in multiSync:
									if i.key().id() == idSync:
										logging.info('Sync istnieje')
										syncAns = SyncAnswers.all()
										syncAns.filter("jid =",jid)
										syncAns.filter("syncId =",i.key().id())
										syncAns = syncAns.fetch(1)
										if len(syncAns) > 0:
											sync = syncAns[0]
											sync.syncCmd = syncOdp
											sync.put()
											message.reply('Twoja odpowiedź została zaktualizowana.')
											return True
										SyncAnswer = SyncAnswers(syncId=i.key().id(),jid=jid,syncCmd=syncOdp)
										SyncAnswer.put()
										message.reply('Dziękuje za odpowiedź.')
										return True
								message.reply('Aktualnie nie ma synchro o identyfikatorze `%s`. Popraw i spróbuj ponownie :)' % (idSync))
								return False
							except ValueError:
								logging.info('Blad parsowania')
								message.reply(u'Identyfikator `%s` nie jest poprawną liczbą. Popraw i spróbuj ponownie :)' % (cmd[1]))
								return False
						wiadomosc = u'W tym samym czasie przeprowadzanych jest %s pytań o synchro:\n' % (len(multiSync))
						for i in multiSync:
							wiadomosc+=u'%s) %s: *%s*\n' % (i.key().id(),i.jid,i.files)
						wiadomosc+=u'Odpisz np `/sync ok %s` by zgodzić się na pierwsze synchro' % (multiSync[0].key().id())
						message.reply(wiadomosc)
					else:
						message.reply('W tej chwili nikt nie synchronizuje plików.')
					return False
				
				# Jedno synchro
				t = datetime.datetime(*time.strptime(str(item[0].created).split('.')[0],"%Y-%m-%d %H:%M:%S")[0:5])
				difference = datetime.datetime.now() - t
				minutes, seconds = divmod(difference.seconds, 60)
				logging.info('SYNC ok diff: %s' % (minutes))
				if minutes > settings.SYNC_LIMIT_MIN:
					message.reply('W tej chwili nikt nie synchronizuje plików. Ostatnia prośba o synchro miało miejsce %s minut temu.' % (minutes))
					return False
				#Sprawdz czy synchro nie robie ja sam
				if item[0].jid == jid:
					message.reply('Trwa zbieranie odpowiedzi od innych osób. Poczekaj cierpliwie na odpowiedź w sprawie Twojego synchro.')
					return False
				#Sprawdz czy juz odpowiadales
				sync = SyncAnswers.all()
				sync.filter("jid =",jid)
				sync.filter("syncId =",item[0].key().id())
				sync = sync.fetch(1)
				if len(sync) > 0:
					sync = sync[0]
					sync.syncCmd = syncOdp
					sync.put()
					message.reply('Twoja odpowiedź została zaktualizowana.')
					return True
				#Odpowiedz
				SyncAnswer = SyncAnswers(syncId=item[0].key().id(),jid=jid,syncCmd=syncOdp)
				SyncAnswer.put()
				message.reply('Dziękuje za odpowiedź.')
				return True
		else:
			if(len(pliki) < 5):
				message.reply('Co tak skromnie? Podaj więcej plików, które chesz synchronizować - wpisz np.: /sync mojPlik.php robertaPlik.php')
				return False
			sync = Sync.all()
			sync.filter("jid =", jid)
			sync.order("-__key__")
			item = sync.fetch(1)
			if len(item) > 0:
				t = datetime.datetime(*time.strptime(str(item[0].created).split('.')[0],"%Y-%m-%d %H:%M:%S")[0:5])
				difference = datetime.datetime.now() - t
				minutes, seconds = divmod(difference.seconds, 60)
				logging.info('SYNC diff: %s' % (minutes))
				if settings.SYNC_LIMIT_MIN > minutes:
					message.reply('W ciągu ostatnich %s minut synchronizowałeś już pliki. Odczekaj troszkę i daj odpocząć serwerom :)' % (settings.SYNC_LIMIT_MIN))
					return False
			r = Roster.all()
			r.filter("jid !=",jid)
			r.filter("syncCmd =",True)
			items = r.fetch(settings.BROADCAST_USERS_LIMIT)
			if(len(items) == 0):
				message.reply('Brak osób które mogłyby odpowiedzieć na Twoją synchronizację (wszyscy wyłączyli sobie chęć odbierania tego typu powiadomień?).')
				return False
			sync = Sync(jid=jid,files=pliki)
			sync.put()
			
			usersOnline = 0
			p = PresenceStatus.all(keys_only=True)
			p.filter("online =",True)
			usersOnline = p.count() - 1 if p.count() > 0 else 0

			# Informacja o synchro została wysłana do 5 osób (w tym 2 Idle) <-- tu powinno byc sprawdzone kto jest online 
			message.reply('Informacja o synchro została wysłana do %s osób (w tym %s online). Jeżeli w przeciągu %s minut ktoś odpowie na Twoją prośbę zostaniesz o tym automatycznie poinformowany.' % (len(items),usersOnline,settings.SYNC_LIMIT_MIN))
			jids = []
			for item in items:
				jids.append(item.jid)
			msg = u'SYNC: %s\nPowyższe pliki zostaną synchronizowane przez %s. Czy wyrażasz na to zgodę? Odpowiedz: /sync tak|ok|yes jeżeli nie masz nic przeciwko lub /sync nie|no jeżeli synchronizacja ma zostać przerwana.'
			xmpp.send_message(jids,msg % (pliki,jid),None,xmpp.MESSAGE_TYPE_CHAT)

	def help_command(self, message=None):
		logging.info('HELP')
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
	
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		
		if info != None and settings.COMMANDS_HELP.has_key(info):
			message.reply(settings.COMMANDS_HELP[info])
			return True
			
		cmd = ""
		keys = settings.COMMANDS_DESC.keys();
		keys.sort()
		for key in keys:
			cmd += "/"+key+" - "+settings.COMMANDS_DESC[key]+"\n"
		
		# link do webGUI
		gui_hash = ''
		user = Roster.findByJid(jid)
		if(user != None):
			if user.password == None or user.password == Null:
				# Generate password
				m = hashlib.md5()
				m.update("Nobody inspects")
				#logging.info(str(m.digest()))
				
			gui_hash = str(user.key())
		logging.info('xxx')
		#message.reply("Devel ver. %s\nLista dostępnych poleceń:\n%s\n\nLink do webGUI: %s" % (Version.getMajorVersion(), cmd, settings.WEBGUI_URL+gui_hash))
		return True
	
	def _checkSyncTime(self,item):
		t = datetime.datetime(*time.strptime(str(item.created).split('.')[0],"%Y-%m-%d %H:%M:%S")[0:5])
		difference = datetime.datetime.now() - t
		minutes, seconds = divmod(difference.seconds, 60)
		logging.info('SYNC ok diff: %s' % (minutes))
		if minutes > settings.SYNC_LIMIT_MIN:
			return False
		else:
			return True

class MessageErrHandler(xmpp_handlers.CommandHandler):
	def text_message(self, message=None):
		logging.error('ERROR messasge %s from %s' % (message.body, message.sender))
	def unhandled_command(self, message=None):
		logging.error('ERROR message %s from %s' % (message.body, message.sender))