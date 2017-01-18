from django.shortcuts import render
from django.views.generic.list import ListView

from catalog.models import search as filter_
from catalog.views import catalog
from pages.models import CustomPage, ModelPage
from images.models import Image

from stroyprombeton.models import Product, Category
from stroyprombeton.views.helpers import set_csrf_cookie, get_keys_from_post


def fetch_products(request):
    """Filter product table on Category page by Name, vendor code, series."""
    size = 30
    category_id, term, offset, filtered = get_keys_from_post(
        request, 'categoryId', 'term', 'offset', 'filtered',
    )

    category = Category.objects.get(id=category_id)
    products = Product.objects.get_by_category(category, ordering=('name', 'mark'))

    if filtered == 'true':
        lookups = ['name__icontains', 'code__icontains', 'mark__icontains']
        products = filter_(term, products, lookups, ordering=('name', 'mark'))

    if offset:
        offset = int(offset)
        left_product_count = products.count() - offset
        size = left_product_count if left_product_count < size else size

        products = products.get_offset(offset, size)

    images = Image.objects.get_main_images_by_pages(product.page for product in products)

    products_with_images = [
        (product, images.get(product.page))
        for product in products
    ]

    return render(
        request,
        'catalog/category_products.html',
        {'products_with_images': products_with_images}
    )


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
    related_model_name = Category().related_model_name
    queryset = ModelPage.objects.prefetch_related(related_model_name)
    pk_url_kwarg = 'category_id'
    template_name = 'catalog/category.html'

    def get_object(self, queryset=None):
        category_pk = self.kwargs.get(self.pk_url_kwarg)
        lookup = '{}__id'.format(self.related_model_name)
        return self.queryset.filter(**{lookup: category_pk}).get()

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)
        category = context.get('category')

        products = (
            Product.objects
                .get_by_category(category, ordering=('name', 'mark'))
                .select_related('page')
                .get_offset(0, 30)
        )

        images = Image.objects.get_main_images_by_pages(product.page for product in products)

        products_with_images = [
            (product, images.get(product.page))
            for product in products
        ]

        return {
            **context,
            'products_with_images': products_with_images,
        }


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    queryset = Product.objects.select_related('page').prefetch_related('page__images')

    def get_context_data(self, **kwargs):
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = context[self.context_object_name]

        siblings = (
            Product.objects
                .filter(specification=product.specification)
                .exclude(id=product.id)
                .select_related('page')
        )

        images = Image.objects.get_main_images_by_pages(sibling.page for sibling in siblings)

        siblings_with_images = [
            (product, images.get(product.page))
            for product in siblings
        ]

        return {
            **context,
            'sibling_with_images': siblings_with_images
        }
