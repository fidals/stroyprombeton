from django import template

register = template.Library()


@register.inclusion_tag('product_values.html')
def show_if_exist(value, title):
        return {
            'title': title,
            'value': value
        }
