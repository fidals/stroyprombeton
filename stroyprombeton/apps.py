from django.apps import AppConfig
from django.core.checks import Error, register
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from stroyprombeton import celery_app


class StroyprombetonAppConfig(AppConfig):
    name = 'stroyprombeton'
    verbose_name = _('Stroyprombeton')


@register()
def rabbitmq_availability(app_configs, **kwargs):
    if not settings.USE_CELERY:
        return []

    active_queues = celery_app.control.inspect().active_queues()
    declared_queues = celery_app.conf.task_queues
    return [
        Error(
            f'Worker for the queue isn\'t available.',
            hint=f'Run a worker for the queue before launching the application.',
            obj=dq,
        ) for dq in declared_queues
        if not any(
            dq.name in aq[0]['name']
            for aq in active_queues.values()
            if aq
        )
    ]
