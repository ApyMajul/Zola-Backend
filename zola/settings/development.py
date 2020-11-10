
from sys import stdout
from os import getenv, environ
from pathlib import Path

from zola.settings.base import *

DEBUG = True

# ALLMECEN_ENVIRONMENT = environ.get('AMCENV', 'development')

PAGE_CACHE_SECONDS = 1

ALLOWED_HOSTS = [
    'localhost'
]

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3001',
]

WEBPACK = {
    'dev_server': True,
    'url': 'http://localhost',
    'port': 3001,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(PARENT_DIR / 'db.sqlite'),
    }
}

# LOGGING =

GRAPHQL_JWT['JWT_EXPIRATION_DELTA'] = timedelta(hours=12)

# ############ Storage ########################

MEDIA_ROOT = PARENT_DIR / 'medias'
Path(MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
MEDIA_URL = '/medias/'

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    SRC_DIR / 'static',
]

