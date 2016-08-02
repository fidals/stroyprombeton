"""
Stroyprombeton views.

NOTE: They all should be 'zero-logic'.
All logic should be located in respective applications.
"""
from django.shortcuts import render
from django.views.generic import FormView, TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from catalog.views import catalog, search
from ecommerce import views as ec_views

from stroyprombeton import config, mailer
from stroyprombeton.models import Category, Product
from stroyprombeton.forms import OrderForm, PriceForm, DrawingForm

### Helpers ###

# Sets CSRF-cookie to CBVs.
set_csrf_cookie = method_decorator(ensure_csrf_cookie, name='dispatch')
MODEL_MAP = {'product': Product, 'category': Category}

### Search views ###

class AdminAutocomplete(search.AdminAutocomplete):
    """Override model_map for autocomplete."""
    model_map = MODEL_MAP


class Search(search.Search):
    """Override model references to SE-specific ones."""
    model_map = MODEL_MAP


class Autocomplete(search.Autocomplete):
    """Override model references to SE-specific ones."""
    model_map = MODEL_MAP
    see_all_label = 'Смотреть все результаты'
    search_url = 'search'


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
        context = super(CategoryPage, self).get_context_data(**kwargs)
        templates = {True: 'catalog/category_table.html',
                     False: 'catalog/category_tile.html'}

        self.template_name = templates.get(context['category'].is_leaf_node())

        return context


@set_csrf_cookie
class ProductPage(catalog.ProductPage):
    """Override model attribute to STB-specific Product."""
    model = Product


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

### STB-specific views ###


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


@ensure_csrf_cookie
def index(request):
    """Main page view"""

    context = {
        'meta': config.page_metadata('main'),
        'href': config.HREFS,
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
