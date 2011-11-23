#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from datetime import datetime
from botModels import Roster, Sync, SyncAnswers
import logging, time, datetime, messageHandler, settings

class CronHandler(webapp.RequestHandler):

	# Worker powinien być odpalany np co 1 minutę
	# powinien szukać rekordów z Sync gdzie done=False
	# nastepnie sprawdzic czy przyszedl juz ich czas (czy wieksze niz 5 min)
	# jezeli tak to powinien sprawdzic czy ktos odpowiedzial na synchro
	# zlozyc odpowiedz dla wlasciciela, wyslac info dla tych co odpowiedzieli
	# odnzaczyc zadanie
	def _sync(self):
		logging.info('SYNC WORKER: START')
		items = Sync.all()
		items.filter('done =',False)
		items = items.fetch(100)
		if len(items) == 0:
			logging.info('SYNC WORKER: Brak zadań. Kończę pracę.')
			return True
		for item in items:
			t = datetime.datetime(*time.strptime(str(item.created).split('.')[0],"%Y-%m-%d %H:%M:%S")[0:5])
			difference = datetime.datetime.now() - t
			minutes, seconds = divmod(difference.seconds, 60)
			if minutes > settings.SYNC_LIMIT_MIN:
				logging.info('Szukam SyncAnswers.syncId = %s', (item.key().id()))
				ans = SyncAnswers.all()
				ans.filter('syncId =',item.key().id())
				ans = ans.fetch(100)
				if len(ans) == 0:
					logging.info(item.jid)
					xmpp.send_message(item.jid,u'Nikt nie odpowiedział na Twoją synchronizację dotyczącą plików:\n%s' % (item.files))
					item.done = True
					item.put()
					continue
				# Zobacz jakie byly odpowiedzi
				odpTak = 0
				odpNie = 0
				osobyNie = []
				jids = []
				for an in ans:
					jids.append(an.jid)
					if an.syncCmd:
						odpTak=odpTak+1
					else:
						odpNie=odpNie+1
						osobyNie.append(an.jid)
				# Message do autora
				msg = ''
				if odpTak > 0 and odpNie == 0:
					msg = u'Wszyscy zgodzili się na Twoje synchro. Osób za %s, przeciwko %s.'
					msg = msg % (odpTak,odpNie)
				elif odpNie > 0 and odpTak == 0:
					msg = u'Nikt nie zgodził się na Twoje synchro. Osób za %s, przeciwko %s. Osoby przeciwko to:\n'
					msg = msg % (odpTak,odpNie)
					for osoba in osobyNie:
						msg=msg+osoba+'\n'
				else:
					msg = u'Odpowiedź na Twoje synchro: osób za %s, przeciwko %s. Osoby przeciwko to:\n'
					msg = msg % (odpTak,odpNie)
					for osoba in osobyNie:
						msg=msg+osoba+'\n'
				xmpp.send_message(item.jid,msg)
				
				# Message do tych co oddali odpowiedz
				msg = 'Wyniki głosowania o synchro w którym brałeś udział to: osób za %s, przeciwko %s.'
				msg = msg % (odpTak,odpNie)
				xmpp.send_message(jids,msg)
				
				item.done = True
				item.put()


	def get(self):
		name = self.request.path.replace('/cron/','')
		if(name == 'sync'):
			self._sync()
		else:
			logging.error('Brak CRONa o nazwie: %s' % (name))
