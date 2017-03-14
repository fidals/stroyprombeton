from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from wkhtmltopdf.views import PDFTemplateView

from catalog.models import search as filter_
from catalog.views import catalog
from images.models import Image
from pages.models import CustomPage, ModelPage

from stroyprombeton.models import Product, Category
from stroyprombeton.views.helpers import set_csrf_cookie, get_keys_from_post

PRODUCTS_ORDERING = ['code', 'name', 'mark']
PRODUCTS_PER_PAGE = 30


def fetch_products(request):
    """Filter product table on Category page by Name, code, specification."""
    category_id, term, offset, filtered = get_keys_from_post(
        request, 'categoryId', 'term', 'offset', 'filtered',
    )
    term = term.strip()

    category = Category.objects.get(id=category_id)
    products = Product.objects.get_by_category(
        category, ordering=PRODUCTS_ORDERING
    )

    if filtered == 'true' and not term:
        lookups = [
            'name__icontains',
            'code__icontains',
            'mark__icontains',
            'specification__icontains',
        ]
        products = filter_(term, products, lookups, ordering=PRODUCTS_ORDERING)

    offset = int(offset)
    left_product_count = products.count() - offset
    size = left_product_count if left_product_count < PRODUCTS_PER_PAGE else PRODUCTS_PER_PAGE
    products = products.get_offset(offset, size)

    images = Image.objects.get_main_images_by_pages(
        product.page
        for product in products
    )
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
    """Show list of root categories."""
    template_name = 'catalog/catalog.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(parent=None, page__is_active=True)

    def get_context_data(self, **kwargs):
        context = super(CategoryTree, self).get_context_data(**kwargs)
        return {
            **context,
            'page': CustomPage.objects.get(slug='gbi'),
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage, ListView):

    # for catalog.CategoryPage
    related_model_name = Category().related_model_name
    queryset = ModelPage.objects.prefetch_related(related_model_name)
    pk_url_kwarg = 'category_id'
    template_name = 'catalog/category.html'

    # for ListView
    page_kwarg = 'page_index'
    paginate_by = PRODUCTS_PER_PAGE

    def get_object(self, queryset=None):
        category_pk = self.kwargs.get(self.pk_url_kwarg)
        lookup = '{}__id'.format(self.related_model_name)
        return self.queryset.filter(**{lookup: category_pk}).get()

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        self.object_list = (
            Product.objects
            .get_by_category(self.object.model, ordering=PRODUCTS_ORDERING)
            .select_related('page')[PRODUCTS_PER_PAGE:]
        )
        return super(CategoryPage, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CategoryPage, self).get_context_data(**kwargs)
        category = context.get('category')
        page_index = int(self.request.GET.get('page_index', 1))

        products = (
            Product.objects
            .get_by_category(category, ordering=PRODUCTS_ORDERING)
            .select_related('page')
        )

        # here we offsetting products for seo-robots & for users:
        products_offset = products.get_offset(
            PRODUCTS_PER_PAGE * (page_index - 1), PRODUCTS_PER_PAGE
        )

        images = Image.objects.get_main_images_by_pages(
            product.page for product in products_offset
        )
        products_with_images = [
            (product, images.get(product.page))
            for product in products_offset
        ]

        return {
            **context,
            'paginator_links': context['paginator'].page_range,
            'pagination_param': self.page_kwarg,
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
            .get_by_category(product.category)
            .exclude(id=product.id)
            .select_related('page')
        )

        images = Image.objects.get_main_images_by_pages(
            sibling.page for sibling in siblings
        )

        siblings_with_images = [
            (product, images.get(product.page))
            for product in siblings
        ]

        return {
            **context,
            'sibling_with_images': siblings_with_images,
        }


class ProductPDF(PDFTemplateView, DetailView):
    model = Category
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    template_name = 'catalog/product_pdf_price.html'
    filename = 'stb_product_price.pdf'

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super(ProductPDF, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ProductPDF, self).get_context_data(**kwargs)
        category = context[self.context_object_name]

        products = (
            Product.objects
            .get_by_category(category, ordering=PRODUCTS_ORDERING)
            .select_related('page')
        )

        return {
            **context,
            'category': category,
            'products': products,
        }
