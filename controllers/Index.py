# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
from Base import BaseController
from models.Users import Users

class IndexController(BaseController):
	title = 'Bot'

	def get(self):

		self.view['jid'] = self.currentUser.jid

		