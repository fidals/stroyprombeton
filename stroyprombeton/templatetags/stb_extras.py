from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.defaultfilters import floatformat

from images.models import ImageMixin
from pages.models import Page

from stroyprombeton.models import Category, Product

register = template.Library()


@register.inclusion_tag('tags/product_values.html')
def show_field_if_exist(value, title, link=None):
    return {
        'title': title,
        'value': value,
        'link': link
    }


@register.inclusion_tag('tags/customer_info.html')
def customer_info(value, title):
    return {
        'title': title,
        'value': value
    }


@register.inclusion_tag('tags/search_result.html')
def search_result(items, item_type):
    return {
        'items': items,
        'item_type': item_type
    }


@register.inclusion_tag('tags/order_form_field_error.html')
def order_form_field_error(errors):
    return {
        'errors': errors
    }


@register.filter
def format_price(price):
    if price:
        return floatformat(price, 0) + ' руб.'
    else:
        return 'По запросу'


@register.simple_tag
def get_root_categories():
    return (Category.objects.root_nodes().filter(page__is_active=True)
            .order_by('page__position', 'name'))


# Not good code, but duker at 06/10/2016 don't know how to fix it.
# It makes Image model very complex.
@register.simple_tag
def get_img_alt(entity: ImageMixin):
    product_alt = 'Фотография {}'
    logo_alt = 'Логотип компании Shopelectro'

    if not isinstance(entity, Page):
        return logo_alt

    # try one of this attributes to get pages name
    name_attrs = ['h1', 'title', 'name']
    entity_name = next(
        filter(None, (getattr(entity, attr, None) for attr in name_attrs)))
    return product_alt.format(entity_name)


# TODO - move it in pages. Inspired by LP electric
@register.simple_tag
def full_url(url_name, *args):
    return settings.BASE_URL + reverse(url_name, args=args)


@register.simple_tag
def get_product_field(product_id, parameter):
    product = Product.objects.get(id=product_id)

    return getattr(product, parameter)
