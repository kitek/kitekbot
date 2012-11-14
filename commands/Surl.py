# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import json
from google.appengine.api import app_identity
from google.appengine.api import urlfetch
from library.Message import Message
from library.XmppCommand import Command
from library.XmppCommand import CommandDispatcher

class SurlCommand(Command):
	description = u"Skraca podany link."
	help = u"Wymaga parametru będącego URL'em. Korzysta z urlshortener'a Google."
	def run(self, user, params):
		if len(params):
			long_url = params[0].strip()
			if len(long_url) == 0:
				Message.reply(u"Podaj URL do skrócenia.")
				return
			scope = "https://www.googleapis.com/auth/urlshortener"
			authorization_token, _ = app_identity.get_access_token(scope)
			payload = json.dumps({"longUrl": long_url})
			
			response = urlfetch.fetch("https://www.googleapis.com/urlshortener/v1/url?pp=1",
										method=urlfetch.POST,
										payload=payload,
										headers = {"Content-Type": "application/json","Authorization": "OAuth " + authorization_token})
			
			if response.status_code == 200:
				result = json.loads(response.content)
				Message.reply(u"Short URL: %s" % (result["id"]))
				return
			Message.reply(u"Call failed. Status code %s. Body %s",response.status_code, response.content)
			return
		Message.reply(u"Podaj URL do skrócenia.")

CommandDispatcher.register(['surl','tnij'], SurlCommand)
