# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import webapp2
# Web
from controllers.Index import IndexController
from controllers.Debug import DebugController
from controllers.Admin import AdminController
from controllers.Api import ApiController
# Xmpp
from library.XmppSubscribe import SubscribeHandler
from library.XmppSubscribed import SubscribedHandler
from library.XmppUnsubscribe import UnsubscribeHandler
from library.XmppUnsubscribed import UnsubscribedHandler
from library.XmppAvailable import AvailableHandler
from library.XmppUnavailable import UnavailableHandler
from library.XmppMessage import MessageHandler
from library.XmppProbe import ProbeHandler

app = webapp2.WSGIApplication([
	('/', IndexController),
	('/debug', DebugController),
	('/admin', AdminController),
	(r'/api/([A-Za-z0-9]+)/?([A-Za-z0-9]+)?', ApiController),

	('/_ah/xmpp/subscription/subscribe/', SubscribeHandler),
	('/_ah/xmpp/subscription/subscribed/', SubscribedHandler),
	('/_ah/xmpp/subscription/unsubscribe/', UnsubscribeHandler),
	('/_ah/xmpp/subscription/unsubscribed/', UnsubscribedHandler),
	('/_ah/xmpp/presence/available/', AvailableHandler),
	('/_ah/xmpp/presence/unavailable/', UnavailableHandler),
	('/_ah/xmpp/presence/probe/', ProbeHandler),
	('/_ah/xmpp/message/chat/', MessageHandler)

],debug=os.environ['SERVER_SOFTWARE'].startswith('Development'))
