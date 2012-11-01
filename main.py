# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import webapp2
from controllers.Index import IndexController
from controllers.Debug import DebugController
from library.XmppSubscribe import SubscribeHandler
from library.XmppSubscribed import SubscribedHandler
from library.XmppUnsubscribed import UnsubscribedHandler

app = webapp2.WSGIApplication([
	('/', IndexController),
	('/debug', DebugController),

	('/_ah/xmpp/subscription/subscribe/', SubscribeHandler),
	('/_ah/xmpp/subscription/subscribed/', SubscribedHandler),
	('/_ah/xmpp/subscription/unsubscribed/', UnsubscribedHandler)

],debug=os.environ['SERVER_SOFTWARE'].startswith('Development'))
