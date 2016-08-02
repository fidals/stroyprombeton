from django import template

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


@register.assignment_tag
def get_roots():
    return Category.objects.root_nodes().filter(is_active=True).order_by('position', 'name')

