#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from library.XmppCore import XmppHandler

"""
Klasa obsługująca inicjalizację zaproszenia na poziomie XMPP.
Na chwilę obecną nie potrzebna tu jest specjalna implementacja.

"""
class SubscribeHandler(XmppHandler):
	def post(self):
		logging.info("Subscribe initiated (subscribe) from: %s", self.jid)
