from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from pages.models import Page

from stroyprombeton.models import Product, Category


# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')

MODEL_MAP = {
    'product': Product.objects.filter(
        page__is_active=True,
    ),
    'category': Category.objects.filter(
        page__is_active=True,
    ),
    'page': Page.objects.filter(is_active=True),
}


def get_keys_from_post(request, *args):
    """Get a list of given keys from request.POST object."""
    return [request.POST.get(arg) for arg in args]
