# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from Base import BaseController
from models.Users import Users

class AdminController(BaseController):
	title = 'Panel administratora - Kitekbot'

	def get(self):
		self.view['jid'] = self.currentUser.jid
		self.view['usersTab'] = Users.getAll()
		pass
		
