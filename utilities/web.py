#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template, RequestHandler
from botModels import Acl
from utilities.sessions import Session
# Ustawienia
import settings
settings = settings

import re
from datetime import datetime

def parseDateTime(s):
	"""Create datetime object representing date/time
	   expressed in a string
 
	Takes a string in the format produced by calling str()
	on a python datetime object and returns a datetime
	instance that would produce that string.
 
	Acceptable formats are: "YYYY-MM-DD HH:MM:SS.ssssss+HH:MM",
							"YYYY-MM-DD HH:MM:SS.ssssss",
							"YYYY-MM-DD HH:MM:SS+HH:MM",
							"YYYY-MM-DD HH:MM:SS"
	Where ssssss represents fractional seconds.	 The timezone
	is optional and may be either positive or negative
	hours/minutes east of UTC.
	"""
	if s is None:
		return None
	# Split string in the form 2007-06-18 19:39:25.3300-07:00
	# into its constituent date/time, microseconds, and
	# timezone fields where microseconds and timezone are
	# optional.
	m = re.match(r'(.*?)(?:\.(\d+))?(([-+]\d{1,2}):(\d{2}))?$',
				 str(s))
	datestr, fractional, tzname, tzhour, tzmin = m.groups()
 
	# Create tzinfo object representing the timezone
	# expressed in the input string.  The names we give
	# for the timezones are lame: they are just the offset
	# from UTC (as it appeared in the input string).  We
	# handle UTC specially since it is a very common case
	# and we know its name.
	if tzname is None:
		tz = None
	else:
		tzhour, tzmin = int(tzhour), int(tzmin)
		if tzhour == tzmin == 0:
			tzname = 'UTC'
		tz = FixedOffset(timedelta(hours=tzhour,
								   minutes=tzmin), tzname)
 
	# Convert the date/time field into a python datetime
	# object.
	x = datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")
 
	# Convert the fractional second portion into a count
	# of microseconds.
	if fractional is None:
		fractional = '0'
	fracpower = 6 - len(fractional)
	fractional = float(fractional) * (10 ** fracpower)
 
	# Return updated datetime object with microseconds and
	# timezone information.
	return x.replace(microsecond=int(fractional), tzinfo=tz)
 


class Controller(RequestHandler):
	__no_render = False
	__user_acl = settings.default_acl
	_acl = settings.default_acl_restriction
	_is_logged = False
	_title = ''
	_menu_ac = ''
	_js = []
	session = None
	view = {}
	
	def __init__(self):
		super(Controller, self).__init__()
		self.session = Session()
		if(self.session.has_key('auth') and self.session['auth'].has_key('acl')):
			self.__user_acl = self.session['auth']['acl']
			self._is_logged = True
	def __check_acl(self):
		if(self.__user_acl < self._acl):
			if self.__user_acl == Acl.GUEST:
				super(Controller, self).redirect(settings.login_url)
			else:
				raise NameError, 'BRAK UPRAWNIEN'
			return False
		return True
	
	# @todo tu by sie przydalo renderowac strone brak uprawnien, czy cus
	def get(self, *kwargs):
		if self.__check_acl():
			self._get(kwargs)
			self.__render()
	
	def post(self):
		if self.__check_acl():
			self._post()
			self.__render()
	
	def set_no_render(self,value):
		self.__no_render = value

	def __render(self):
		if self.__no_render:
			return
		templateName = False
		layoutName = False
		handlerName = self.__class__.__name__.replace('Handler','')
		if hasattr(self,'_template'):
			if(os.path.exists(os.path.join(settings.templates_dir,self._template+'.html'))):
				templateName = self._template.replace('.html','')+'.html'
			else:
				raise NameError, "Brak pliku widoku (template) dla handlera '%s' o nazwie '%s'" % (handlerName, self._template)
		elif(os.path.exists(os.path.join(settings.templates_dir,handlerName.lower()+'.html'))):
			templateName = handlerName.lower()+'.html'
		if False == templateName:
			raise NameError, "Brak pliku widoku (template) dla handlera '%s'" % (handlerName)
		if hasattr(self,'_layout'):
			if(os.path.exists(os.path.join(settings.layouts_dir,self._layout+'.html'))):
				layoutName = self._layout.replace('.html','')+'.html'
			else:
				raise NameError, "Brak pliku layoutu o nazwie '%s' dla handlera '%s'" % (self._layout, handlerName)
		else:
			layoutName = settings.layouts_default
		
		self.view['template_name'] = os.path.join(settings.templates_dir,templateName)
		self.view['template_css'] = settings.css_include
		self.view['template_js'] = settings.js_include
		self.view['auth'] = None
		self.view['is_logged'] = False
		if hasattr(self,'_js'):
			self.view['template_js'] = self.view['template_js'] + self._js
		if hasattr(self,'_css'):
			self.view['template_css'] = self.view['template_css'] + self._css
		if hasattr(self,'_menu_ac'):
			self.view['menu_ac'] = self._menu_ac
		if hasattr(self,'_title'):
			self.view['title'] = self._title
		if settings.title_default:
			self.view['title'] = settings.title_default % (self.view['title'])
		if(self.session.has_key('auth')):
			self.view['auth'] = self.session['auth']
			self.view['is_logged'] = True
		self.response.out.write(template.render(os.path.join(settings.layouts_dir,layoutName), self.view))
		
		
		