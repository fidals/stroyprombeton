from django.conf import settings


def site_info(request):
    return {
        'site_info': settings.SITE_INFO,
        'base_url': settings.BASE_URL,
        'DEBUG': settings.DEBUG,
        'tags_ui_limit': settings.TAGS_UI_LIMIT,
    }
