from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.template import Template, Context
from django.views.decorators.http import require_POST
from django.views.generic import FormView, TemplateView

from ecommerce import cart as ec_cart, views as ec_views
from ecommerce.mailer import send_backcall
from pages.models import CustomPage
from pages.views import CustomPageView
from stroyprombeton import mailer
from stroyprombeton.forms import OrderForm, PriceForm
from stroyprombeton.models import Option, Order


class Cart(ec_cart.Cart):
    def get_position_data(self, position: Option):
        return {
            **super().get_position_data(position),
            'code': position.code or '',
            'catalog_name': position.catalog_name,
        }


class OrderPage(ec_views.OrderPage):
    cart = Cart
    order_form = OrderForm
    email_extra_context = {
        'base_url': settings.BASE_URL,
        'site_info': settings.SITE_INFO
    }


class OrderSuccess(ec_views.OrderSuccess):
    order = Order


class AddToCart(ec_views.AddToCart):
    cart = Cart
    order_form = OrderForm
    position_model = Option
    # @todo #468  Rename position_key to 'option' at js files.
    #  All `position_key` values at this file will become 'option'.
    position_key = 'product'


class RemoveFromCart(ec_views.RemoveFromCart):
    cart = Cart
    order_form = OrderForm
    position_model = Option
    position_key = 'product'


class FlushCart(ec_views.FlushCart):
    cart = Cart
    order_form = OrderForm
    position_model = Option
    position_key = 'product'


class ChangeCount(ec_views.ChangeCount):
    cart = Cart
    order_form = OrderForm
    position_model = Option
    position_key = 'product'


# -------- STB-specific views -------- #
class OrderDrawing(CustomPageView):
    template_name = 'ecommerce/order/drawing.html'


class OrderPrice(FormView, CustomPageView):
    form_class = PriceForm
    template_name = 'ecommerce/order/price.html'
    success_url = reverse_lazy(
        CustomPage.ROUTE,
        current_app='stroyprombeton',
        args=('price-success',)
    )

    def get_context_data(self, **kwargs):
        context = super(CustomPageView, self).get_context_data(**kwargs)
        page = context['page']
        page_content_context = Context({'form': context['form']})
        page_content_template = Template(page.content)
        return {
            **context,
            'order_page_content': page_content_template.render(page_content_context)
        }

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            mailer.send_form(
                form=form,
                template='ecommerce/email_price.html',
                subject='Заказ прайс-листа',
            )
            return self.form_valid(form)
        else:
            return self.get(request, *args, **kwargs)


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
