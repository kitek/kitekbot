#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from library.DbProperty import CetDateTimeProperty

class Chats(db.Model):
	jid = db.StringProperty(required=True)
	message = db.StringProperty(required=True)
	roomName = db.StringProperty(required=True, default='global')
	created = CetDateTimeProperty(auto_now_add=True)
