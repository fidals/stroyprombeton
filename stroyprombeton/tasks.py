from __future__ import absolute_import, unicode_literals

from django.core.management import call_command

from stroyprombeton.celery import app


@app.task
def update_prices():
    call_command('price')
    print('Generate prices complete.')
    call_command('collectstatic', '--no-input')
