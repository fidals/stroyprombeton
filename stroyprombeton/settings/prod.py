from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

# http->https change
TEMPLATE_DEBUG = False
os.environ['HTTPS'] = 'off'

USE_CELERY = True
