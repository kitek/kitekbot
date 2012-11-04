# -*- coding: utf-8 -*-
#!/usr/bin/env python

import logging

class Acl(object):
	""" Klasa implementująca dostępne uprawnienia. """
	roles = {'user':1, 'admin': 2, 'owner': 3}

	@staticmethod
	def getRoles():
		""" Zwraca listę dostępnych w systemie poziomy uprawnień. """
		return Acl.roles.keys()

	@staticmethod
	def isAllowed(user, role):
		""" Sprawdza czy user posiada odpowiednie uprawnienia. """
		if False == Acl.roles.has_key(user.aclRole):
			logging.error('Passed user.aclRole "%s" is incorrect.' % (user.aclRole))
			return False
		if False == Acl.roles.has_key(role):
			logging.error('Passed role "%s" is incorrect.' % (role))
			return False
		if Acl.roles[user.aclRole] >= Acl.roles[role]:
			return True
		return False

		