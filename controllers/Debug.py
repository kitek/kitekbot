# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import logging
import datetime
from google.appengine.ext import db
from Base import BaseController
from models.Users import Users
from models.UsersInvited import UsersInvited
from models.UsersSettings import UsersSettings
from library.XmppCommand import CommandDispatcher
from google.appengine.api import users



class DebugController(BaseController):
	title = 'Debug - Kitekbot'

	def get(self):

		# Nowy uzytkownik
		# jid = 'tomek@o2.pl'
		# user = Users(key_name=jid)
		# user.currentRoom = 'global'
		# user.put()

		# UsersSettings.setupDefaults(jid)

		# Zmien ustawienia
		# settings = UsersSettings.set(jid,'offlineChat','disabled')

		pass
		
	def dispatch(self):
		isDevServer = os.environ['SERVER_SOFTWARE'].startswith('Development')
		if isDevServer:
			super(DebugController, self).dispatch()
		else:
			self.response.write('Debug is available only on development server.')


		