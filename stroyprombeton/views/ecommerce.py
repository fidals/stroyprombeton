from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from ecommerce import views as ec_views
from ecommerce.mailer import order_backcall as send_backcall
from pages.models import Page

from stroyprombeton import mailer
from stroyprombeton.forms import DrawingForm, OrderForm, PriceForm
from stroyprombeton.models import Product, Order


class OrderPage(ec_views.OrderPage):
    order_form = OrderForm


class OrderSuccess(ec_views.OrderSuccess):
    order = Order


class AddToCart(ec_views.AddToCart):
    order_form = OrderForm
    product_model = Product


class RemoveFromCart(ec_views.RemoveFromCart):
    order_form = OrderForm
    product_model = Product


class FlushCart(ec_views.FlushCart):
    order_form = OrderForm
    product_model = Product


class ChangeCount(ec_views.ChangeCount):
    order_form = OrderForm
    product_model = Product


# -------- STB-specific views -------- #
class OrderDrawing(FormView):
    form_class = DrawingForm
    template_name = 'ecommerce/order/drawing.html'
    success_url = reverse_lazy(
        Page.CUSTOM_PAGES_URL_NAME,
        current_app='stroyprombeton',
        args=('drawing-success',)
    )

    def form_valid(self, form):
        mailer.send_form(
            form=form,
            template='ecommerce/email_drawing.html',
            subject='Изготовление по индивидуальным чертежам'
        )

        return super(OrderDrawing, self).form_valid(form)


class OrderDrawingSuccess(TemplateView):
    template_name = 'ecommerce/order/drawing_success.html'


class OrderPrice(FormView):
    form_class = PriceForm
    template_name = 'ecommerce/order/price.html'
    success_url = reverse_lazy(
        Page.CUSTOM_PAGES_URL_NAME,
        current_app='stroyprombeton',
        args=('price-success',)
    )

    def form_valid(self, form):
        mailer.send_form(
            form=form,
            template='ecommerce/email_price.html',
            subject='Заказ прайс-листа'
        )

        return super(OrderPrice, self).form_valid(form)


class OrderPriceSuccess(TemplateView):
    template_name = 'ecommerce/order/price_success.html'


@require_POST
def order_backcall(request):
    """Send email about ordered Backcall."""

    name, phone, url = ec_views.get_keys_from_post(
        request,
        'orderData[id_name]',
        'orderData[id_phone]',
        'orderData[url]'
    )

    send_backcall(
        subject=settings.EMAIL_SUBJECTS['backcall'],
        name=name,
        phone=phone,
        url=url
    )

    return HttpResponse('ok')
