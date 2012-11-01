#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
from pytz.gae import pytz
from google.appengine.ext import db


class CetDateTimeProperty(db.DateTimeProperty):

	def get_value_for_datastore(self, model_instance):
		date = super(CetDateTimeProperty, self).get_value_for_datastore(model_instance)
		if date:
			if date.tzinfo:
				return date.astimezone(pytz.utc)
			else:
				return date.replace(tzinfo=pytz.utc)
		else:
  			return None
  	def make_value_from_datastore(self, value):
		if value is None:
			return None
		else:
			utc=pytz.UTC
			dt = utc.localize(value)
			return dt.astimezone(pytz.timezone('Europe/Warsaw'))
