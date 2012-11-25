#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from library.DbProperty import CetDateTimeProperty

class ApiAccess(db.Model):
	"""
	Przechowuje informacje o dostępie do API
	key - wygenerowany klucz md5
	appName - nazwa aplikacji
	"""
	appName = db.StringProperty(required=True)
	created = CetDateTimeProperty(auto_now_add=True)
	authorJid = db.StringProperty(required=False)
