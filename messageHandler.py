#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.api import xmpp
from google.appengine.ext.webapp import xmpp_handlers
from botModels import Version, Sync, Roster, SyncAnswers, InfoMessages, Menu, Presence
import logging, re, time, datetime

class MessageHandler(xmpp_handlers.CommandHandler):
	syncAllowMinutes = 5
	usersLimit = 100
	
	commands = dict({
		'help':'Wyświetla informacje o dostępnych komendach systemu',
		'help nazwaPolecenia':'Wyświetla szczegółową pomoć dla podanego polecenia',
		'sync plik1...plikN':'Wysyła informacje o plikach do synchronizacji',
		'sync on|off':'Włącza/Wyłącza otrzymywanie informacji o synchronizowanych plikach',
		'info TwojaWiadomość':'Wysyła dowolną wiadomość do osób, które chcą otrzymywać tego rodzaju komunikaty',
		'info on|off':'Włącza/Wyłącza otrzymywanie informacji od użytkowników systemu',
		'menu (jutro)':'Wyświetla menu obiadowe na dzisiejszy / jutrzejszy dzień'
	})
	commands_help = dict({
		'sync':'Lorem ipsum for sync',
		'info':'Lorem ipsum for info'
	})
	
	def text_message(self, message=None):
		self.info_command(message)
		
	def unhandled_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		message.reply("Nieznana komenda. Wpisz \help by wyświetlić pomoc.")
	
	def rescue_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False

		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		logging.info('RESCUE: %s from %s' % (info,jid))
	
	def menu_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		logging.info(info)
		
		dzis = datetime.date.today()
		jutro = dzis + datetime.timedelta(days=1)
		 
		if info == 'jutro':
			qDzien = jutro
		else:
			qDzien = dzis

		r = Menu.all()			
		r.filter("data =",qDzien)			
		items = r.fetch(1)
		if(len(items) == 0):
			message.reply('Brak infomracji o menu obiadowym na dzień: %s' % (qDzien))
		else:
			if info == 'jutro':
				message.reply('Jutro na obiad: %s' % (items[0].name))
			else:
				message.reply('Dzisiaj na obiad: %s' % (items[0].name))
	
	def info_command(self, message=None):
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
		
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		logging.info('INFO: %s from %s' % (info,jid))
		if(len(info) <= 1):
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
			message.reply('Wpisz dłuższą wiadomość (minimum to 1 znak).')
			return False
		
		r = Roster.all()
		r.filter("jid !=",jid)
		r.filter("infoCmd =",True)
		items = r.fetch(self.usersLimit)
		if len(items) == 0:
			message.reply('Brak osób które mogłyby odpowiedzieć na Twoją wiadomość (wszyscy wyłączyli sobie chęć odbierania tego typu powiadomień?).')
			return False
		jids = []
		for item in items:
			jids.append(item.jid)
		xmpp.send_message(jids,u'%s: %s' % (jid.replace('@firma.fotka.pl',''),info))
		mes = InfoMessages(jid=jid,message=info)
		mes.put()
	
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
				if minutes > self.syncAllowMinutes:
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
				if self.syncAllowMinutes > minutes:
					message.reply('W ciągu ostatnich %s minut synchronizowałeś już pliki. Odczekaj troszkę i daj odpocząć serwerom :)' % (self.syncAllowMinutes))
					return False
			r = Roster.all()
			r.filter("jid !=",jid)
			r.filter("syncCmd =",True)
			items = r.fetch(self.usersLimit)
			if(len(items) == 0):
				message.reply('Brak osób które mogłyby odpowiedzieć na Twoją synchronizację (wszyscy wyłączyli sobie chęć odbierania tego typu powiadomień?).')
				return False
			sync = Sync(jid=jid,files=pliki)
			sync.put()
			logging.info('SYNC: zapisano.')
			
			usersOnline = 0
			for item in items:
				# Sprawdz status
				presence = Presence.all()
				presence.filter('userRef =',item)
				presence.order("-__key__")
				presence = presence.fetch(1)
				if len(presence) > 0 and presence[0].type == Presence.AVAILABLE:
					usersOnline+=1
			# Informacja o synchro została wysłana do 5 osób (w tym 2 Idle) <-- tu powinno byc sprawdzone kto jest online 
			message.reply('Informacja o synchro została wysłana do %s osób (w tym %s online). Jeżeli w przeciągu %s minut ktoś odpowie na Twoją prośbę zostaniesz o tym automatycznie poinformowany.' % (len(items),usersOnline,self.syncAllowMinutes))
			jids = []
			for item in items:
				jids.append(item.jid)
			msg = u'SYNC: *%s*\nPowyższe pliki zostaną synchronizowane przez %s. Czy wyrażasz na to zgodę? Odpowiedz: /sync tak|ok|yes jeżeli nie masz nic przeciwko lub /sync nie|no jeżeli synchronizacja ma zostać przerwana.'
			xmpp.send_message(jids,msg % (pliki,jid),None,xmpp.MESSAGE_TYPE_CHAT)

	def help_command(self, message=None):
		logging.info('HELP')
		jid = message.sender.split('/')[0]
		if Roster.check_jid(jid) == False:
			return False
	
		info = message.arg.strip().replace("\r"," ")
		info = re.sub('\n',' ',info)
		
		if info != None and self.commands_help.has_key(info):
			message.reply(self.commands_help[info])
			return True
			
		cmd = ""
		keys = self.commands.keys()
		keys.sort()
		for key in keys:
			cmd += "/"+key+" - "+self.commands[key]+"\n"
		
		# link do webGUI
		gui_hash = ''
		user = Roster.findByJid(jid)
		if(user != None):
			gui_hash = str(user.key())
		
		message.reply("Devel ver. %s\nLista dostępnych poleceń:\n%s\n\nLink do webGUI: %s" % (Version.getMajorVersion(), cmd, Roster.webgui_link+gui_hash))
		return True
	def _checkSyncTime(self,item):
		t = datetime.datetime(*time.strptime(str(item.created).split('.')[0],"%Y-%m-%d %H:%M:%S")[0:5])
		difference = datetime.datetime.now() - t
		minutes, seconds = divmod(difference.seconds, 60)
		logging.info('SYNC ok diff: %s' % (minutes))
		if minutes > self.syncAllowMinutes:
			return False
		else:
			return True
