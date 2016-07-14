"""
Stroyprombeton views.

NOTE: They all should be 'zero-logic'.
All logic should be located in respective applications.
"""

from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from . import config
from catalog.views import catalog
from stroyprombeton.models import Category, Product

set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')


class CategoryTree(catalog.CategoryTree):
    """Override model attribute to STB-specific Category."""
    model = Category


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    """
    Override model attribute to STB-specific Category.

    Extend get_object and get_context_data.
    """
    model = Category
    url_lookup_field = 'category_id'
    db_lookup_field = 'id'

    def get_context_data(self, **kwargs):
        """Extend method. Use new get_object method."""
        context = super(CategoryPage, self).get_context_data(**kwargs)
        templates = {True: 'catalog/category_table.html',
                     False: 'catalog/category_tile.html'}

        self.template_name = templates.get(context['category'].is_leaf_node())

        return context


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    """Override model attribute to STB-specific Product."""
    model = Product


### STB-specific views ###


@ensure_csrf_cookie
def index(request):
    """Main page view"""

    context = {
        'meta': config.page_metadata('main'),
        'href': config.HREFS,
        'shop_info': config.SHOP_INFO
    }

    return render(
        request, 'index/index.html', context)


@ensure_csrf_cookie
def visual_page(request):
    """Visual page view with Products catalog with images"""

    context = {
    }

    return render(
        request, 'catalog/visual.html', context)


def blog_news_list(request):
    """News page view"""

    context = {
    }

    return render(request, 'blog/news_list.html', context)


def blog_news_item(request):
    """News page view"""

    context = {
    }

    return render(request, 'blog/news_item.html', context)


def blog_post_item(request):
    """Blog post page view"""

    context = {
    }

    return render(request, 'blog/post_item.html', context)


def order_page(request):
    """Order page view with table of Products"""

    context = {
    }

    return render(request, 'ecommerce/order.html', context)
