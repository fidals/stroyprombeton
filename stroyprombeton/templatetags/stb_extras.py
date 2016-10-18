from django import template

from images.models import ImageMixin

from stroyprombeton.models import Category

register = template.Library()


@register.inclusion_tag('tags/product_values.html')
def show_field_if_exist(value, title):
    return {
        'title': title,
        'value': value
    }


@register.inclusion_tag('tags/customer_info.html')
def customer_info(value, title):
    return {
        'title': title,
        'value': value
    }


@register.inclusion_tag('tags/search_result.html')
def search_result(items, type_):
    return {
        'items': items,
        'type_': type_
    }


@register.filter
def format_price(price):
    if price:
        return str(price) + ' руб.'
    else:
        return 'По запросу'


@register.simple_tag
def get_root_categories():
    return Category.objects.root_nodes().filter(page__is_active=True).order_by('position', 'name')


# Not good code, but duker at 06/10/2016 don't know how to fix it.
# It makes Image model very complex.
@register.simple_tag
def get_img_alt(entity: ImageMixin):
    product_alt = 'Фотография {}'
    logo_alt = 'Логотип компании Shopelectro'

    if not hasattr(entity, 'images') or not entity.images.all():
        return logo_alt

    # try one of this attributes to get pages name
    name_attrs = ['h1', 'title', 'name']
    entity_name = next(
        filter(None, (getattr(entity, attr, None) for attr in name_attrs)))
    return product_alt.format(entity_name)
