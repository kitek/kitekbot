#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from library.XmppCore import XmppHandler

class UnsubscribeHandler(XmppHandler):
	def post(self):
		logging.info("Unsubscribe initiated (unsubscribe) from: %s", self.jid)