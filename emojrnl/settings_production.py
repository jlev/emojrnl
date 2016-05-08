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
SSLIFY_DISABLE = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Allowed host headers
ALLOWED_HOSTS = ['emojrnl.herokuapp.com', 'my.emojr.nl']

# Twilio
DJANGO_TWILIO_FORGERY_PROTECTION = False

# Static asset configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# import raven

# RAVEN_CONFIG = {
#     'dsn': 'https://hash@app.getsentry.com/id',
# }
