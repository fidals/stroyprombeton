from django.conf import settings


def site_info(request):
    """
    Inject shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {
        'site_info': settings.SITE_INFO,
        'base_url': settings.BASE_URL,
        'DEBUG': settings.DEBUG,
    }
