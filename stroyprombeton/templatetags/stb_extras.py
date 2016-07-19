from django import template

register = template.Library()


@register.inclusion_tag('tags/product_values.html')
def show_if_exist(value, title):
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
