import re

from django import template
from django.conf import settings
from django.template.defaultfilters import floatformat

from images.models import ImageMixin
from pages.models import Page
from stroyprombeton import models as stb_models

register = template.Library()


# don't put it in the settings.
# because it's temporary UI decision
TOP_MENU_EXAMPLES_COUNT = 7


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


@register.filter
def format_price(price):
    if price:
        return floatformat(price, 0) + ' руб'
    else:
        return 'По запросу'


@register.simple_tag
def get_top_menu_categories():
    return (
        stb_models.Category.objects
        .bind_fields()
        .active()
        .filter(level=1)
        .order_by('page__position', 'name')
        [:TOP_MENU_EXAMPLES_COUNT]
    )


@register.simple_tag
def get_top_menu_series():
    return (
        stb_models.Series.objects
        .bind_fields()
        .exclude_empty()
        .order_by('page__position', 'name')
        [:TOP_MENU_EXAMPLES_COUNT]
    )


@register.simple_tag
def get_top_menu_sections():
    return (
        stb_models.Section.objects
        .bind_fields()
        .exclude_empty()
        .order_by('page__position', 'name')
        [:TOP_MENU_EXAMPLES_COUNT]
    )


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


# @todo #500:60m  Improve tags table performance clearly.
#  Drop `get_tag_name` template tag. It spawns O(n) queries to DB.
#  Prepare tags structure at the view side instead.
#  This approach requires just few queries.
@register.simple_tag
def get_tag_name(group, option) -> str:
    tag = stb_models.Tag.objects.filter(group=group, options__in=[option]).first()
    return tag.name if tag else ''


@register.filter
def remove_specification(value, specification):
    replace_pattern = '. {}'.format(specification)
    return value.replace(replace_pattern, '')


@register.filter
def get_objects_attributes(objects, attribute='name:3') -> str:
    try:
        attribute, count = attribute.split(':')
        count = int(count)
    except ValueError:
        count = None
    values = list(
        set(
            filter(
                None,
                map(
                    lambda x: remove_specification(x[0], x[1]) if x[1] else x[0],
                    map(
                        lambda x: (getattr(x, attribute, None), x.specification),
                        objects
                    )
                )
            )
        )
    )

    if count:
        values = values[:count]

    return ', '.join(values)


def parse_page_metadata(content: str, delimiter_pattern=r'[\-]{3,}') -> (dict, str):
    """
    Parse metadata.

    Return dictionary with metadata extracted from content and content body
    without metadata headers.
    For example: {'delivery-time': 'Август, 2014'}
    """
    metadata = {}

    if not content:
        return {}, content

    delimiter_span = re.search(delimiter_pattern, content)

    if not delimiter_span:
        return {}, content

    delimiter_start, delimiter_end = delimiter_span.span(0)

    header_lines = (line.strip() for line in content[:delimiter_start].splitlines())
    for line in header_lines:
        key, value = line.split(':')
        metadata[key.strip()] = value.strip()

    return metadata, content[delimiter_end + 1:]


@register.filter
def get_page_metadata(content: str) -> dict:
    metadata, cleaned_content = parse_page_metadata(content)
    return {
        'metadata': metadata,
        'cleaned_content': cleaned_content,
    }


@register.filter
def get_category_gent_name(category: stb_models.Category, default=None) -> str:
    return settings.CATEGORY_GENT_NAMES.get(
        category.id, category.name if not default else default
    )
