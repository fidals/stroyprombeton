from .base import *


DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# http->https change
os.environ['HTTPS'] = 'on'

YANDEX_KASSA_LINK = 'https://money.yandex.ru/eshop.xml'
