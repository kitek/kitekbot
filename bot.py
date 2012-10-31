#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# Force Django to reload its settings.
from django.conf import settings
settings._target = None

# Must set this env var before importing any part of Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.ext.webapp import xmpp_handlers
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import wsgiref.handlers
import logging, presenceHandler
import webHandler, messageHandler, subscirbeHandler, unsubscirbeHandler, botModels, cronHandler


__version__ = "1.0"

def main():
	app = webapp.WSGIApplication([
		# Web
		('/', webHandler.IndexHandler),
		(r'/login/?', webHandler.LoginHandler),
		(r'/logout/?', webHandler.LogoutHandler),
		(r'/chats/?', webHandler.ChatsHandler),
		(r'/chats/([a-z0-9\-]+)/?(\d+)?', webHandler.ChatsHandler),
		#(r'/sync/?', webHandler.SyncHandler),

		#(r'/solutions/?', webHandler.SolutionsHandler),
		#(r'/solutions/[0-9]+', webHandler.SolutionHandler),
		#(r'/solutions/add/?', webHandler.SolutionsAddHandler),
		
		# XMPP
		('/_ah/xmpp/message/chat/', messageHandler.MessageHandler),
		('/_ah/xmpp/message/error/', messageHandler.MessageErrHandler),
		('/_ah/xmpp/subscription/subscribe/', subscirbeHandler.SubscirbeHandler),
		('/_ah/xmpp/subscription/subscribed/', subscirbeHandler.SubscirbedHandler),
		('/_ah/xmpp/subscription/unsubscribed/', unsubscirbeHandler.UnSubscirbeHandler),
		('/_ah/xmpp/presence/available/', presenceHandler.AvailableHandler),
		('/_ah/xmpp/presence/unavailable/', presenceHandler.UnavailableHandler),
		('/_ah/xmpp/presence/probe/', presenceHandler.ProbeHandler),
		
		# CRON
		('/cron/.*',cronHandler.CronHandler)
	], debug=True)
	wsgiref.handlers.CGIHandler().run(app)

if __name__ == '__main__':
	main()