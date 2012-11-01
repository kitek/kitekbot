# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import logging
from google.appengine.ext import db
from Base import BaseController
from models.Users import Users
from models.UsersInvited import UsersInvited
from models.UsersSettings import UsersSettings

class DebugController(BaseController):
	title = 'Debug - Kitekbot'

	def get(self):

		#jid = ''
		#user = Users.getByJid(jid)
		#user = Users.get_by_key_name(jid)
		#logging.info(user.settings[0].name)

		#settings = UsersSettings.all()
		#settings.filter('user =', user)
		#items = settings.fetch(limit=1000,keys_only=True)
		#if len(items):
			#db.delete(items)
			#items.delete()

		#logging.info(len(items))


		#x = {'pole1':1,'pole2':2}
		#logging.info(x)

		#UsersSettings.set(user,'receiveMsgWhenOffline',x)
		#UsersSettings(user=user,name='receiveMsgWhenOffline',value='1').put()

		#user.aclRole = 'user'
		#user = Users(key_name=jid)
		#user.put()




		#invitation = UsersInvited(key_name=jid,invitedBy='admin@kitek.pl')
		#invitation.put()


		pass
	def dispatch(self):
		isDevServer = os.environ['SERVER_SOFTWARE'].startswith('Development')
		if isDevServer:
			super(DebugController, self).dispatch()
		else:
			self.response.write('Debug is available only on development server.')


		