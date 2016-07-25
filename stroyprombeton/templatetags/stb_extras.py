from django import template

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
def show_if_exist(value, default=''):
    return value if value else default
