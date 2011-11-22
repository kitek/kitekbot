#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__ = '0.1'

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import xmpp, datastore_errors
from datetime import datetime
from botModels import Acl,Roster,LogsLogin,Sync,SyncAnswers,GeneralCounterShard,Solution
import logging, md5
from utilities.web import Controller


"""
Logowanie do systemu
URL: /login
"""
class LoginHandler(Controller):
	_acl = Acl.GUEST
	
	def _get(self):
		self.view['info'] = ''
		if self._is_logged:
			super(Controller, self).redirect('/')
		elif (self.request.get('hash')):
			try:
				user = Roster.get(self.request.get('hash'))
				if(user != None):
					self.__init_session(user)
					super(Controller, self).redirect('/')
				else:
					self.view['info'] = 'Błędny login lub hasło.'
			except datastore_errors.BadKeyError:
				self.view['info'] = 'Błędny login lub hasło.'
		
		
	def _post(self):
		if(self.request.get('login') and self.request.get('pass')):
			user = Roster.findByJid(self.request.get('login'))
			
			#user.password = md5.new(self.request.get('pass')).hexdigest()
			#user.acl = Acl.ADMIN
			#user.put()
						
			if user != None and user.password == md5.new(self.request.get('pass')).hexdigest():
				self.session['auth'] = {
					'jid' : user.jid,
					'password' : user.password,
					'acl' : user.acl
				}
				log = LogsLogin(userRef=user)
				log.put()
				super(Controller, self).redirect('/')
			else:
				self.view['info'] = 'Błędny login lub hasło.'
	
	def __init_session(self,user):
		self.session['auth'] = {
			'jid' : user.jid,
			'password' : user.password,
			'acl' : user.acl
		}
		log = LogsLogin(userRef=user)
		log.put()

"""
Wylogowanie z systemu 
URL: /logout
"""
class LogoutHandler(Controller):
	_acl = Acl.GUEST
	def _get(self):
		self.set_no_render(True)
		if self._is_logged:
			self.session.delete()
		super(Controller, self).redirect('/')
	def _post(self):
		self._get()

class SyncHandler(Controller):
	_acl = Acl.MEMBER
	_title = 'Ostatnio przeprowadzone synchronizacje'
	_limit = 10
	
	def _get(self):
		self.view['lastSync'] = []
		self.view['ile'] = self._limit
		
		lastSync = Sync.all()
		lastSync.order('-__key__')
		lastSync = lastSync.fetch(10)
		if len(lastSync) > 0:
			ids = ''
			for item in lastSync:
				ids+=str(item.key().id())+','
			query = SyncAnswers.gql("WHERE syncId IN (%s)" % (ids[0:-1]))
			wynik = query.fetch(100)
			
			odp = {}
			liczniki = {}
			if len(wynik) > 0:
				for i in wynik:
					if False == odp.has_key(int(i.syncId)):
						odp[int(i.syncId)] = []
						liczniki[int(i.syncId)] = {'za':0,'przeciw':0}
					odp[int(i.syncId)].append({'jid':i.jid,'syncCmd':i.syncCmd})
					if(True == i.syncCmd):
						liczniki[int(i.syncId)]['za']+=1
					else:
						liczniki[int(i.syncId)]['przeciw']+=1
			self.view['answers'] = odp
			for item in lastSync:
				if False == liczniki.has_key(int(item.key().id())):
					liczniki[int(item.key().id())] = {'za':0,'przeciw':0}
				self.view['lastSync'].append({
					'id':item.key().id(),
					'jid':item.jid,
					'created':item.created,
					'done':item.done,
					'files':item.files,
					'za' : liczniki[int(item.key().id())]['za'],
					'przeciw' : liczniki[int(item.key().id())]['przeciw']
				})
			self.view['liczniki'] = liczniki
			

class SolutionsHandler(Controller):
	_acl = Acl.MEMBER
	_title = 'Solutions'
	
	def _get(self):
		self.view['solution_list'] = []
		solutions  = Solution.all()
		solutions.order('-__key__')
		solutions = solutions.fetch(50)
		if len(solutions) > 0:
			for i in solutions:
				self.view['solution_list'].append({
					'id' : i.key().id(),
					'title' : i.title
				})
	def _post(self):
		pass
	
class SolutionHandler(Controller):
	_acl = Acl.MEMBER
	_title = 'Solution'
	
	def _get(self):
		id = int(self.request.url.split('/')[-1])
		self.view['solution_id'] = id
		self.view['solution'] = {}
		if id > 0:
			solution = Solution.get_by_id(id)
			if solution != None:
				self.view['solution'] = {
					'title':solution.title,
					'body':solution.body,
					'created':solution.created,
					'jid':solution.author.jid,
					'language':solution.language
				}
				return True
		super(Controller, self).redirect('/solutions')
		return False
	def _post(self):
		pass
	
class SolutionsAddHandler(Controller):
	_acl = Acl.MEMBER
	_title = 'Dodaj solucję'
	_post = {'title':'','body':'','language':2}
	
	def _get(self):
		pass
	def _post(self):
		self.view['errors'] = {}
		if self._validate():
			solution = Solution(title=self._post['title'],body=self._post['body'],author=Roster.findByJid(self.session['auth']['jid']),language=int(self._post['language']))
			solution.put()
			super(Controller, self).redirect('/solutions/%s' % (solution.key().id()))
		self.view['post'] = self._post
		
	def _validate(self):
		title = self.request.get('title')
		body = self.request.get('body')
		language = self.request.get('language')
		
		if len(title) < 5:
			self.view['errors']['title'] = 'Tytuł jest za krótki. Min to 5 znaków.'
		if len(body) < 5:
			self.view['errors']['body'] = 'Kod jest za krótki. Min to 5 znaków.'
		
		self._post = {'title':title,'body':body,'language':language}
		return len(self.view['errors']) == 0

class WebHandler(Controller):
	_template = 'index'
	def _get(self):
		
		pass
		
	def _post(self):
		pass