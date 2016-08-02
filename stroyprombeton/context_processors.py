from stroyprombeton.config import SITE_INFO


def site_info(request):
    """
    Injects shop dict into request.

    Shop dict contains information about shop:
    emails, phones, API-integrations.
    """
    return {'site_info': SITE_INFO}
