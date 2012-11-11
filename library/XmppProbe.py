#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.api import xmpp
from google.appengine.api import memcache
from library.XmppCore import XmppHandler

class ProbeHandler(XmppHandler):
	def post(self):
		status = memcache.get('xmppStatus')
		if None != status:
			xmpp.send_presence(self.data['user'].jid, status, presence_show=xmpp.PRESENCE_TYPE_AVAILABLE)

