# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import webapp2
from webapp2_extras import json
from webapp2_extras import jinja2
from google.appengine.api import taskqueue
from Base import BaseController
from library.Message import Message
from models.Users import Users
from models.ApiAccess import ApiAccess


class ApiController(BaseController):
	"""
		Wymagany parametr: hash - patrz komenda /api (sprawdzany w dispatch'u)
		@todo To wymaga refaktoryzacji gdy bedzie potrzeba wprowadzenia innych funkcjonalnosci w API

		Na chwile obecna obslugiwane sa jedynie requesty /api/message/send
		- to - do kogo wysłać wiadomość (pełny jid lub kilka rozdzielonych przecinkami)  lub * (do wszystkich dostępnych w Roster'ze)
		- body - treść wiadomości
		- countdown - kiedy dostarczyć wiadomość wyrazone w sekundach (np. za 3600 = 1h)
	"""
	def post(self, moduleName, commandName):
		self.view['response'] = ''

		if False == self.request.POST.has_key('to'):
			self.error(u"Required parameter 'to' was not specified.")
			return
		if False == self.request.POST.has_key('body'):
			self.error(u"Required parameter 'body' was not specified.")
			return

		to = self.request.POST['to'].lower().strip()
		body = self.request.POST['body'].strip()
		countdown = 0

		# Sprawdz czy przeslano tresc
		if 0 == len(body):
			self.error(u"Required parameter 'body' was not specified.")
			return

		# Sprawdz czy przeslano countdown (jezeli tak to kolejkujemy zadanie)
		if self.request.POST.has_key('countdown'):
			try:
				countdown = int(self.request.POST['countdown'])
			except ValueError:
				self.error(u"Invalid 'countdown' parameter.")
				return
        
        # Sprawdzamy czy to zadanie do wynania teraz czy pozniej
		if countdown > 0:
			# Dodaj zadanie do kolejki (pamietaj o przeslaniu klucza)
			taskqueue.add(url='/api/message/send',params={'to':to,'body':body,'hash':self.request.POST['hash']}, method='POST', countdown=countdown)
			self.ok(u"Added to queue.")
			return

        # Wysylamy do wszystkich
		if '*' == to:
			Message.broadcastSystem(body, 'global')
			self.ok(u"Sent to all users.")
			return
		# Sprawdz czy istnieje odbiorca
		toJids = to.split(',')
		allJids = []
		sendTo = []
		roster = Users.getAll()
		for user in roster:
			allJids.append(user.jid)

		for jid in toJids:
			if jid.lower().strip() in allJids:
				sendTo.append(jid)
		
		if 0 == len(sendTo):
			self.error(u"No such users.")
			return

		# Wysylamy wiadomosc
		Message.send(sendTo, body, recordChat = False, sendJid = False)
		self.ok(u"Sent to: %s." % (u', '.join(sendTo)))

	def dispatch(self):
		if False == self.request.POST.has_key('hash'):
			self.error(u"Required parameter 'hash' was not specified.")
			return
		app =  ApiAccess.get_by_key_name(self.request.POST['hash'])
		if None == app:
			self.error(u"Invalid 'hash'.")
			return
		try:
			# Dispatch the request.
			self.response.content_type = 'application/json'
			webapp2.RequestHandler.dispatch(self)
			self.response.write(self.view['response'])
		finally:
			pass

	def error(self, info):
		errorResponse = {'status':'ERROR', 'info' : info}
		self.response.content_type = 'application/json'
		self.response.write(json.encode(errorResponse))

	def ok(self, info):
		okResponse = {'status':'OK', 'info' : info}
		self.response.content_type = 'application/json'
		self.response.write(json.encode(okResponse))


		