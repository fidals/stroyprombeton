from django import template
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
        'link': link,
    }


@register.inclusion_tag('tags/customer_info.html')
def customer_info(value, title):
    return {
        'title': title,
        'value': value,
    }


@register.inclusion_tag('tags/search_result.html')
def search_result(items, item_type):
    return {
        'items': items,
        'item_type': item_type,
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


@register.simple_tag
def get_product_field(product_id, parameter):
    product = Product.objects.get(id=product_id)

    return getattr(product, parameter)


@register.filter
def remove_specification(value, specification):
    replace_pattern = '. {}'.format(specification)
    return value.replace(replace_pattern, '')


def parse_page_metadata(content: str, delimiter='---') -> (dict, str):
    """
    Returns dictionary with metadata extracted from content
    (for example {'delivery-time': 'Август, 2014'))
    and content body without metadata headers
    """
    metadata = {}
    content_begins_with_line = 0
    content_lines = [line.strip() for line in content.splitlines()]

    if (not content_lines or content_lines[0] != delimiter):
        # First line doesn't contain "magic" metadata dashes -> page doesn't have metadata at all
        return {}, content

    for i, line in enumerate(content_lines[1:]):
        if line == delimiter:
            content_begins_with_line = i
            break
        else:
            key, value = line.split(':')
            metadata[key.strip()] = value.strip()

    return metadata, '\n'.join(
        # +2 because we have two "magical dashes":
        # 1. at beginning of the content
        # 2. at the end of metadata header
        content_lines[content_begins_with_line + 2:]
    )


@register.filter
def get_page_metadata(content: str) -> dict:
    metadata, cleaned_content = parse_page_metadata(content)
    return {
        'metadata': metadata,
        'cleaned_content': cleaned_content,
    }
