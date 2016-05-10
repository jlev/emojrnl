import os
import dj_database_url
from memcacheify import memcacheify

from settings import *

# No debug
DEBUG = False
TEMPLATE_DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')

# Heroku hosted database & cache
DATABASES['default'] = dj_database_url.config()
CACHES = memcacheify(timeout=60 * 60)  # max one hour

# Sendgrid email
EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']

# SSL
SSLIFY_DISABLE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Allowed host headers
ALLOWED_HOSTS = ['emojrnl.herokuapp.com', 'my.emojr.nl']
CORS_ORIGIN_WHITELIST = (
    'emojr.nl',
    'www.emojr.nl'
)
CORS_URLS_REGEX = r'^/api/.*$'

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

import raven
INSTALLED_APPS += ('raven.contrib.django.raven_compat', )
RAVEN_CONFIG = {
    'dsn': 'https://f5b5bab5948b4edeb70b0c7948a1c540:0f19ec120474456a9e3a324ed5203007@app.getsentry.com/77363',
    # 'release': raven.fetch_git_sha(os.path.dirname(__file__)),
}
