import typing
from collections import defaultdict
from csv import writer as CSVWriter
from operator import attrgetter

from django import http
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from wkhtmltopdf.views import PDFTemplateView

from catalog import context
from catalog.views import catalog
from images.models import Image
from pages import context as pages_context
from pages.models import CustomPage, ModelPage
from pages.templatetags.pages_extras import breadcrumbs as get_page_breadcrumbs
from stroyprombeton import context as stb_context, models, exception, request_data
from stroyprombeton.views.helpers import set_csrf_cookie


def fetch_products(request):
    """Filter product table on Category page by Name, code, specification."""
    try:
        context_ = stb_context.FetchOptions(
            request_data.FetchProducts(request, url_kwargs={}),
        )
    # @todo #451:60m  Create middleware to for http errors. se2
    #  Middleware should transform http exceptions to http errors errors.
    except exception.Http400 as e:
        return http.HttpResponseBadRequest(str(e))

    return render(request, 'catalog/options.html', context_.context())


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

    response = http.StreamingHttpResponse(
        (writer.writerow(c) for c in categories),
        content_type="text/csv",
    )
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)

    return response


class CategoryMatrix(ListView):
    """The list of root categories."""

    template_name = 'catalog/catalog.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return (
            models.Category.objects
            .bind_fields()
            .active()
            .filter(parent=None)
            .order_by('page__position', 'name')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        lookup = f'{self.related_model_name}__id'
        return get_object_or_404(self.queryset.filter(**{lookup: category_pk}))

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
    ANCESTORS_LABELS = ['Тип изделия', 'класс', 'вид']

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

        siblings_count = settings.PRODUCT_SIBLINGS_COUNT
        sibling_options = (
            models.Option.objects
            .filter(series__in=(
                product.options.active()
                .values_list('series__id', flat=True))
            )
        )
        # @todo #656:60m  Create tests for product siblings.
        siblings = sorted(
            set([o.product for o in sibling_options][:siblings_count]),
            key=attrgetter('name')
        )

        images = Image.objects.get_main_images_by_pages(
            sibling.page for sibling in siblings
        )

        siblings_with_images = [
            (product, images.get(product.page))
            for product in siblings
        ]

        offset = 1  # "каталог" page
        limit = 3
        ancestors_qs = (
            product.category
            .get_ancestors(include_self=True)
            .active()
            [offset:offset + limit]
        )
        ancestor_pairs = [
            (label, category)
            for label, category in zip(self.ANCESTORS_LABELS, ancestors_qs)
        ]
        tag_groups = (
            models.Tag.objects
            .filter_by_options(product.options.all())
            .group_tags()
        ).keys()
        options = product.options.all().order_by(*settings.OPTIONS_ORDERING)

        return {
            **context,
            'sibling_with_images': siblings_with_images,
            'ancestor_pairs': ancestor_pairs,
            'tag_groups': tag_groups,
            'options': options,
        }


class ProductPDF(PDFTemplateView, DetailView):
    model = models.Category
    context_object_name = 'category'
    pk_url_kwarg = 'category_id'
    template_name = 'catalog/product_pdf_price.html'
    filename = 'stb_product_price.pdf'

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context_ = super().get_context_data(**kwargs)
        category = context_[self.context_object_name]

        options_ = stb_context.options.CategoryFiltered(
            stb_context.options.All(),
            category
        )
        grouped_tags = context.tags.GroupedTags(
            tags=stb_context.TagsByOptions(
                stb_context.tags.All(),
                options_.qs(),
            )
        )

        return {
            **context_,
            **pages_context.Contexts([
                options_, grouped_tags,
            ]).context(),
            'category': category,
        }


def series_matrix(request, page='series'):
    def partition_(items: list, columns: int) -> typing.Collection[list]:
        """Partition items to the columns by given columns count."""
        result = defaultdict(list)
        column_length = len(items) // columns + 1
        for i, e in enumerate(items):
            result[i // column_length].append(e)
        return result.values()

    columns = settings.SERIES_MATRIX_COLUMNS_COUNT
    page = CustomPage.objects.get(slug=page)
    series = (
        models.Series.objects.bind_fields()
        .exclude_empty()
        .order_by('name')
    )
    return render(
        request,
        'catalog/matrix.html',
        {
            'page': page,
            'parted_items': partition_(series, columns),
        }
    )


# waiting for #631 to avoid code doubling between series and sections
def sections_matrix(request, page='sections'):
    def partition_(items: list, columns: int) -> typing.Collection[list]:
        """Part items to the columns by given columns count."""
        result = defaultdict(list)  # Ignore CPDBear
        column_length = len(items) // columns + 1
        for i, e in enumerate(items):
            result[i // column_length].append(e)
        return result.values()

    columns = settings.SECTIONS_MATRIX_COLUMNS_COUNT
    page = CustomPage.objects.get(slug=page)
    sections = (
        models.Section.objects.bind_fields()
        .exclude_empty()
        .order_by('name')
    )
    return render(
        request,
        'catalog/matrix.html',
        {
            'page': page,
            'parted_items': partition_(sections, columns),
        }
    )


def series(request, series_slug: str):
    series = get_object_or_404(models.Series.objects, slug=series_slug)
    options = series.options.active()
    # @todo #619:60m  Prevent code doubling in series views.
    #  Now series and series_matrix have doubled code.
    #  Possible solutions:
    #  - Use only one view for series and series+category. As category page does
    #  - Use view context system. Category view does it too.
    #  Those solutions don't except each other.
    images = context.products.ProductImages(
        set([o.product for o in options]), Image.objects.all()
    )
    if not options:
        raise http.Http404('<h1>В секции нет изделий</h1')
    return render(
        request,
        'catalog/series.html',
        {
            **images.context(),
            'products': options,
            'page': series.page,
        }
    )


def section(request, section_slug: str):
    section = get_object_or_404(models.Section.objects, page__slug=section_slug)
    products = section.products.active()
    images = context.products.ProductImages(
        products, Image.objects.all()
    )
    if not products:
        raise http.Http404('<h1>В секции нет изделий</h1')
    return render(
        request,
        'catalog/section.html',
        {
            **images.context(),
            'products': products,
            'page': section.page,
        }
    )


def series_by_category(request, series_slug: str, category_id: int):
    series = get_object_or_404(models.Series.objects, slug=series_slug)
    category = get_object_or_404(models.Category.objects, id=category_id)
    options = (
        models.Option.objects
        .bind_fields()
        .filter(series=series)
        .filter_descendants(category)
        .active()
    )
    if not options:
        raise http.Http404('<h1>В секции нет изделий</h1')

    images = context.products.ProductImages(
        set([o.product for o in options]), Image.objects.all()
    )
    return render(
        request,
        'catalog/series.html',
        {
            **images.context(),
            'products': options,
            'page': series.page,
            'category': category,
        }
    )
