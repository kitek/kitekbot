# -*- coding: utf-8 -*-
#!/usr/bin/env python

import webapp2
from webapp2_extras import jinja2
import logging

class BaseController(webapp2.RequestHandler):
	template = ''
	layout = 'layouts/layout.html'
	title = ''
	view = {}
	def __init__(self, request, response):
		# Set self.request, self.response and self.app.
		self.initialize(request, response)
	@webapp2.cached_property
	def jinja2(self):
		return jinja2.get_jinja2(app=self.app)
	def render(self):
		# Try use default template based on controller name
		if not self.template:
			self.template = type(self).__name__.replace('Controller','').lower()+'.html'
		self.view['_template'] = self.template
		self.view['title'] = self.title
		rv = self.jinja2.render_template(self.layout, **self.view)
		self.response.write(rv)
	def dispatch(self):
		try:
			# Dispatch the request.
			webapp2.RequestHandler.dispatch(self)
			self.render()
		finally:
			pass