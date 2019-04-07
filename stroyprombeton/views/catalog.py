from csv import writer as CSVWriter

from django.conf import settings
from django.http import HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from wkhtmltopdf.views import PDFTemplateView

from catalog.views import catalog
from images.models import Image
from pages.models import CustomPage, ModelPage
from pages.templatetags.pages_extras import breadcrumbs as get_page_breadcrumbs
from stroyprombeton import context as stb_context, models, exception, request_data
from stroyprombeton.views.helpers import set_csrf_cookie


def fetch_products(request):
    """Filter product table on Category page by Name, code, specification."""
    try:
        context_ = stb_context.FetchPositions(
            request_data.FetchProducts(request, url_kwargs={}),
        )
    # @todo #451:60m  Create middleware to for http errors. se2
    #  Middleware should transform http exceptions to http errors errors.
    except exception.Http400 as e:
        return HttpResponseBadRequest(str(e))

    return render(
        request,
        'catalog/category_products.html',
        context_.context()
    )


class CSVExportBuffer:
    """Pseudo-buffer that required for streaming csv response."""

    def write(self, value):
        return value


def categories_csv_export(request, filename='categories.csv', breadcrumbs_delimiter=' » '):

    def serialize_categories(categories):
        for category in categories:
            url = settings.BASE_URL + category.get_absolute_url()
            breadcrumbs = get_page_breadcrumbs(category)['crumbs_list']
            breadcrumbs = breadcrumbs_delimiter.join(
                (name for name, url in breadcrumbs)
            )

            yield (
                url, category.name, breadcrumbs
            )

    buf = CSVExportBuffer()
    writer = CSVWriter(buf, delimiter='|')

    categories = serialize_categories(
        models.CategoryPage.objects.active()
    )

    response = StreamingHttpResponse(
        (writer.writerow(c) for c in categories),
        content_type="text/csv",
    )
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    return response


# @todo #556:120m  Show root categories as matrix.
#  We have no mockup for it. Propose your own solution.
#  Currently we have problem with many categories.
#  Screen: http://prntscr.com/n802pt
class CategoryTree(ListView):
    """The list of root categories."""

    template_name = 'catalog/catalog.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return models.Category.objects.active().filter(parent=None)

    def get_context_data(self, **kwargs):
        context = super(CategoryTree, self).get_context_data(**kwargs)
        return {
            **context,
            'page': CustomPage.objects.get(slug='gbi'),
        }


@set_csrf_cookie
class CategoryPage(catalog.CategoryPage):
    pk_url_kwarg = 'category_id'
    related_model_name = models.Category().related_model_name
    queryset = ModelPage.objects.prefetch_related(related_model_name)

    def get_object(self, queryset=None):
        category_pk = self.kwargs.get(self.pk_url_kwarg)
        lookup = '{}__id'.format(self.related_model_name)
        return self.queryset.filter(**{lookup: category_pk}).get()

    def get_context_data(self, **kwargs):
        """Add sorting options and view_types in context."""
        context_ = stb_context.Catalog(
            request_data.Category(self.request, url_kwargs=self.kwargs),
        )

        return {
            **super().get_context_data(**kwargs),
            **context_.context(),
        }


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    queryset = (
        models.Product.objects
        .active()
        .select_related('page')
        .prefetch_related('options')
        .prefetch_related('page__images')
    )

    def get_context_data(self, **kwargs):
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = context[self.context_object_name]

        siblings = product.get_siblings(settings.PRODUCT_SIBLINGS_COUNT)
        images = Image.objects.get_main_images_by_pages(
            sibling.page for sibling in siblings
        )

        siblings_with_images = [
            (product, images.get(product.page))
            for product in siblings
        ]

        product_ancestors = product.page.get_ancestors_fields('name', 'get_absolute_url')
        offset = 1  # "каталог" page
        limit = 3
        product_categories = [
            {'name': name, 'url': url()}
            for (name, url) in product_ancestors[offset:offset + limit]
        ]
        tag_groups = (
            models.Tag.objects
            .filter_by_options(product.options.all())
            .group_tags()
        ).keys()

        return {
            **context,
            'sibling_with_images': siblings_with_images,
            'product_categories': product_categories,
            'tag_groups': tag_groups,
        }


class ProductPDF(PDFTemplateView, DetailView):
    model = models.Category
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
            models.Product.objects
            .active()
            .filter_descendants(category)
            # use `OPTIONS_ORDERING` instead
            # .order_by(*settings.PRODUCTS_ORDERING)
        )

        return {
            **context,
            'category': category,
            'products': products,
        }
