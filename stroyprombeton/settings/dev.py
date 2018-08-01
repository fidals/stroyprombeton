from os import environ

from .base import *


DEBUG = True

ALLOWED_HOSTS = ['*']

# http://bit.ly/sorl-thumbnail-docs
# to suppress tests failings. Tests have no static
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = False

SITE_DOMAIN_NAME = 'stage.stroyprombeton.ru'

USE_CELERY = False

def show_toolbar(request):
    # Display debug toolbar when running on development config
    # With exception for test environment
    return not environ.get('TEST_ENV', False)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': show_toolbar,
}

SELENIUM_URL = os.environ.get('SELENIUM_URL', 'http://selenium:4444/wd/hub')
SELENIUM_WAIT_SECONDS = int(os.environ['SELENIUM_WAIT_SECONDS'])
SELENIUM_TIMEOUT_SECONDS = int(os.environ['SELENIUM_TIMEOUT_SECONDS'])
