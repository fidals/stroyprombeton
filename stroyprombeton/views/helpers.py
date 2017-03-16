from django.db.models import F, Value, CharField
from django.db.models.functions import Concat
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from pages.models import Page

from stroyprombeton.models import Product, Category


# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')

MODEL_MAP = {
    'product': Product.objects.annotate(
        search_field=Concat(
            F('name'), Value(' '),
            F('mark'), Value(' '),
            F('specification'),
            output_field=CharField(),
        )
    ),
    'category': Category,
    'page': Page,
}


def get_keys_from_post(request, *args):
    """Get a list of given keys from request.POST object."""

    return [request.POST.get(arg) for arg in args]
