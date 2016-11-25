"""STB catalog views."""
from django.shortcuts import render
from django.views.generic.list import ListView

from catalog.models import search as filter_
from catalog.views import catalog

from pages.models import CustomPage
from stroyprombeton.models import Product, Category
from stroyprombeton.views.helpers import set_csrf_cookie, get_keys_from_post


def fetch_products(request):
    """Filter product table on Category page by Name, vendor code, series."""

    size = 30
    category_id, term, offset, filtered = get_keys_from_post(
        request, 'categoryId', 'term', 'offset', 'filtered',
    )

    category = Category.objects.get(id=category_id)
    products = Product.objects.get_products_by_category(category, ordering=('name', 'mark'))

    if filtered == 'true':
        lookups = ['name__icontains', 'code__icontains', 'mark__icontains']
        products = filter_(term, products, lookups, ordering=('name', 'mark'))

    if offset:
        offset = int(offset)
        left_product_count = products.count() - offset
        size = left_product_count if left_product_count < size else size

        products = products.get_offset(offset, size)

    return render(request, 'catalog/category_products.html', {'products': products})


class CategoryTree(ListView):
    """Show list of root categories"""
    template_name = 'catalog/catalog.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent=None, page__is_active=True)

    def get_context_data(self, **kwargs):
        context = super(CategoryTree, self).get_context_data(**kwargs)
        return {
            **context,
            'page': CustomPage.objects.get(slug='gbi')
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    model = Category
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    query_pk_and_slug = 'pk'

    def get_context_data(self, **kwargs):
        context = super(catalog.CategoryPage, self).get_context_data(**kwargs)
        category = context[self.context_object_name]
        products = Product.objects.get_products_by_category(
            category, ordering=('name', 'mark')
        )

        return {
            **context,
            'page': category.page,
            'children': category.get_children(),
            'products': products.get_offset(0, 30),
        }


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    model = Product

    def get_context_data(self, **kwargs):
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = context[self.context_object_name]
        siblings = Product.objects.filter(specification=product.specification).exclude(id=product.id)

        return {
            **context,
            'siblings': siblings
        }
