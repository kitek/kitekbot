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

class Controller(RequestHandler):
	__no_render = False
	__user_acl = settings.default_acl
	_acl = settings.default_acl_restriction
	_is_logged = False
	_title = 'Devel'
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
	def get(self):
		if self.__check_acl():
			self._get()
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
		self.view['auth'] = None
		self.view['is_logged'] = False
		if hasattr(self,'_title'):
			self.view['title'] = self._title
		if(self.session.has_key('auth')):
			self.view['auth'] = self.session['auth']
			self.view['is_logged'] = True
		self.response.out.write(template.render(os.path.join(settings.layouts_dir,layoutName), self.view))
		
		
		