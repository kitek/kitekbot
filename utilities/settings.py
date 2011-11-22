#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from botModels import Acl


templates_dir = os.path.join(os.path.dirname(__file__), '..', 'templates') # Katalog z plikami template'ów
layouts_dir = os.path.join(os.path.dirname(__file__), '..', 'templates','layouts') # Katalog z plikami layout'ów
layouts_default = 'layout.html'

# zmienic nazwe na acl_
default_acl = Acl.GUEST # Domyślna rola ACL
default_acl_restriction = Acl.MEMBER # Domyślna wymagana rola ACL

login_url = '/login' # URL do strony z logowaniem

css_url = '/css/'
css_include = ['main.css']

# Configuration settings for the session class.
session = {    
    "COOKIE_NAME": "auth",
    "DEFAULT_COOKIE_PATH": "/",
    "DEFAULT_COOKIE_DOMAIN": False, # Set to False if you do not want this value
                                    # set on the cookie, otherwise put the
                                    # domain value you wish used.
    "SESSION_EXPIRE_TIME": 7200,    # sessions are valid for 7200 seconds
                                    # (2 hours)
    "INTEGRATE_FLASH": False,        # integrate functionality from flash module?
    "SET_COOKIE_EXPIRES": True,     # Set to True to add expiration field to
                                    # cookie
    "WRITER":"datastore",           # Use the datastore writer by default. 
                                    # cookie is the other option.
    "CLEAN_CHECK_PERCENT": 50,      # By default, 50% of all requests will clean
                                    # the datastore of expired sessions
    "CHECK_IP": True,               # validate sessions by IP
    "CHECK_USER_AGENT": True,       # validate sessions by user agent
    "SESSION_TOKEN_TTL": 5,         # Number of seconds a session token is valid
                                    # for.
    "UPDATE_LAST_ACTIVITY": 60,     # Number of seconds that may pass before
                                    # last_activity is updated
}

# Configuration settings for the cache class
cache = {
    "DEFAULT_TIMEOUT": 3600, # cache expires after one hour (3600 sec)
    "CLEAN_CHECK_PERCENT": 50, # 50% of all requests will clean the database
    "MAX_HITS_TO_CLEAN": 20, # the maximum number of cache hits to clean
}

# Configuration settings for the flash class
flash = {
    "COOKIE_NAME": "appengine-utilities-flash",
}

# Configuration settings for the paginator class
paginator = {
    "DEFAULT_COUNT": 10,
    "CACHE": 10,
    "DEFAULT_SORT_ORDER": "ASC",
}

rotmodel = {
    "RETRY_ATTEMPTS": 3,
    "RETRY_INTERVAL": .2,
}
if __name__ == "__main__":
    print "Hello World";

