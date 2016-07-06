"""
Stroyprombeton views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from . import config


@ensure_csrf_cookie
def index(request):
    """Main page view"""

    context = {
        'meta': config.page_metadata('main'),
        'href': config.HREFS,
        'shop_info': config.SHOP_INFO
    }

    return render(
        request, 'index/index.html', context)
