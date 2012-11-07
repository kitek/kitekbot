#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from library.DbProperty import CetDateTimeProperty

class RoomSubscriptions(db.Model):
	name = db.StringProperty(required=True)
	jid = db.StringProperty(required=True)
	created = CetDateTimeProperty(auto_now_add=True)