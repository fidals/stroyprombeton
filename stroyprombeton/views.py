"""
Stroyprombeton views.

NOTE: They all should be 'zero-logic'.
All logic should be located in respective applications.
"""
from django.conf import settings
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

from catalog.views import catalog, search
from catalog.models import search as filter_
from ecommerce import views as ec_views
from pages.views import CustomPage, FlatPage, get_or_create_struct_page

from stroyprombeton import mailer, config
from stroyprombeton.forms import OrderForm, PriceForm, DrawingForm
from stroyprombeton.models import Category, Product, Territory

# Helpers
# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')
MODEL_MAP = {'product': Product, 'category': Category}


def fetch_products(request):
    """Filter product table on Category page by Name, vendor code, series."""

    size = settings.PRODUCTS_TO_LOAD
    category_id = request.POST.get('categoryId')
    term = request.POST.get('term')
    offset = request.POST.get('offset')
    filtered = request.POST.get('filtered')

    category = Category.objects.get(id=category_id)
    products = Product.objects.get_products_by_category_id(category, ordering=('name', 'mark'))

    if filtered == 'true':
        lookups = ['name__icontains', 'code__icontains', 'mark__icontains']
        products = filter_(products, term, lookups, ordering=('name', 'mark'))

    if offset:
        offset = int(offset)
        left_product_count = products.count() - offset
        size = left_product_count if left_product_count < size else size

        products = products[offset:offset + size]

    return render(request, 'catalog/category_products.html', {'products': products})


# Search views #
class Autocomplete(search.Autocomplete):
    """Override model references to STB-specific ones."""

    model_map = MODEL_MAP
    see_all_label = 'Показать все результаты'
    search_url = 'search'

    # Extend default ordering fields
    extra_ordering_fields = ('mark', )

    # Extend default search fields
    extra_entity_fields = {
        'product': {
            'mark',
        },
    }


class AdminAutocomplete(search.AdminAutocomplete):
    """Override model references to STB-specific ones."""
    model_map = MODEL_MAP


class Search(search.Search):
    """Override model references to STB-specific ones."""
    model_map = MODEL_MAP


class OrderFormMixin:
    order_form = OrderForm


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

        self.template_name = 'catalog/category.html'
        context = super(CategoryPage, self).get_context_data(**kwargs)
        products = Product.objects.get_products_by_category_id(kwargs['object'], ordering=('name', 'mark'))
        sliced_products = products[:settings.PRODUCTS_TO_LOAD]

        context['products'] = sliced_products

        return context


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    """Override model attribute to STB-specific Product."""
    model = Product

    def get_context_data(self, **kwargs):
        """Extend Product page context."""
        context = super(ProductPage, self).get_context_data(**kwargs)
        product = self.get_object()
        siblings = Product.objects.filter(specification=product.specification).exclude(id=product.id)

        context.update({
            'siblings': siblings
        })

        return context


# We inherit eCommerce CBVs to override its order_form attribute.
class OrderPage(OrderFormMixin, ec_views.OrderPage):
    pass


class AddToCart(OrderFormMixin, ec_views.AddToCart):
    pass


class RemoveFromCart(OrderFormMixin, ec_views.RemoveFromCart):
    pass


class FlushCart(OrderFormMixin, ec_views.FlushCart):
    pass


class ChangeCount(OrderFormMixin, ec_views.ChangeCount):
    pass


# STB-specific views #
class OrderDrawing(FormView):
    template_name = 'ecommerce/order_drawing.html'
    form_class = DrawingForm
    success_url = '/drawing-success/'

    def form_valid(self, form):
        mailer.send_form(form=form,
                         template='ecommerce/email_drawing.html',
                         subject='Изготовление по индивидуальным чертежам')
        return super(OrderDrawing, self).form_valid(form)


class OrderPriceSuccess(TemplateView):
    template_name = 'ecommerce/order_price_success.html'


class OrderDrawingSuccess(TemplateView):
    template_name = 'ecommerce/order_drawing_success.html'


class OrderPrice(FormView):
    template_name = 'ecommerce/order_price.html'
    form_class = PriceForm
    success_url = '/price-success/'

    def form_valid(self, form):
        mailer.send_form(form=form,
                         template='ecommerce/email_price.html',
                         subject='Заказ прайс-листа')
        return super(OrderPrice, self).form_valid(form)


class IndexPage(CustomPage):
    """Custom view for Index page."""
    template_name = 'pages/index/index.html'
    slug = 'index'
    context = {
        'news': get_or_create_struct_page(slug='news').children.all().filter(is_active=True)[:2],
        'partners': config.PARTNERS,
        'reviews': config.REVIEWS,
    }


class TerritoryMapPage(CustomPage):
    """Custom view for territory map and it's pages."""
    template_name = 'pages/territory/territory_map.html'
    slug_field = 'obekty'
    context = {
        'territories': Territory.objects.all()
    }


class RegionFlatPage(FlatPage):
    """Custom view for regions and it's flat_pages."""
    template_name = 'pages/territory/region_page.html'
