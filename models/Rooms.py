#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import re
from google.appengine.ext import db
from library.DbProperty import CetDateTimeProperty

class Rooms(db.Model):
	NAME_PATTERN = "a-zA-Z0-9\_\-"
	NAME_MIN_LEN = 3
	rejectedNames = ['global']

	name = db.StringProperty(required=True)
	seqId = db.IntegerProperty(required=True)
	count = db.IntegerProperty(default=1,required=False)
	authorJid = db.StringProperty(required=False)
	created = CetDateTimeProperty(auto_now_add=True)

	@staticmethod
	def isValidName(name):
		roomName = re.sub('[^'+Rooms.NAME_PATTERN+']+','',name)
		if roomName <> name:
			return u"Nazwa pokoju '%s' może składać się tylko ze zbioru znaków: [%s]+\n" % (name, Rooms.NAME_PATTERN)
		if len(roomName) < Rooms.NAME_MIN_LEN:
			return u"Nazwa pokoju musi posiadać minimum %s znaki." % (Rooms.NAME_MIN_LEN)
		if roomName.lower() in Rooms.rejectedNames:
			return u"Nazwa pokoju '%s' jest zastrzeżona. Podaj inną." % (roomName)
		return True
