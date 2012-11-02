# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import webapp2
# Web
from controllers.Index import IndexController
from controllers.Debug import DebugController
# Xmpp
from library.XmppSubscribe import SubscribeHandler
from library.XmppSubscribed import SubscribedHandler
from library.XmppUnsubscribe import UnsubscribeHandler
from library.XmppUnsubscribed import UnsubscribedHandler
from library.XmppAvailable import AvailableHandler
from library.XmppUnavailable import UnavailableHandler
from library.XmppMessage import MessageHandler

app = webapp2.WSGIApplication([
	('/', IndexController),
	('/debug', DebugController),

	('/_ah/xmpp/subscription/subscribe/', SubscribeHandler),
	('/_ah/xmpp/subscription/subscribed/', SubscribedHandler),
	('/_ah/xmpp/subscription/unsubscribe/', UnsubscribeHandler),
	('/_ah/xmpp/subscription/unsubscribed/', UnsubscribedHandler),
	('/_ah/xmpp/presence/available/', AvailableHandler),
	('/_ah/xmpp/presence/unavailable/', UnavailableHandler),
	('/_ah/xmpp/message/chat/', MessageHandler)

],debug=os.environ['SERVER_SOFTWARE'].startswith('Development'))
