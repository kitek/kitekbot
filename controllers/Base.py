# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging
import webapp2
from webapp2_extras import jinja2
from google.appengine.api import users
from models.Users import Users
from library.Acl import Acl
from models.UsersSettings import UsersSettings


class BaseController(webapp2.RequestHandler):
	template = ''
	layout = 'layouts/layout.html'
	title = ''
	view = {}
	activeTab = 'index'
	aclRole = 'user'
	currentUser = None
	def __init__(self, request, response):
		# Set self.request, self.response and self.app.
		self.initialize(request, response)
		
	@webapp2.cached_property
	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)
	def render(self):
		self.view['title'] = self.title
		# Try use default template based on controller name
		if not self.template:
			self.template = type(self).__name__.replace('Controller','').lower()+'.html'
		self.view['_template'] = self.template
		self.view['_activeTab'] = self.activeTab
		rv = self.jinja2.render_template(self.layout, **self.view)
		self.response.write(rv)
	def dispatch(self):
		googleUser = users.get_current_user()
		self.view['logoutURL'] = users.create_logout_url("/")
		if not googleUser:
			self.forbidden()
			return
		# Sprawdz czy user jest w bazie
		self.currentUser = Users.getByJid(googleUser.email())
		if None == self.currentUser:
			# Jeżeli jest to administrator to utworz konto i wpuść dalej
			if users.is_current_user_admin():
				Users(key_name=googleUser.email(), aclRole='admin').put()
				UsersSettings.setupDefaults(googleUser.email())
				self.currentUser = Users.getByJid(googleUser.email())
			else:
				self.forbidden()
				return
		# Check ACL cefore dispatch
		if False == Acl.isAllowed(self.currentUser, self.aclRole):
			self.forbidden()
			return
		self.view['_currentUser'] = self.currentUser
		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
			self.render()
		finally:
			pass
	def forbidden(self):
		self.template = 'layouts/forbidden.html'
		self.view['logoutURL'] = users.create_logout_url("/")
		self.render()

