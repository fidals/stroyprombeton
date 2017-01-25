from .base import *


DEBUG = False

ALLOWED_HOSTS = ['*']

# http->https change
os.environ['HTTPS'] = 'off'
