#!/usr/bin/python
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.api import xmpp
from botModels import Roster
import logging

class UnSubscirbeHandler(webapp.RequestHandler):
	
	def post(self):
		jid = self.request.get('from').split('/')[0]
		logging.info("UnSubskrypcja od: %s", jid)
		Roster.deleteByJid(jid)