from .base import *


DEBUG = True

ALLOWED_HOSTS = ['*']

# http://bit.ly/sorl-thumbnail-docs
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = True

SITE_DOMAIN_NAME = 'stage.stroyprombeton.ru'

USE_CELERY = False


"""
    @todo #106 Включить в dev-среде django-debug-toolbar по-умолчанию
      Но в CI его нужно отключать, т.к. возникают ошибки

      def show_toolbar(request):
          # Always display debug toolbar when running on development config
          return True

      DEBUG_TOOLBAR_CONFIG = {
          'SHOW_TOOLBAR_CALLBACK': show_toolbar,
      }

"""
