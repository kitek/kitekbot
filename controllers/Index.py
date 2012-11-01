# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from Base import BaseController
from models.Users import Users

class IndexController(BaseController):
	title = 'Kitekbot'
	#template = 'innyWidok.html'
	def get(self):

		jid = 'jid@gmail.com'
		self.view['jid'] = jid

		#dbUser = Users(key_name=jid)
		#dbUser.aclRole = 'owner'
		#dbUser.created = datetime.datetime.now()
		#dbUser.put()
		#logging.info(dbUser.jid)

		