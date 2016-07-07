"""
Stroyprombeton views.

NOTE: They all should be 'zero-logic'.
All logic should live in respective applications.
"""

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from . import config


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
def product_page(request):
    """Product page view"""

    context = {
    }

    return render(
        request, 'catalog/product.html', context)


@ensure_csrf_cookie
def visual_page(request):
    """Visual page view with Products catalog with images"""

    context = {
    }

    return render(
        request, 'catalog/visual.html', context)


@ensure_csrf_cookie
def catalog_page(request):
    """Catalog page view with all categories list"""

    context = {
    }

    return render(
        request, 'catalog/catalog.html', context)


@ensure_csrf_cookie
def category_tile_page(request):
    """Category page view with tile of subcategories"""

    context = {
    }

    return render(
        request, 'catalog/category_tile.html', context)


@ensure_csrf_cookie
def category_table_page(request):
    """Category page view with table of Products"""

    context = {
    }

    return render(
        request, 'catalog/category_table.html', context)


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
