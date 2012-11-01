#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from google.appengine.ext import db
from library.DbProperty import CetDateTimeProperty

"""
Lista zaproszonych użytkowników.
UsersInvited:
	- key_name (jid)
	- created (datetime)
	- invitedBy (jid)
"""

class UsersInvited(db.Model):
	created = CetDateTimeProperty(auto_now_add=True)
	invitedBy = db.StringProperty(required=True,multiline=False)
	@property
	def jid(self):
		return self.key().name()
