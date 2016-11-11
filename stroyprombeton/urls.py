from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from pages.models import Page

from stroyprombeton.admin import stb_admin_site
from stroyprombeton.views import catalog, ecommerce, pages, search


admin_urls = [
    url(r'^', stb_admin_site.urls),
]

catalog_urls = [
    url(r'^categories/(?P<category_id>[0-9]+)/$',
        catalog.CategoryPage.as_view(), name='category'),
    url(r'^products/(?P<product_id>[0-9]+)/$',
        catalog.ProductPage.as_view(), name='product'),
]

url_name = Page.CUSTOM_PAGES_URL_NAME
custom_pages = [
    url(r'^(?P<page>)$', pages.IndexPage.as_view(), name=url_name),
    url(r'^(?P<page>drawing-success)/$', ecommerce.OrderDrawingSuccess.as_view(), name=url_name),
    url(r'^(?P<page>gbi)/$', catalog.CategoryTree.as_view(), name=url_name),
    url(r'^(?P<page>price-success)/$', ecommerce.OrderPriceSuccess.as_view(), name=url_name),
    url(r'^(?P<page>order)/$', ecommerce.OrderPage.as_view(), name=url_name),
    url(r'^(?P<page>order-success)/$', ecommerce.OrderSuccess.as_view(), name=url_name),
    url(r'^(?P<page>search)/$', search.Search.as_view(), name=url_name),
]

ecommerce_urls = [
    url(r'^cart-add/$', ecommerce.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', ecommerce.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', ecommerce.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', ecommerce.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order/$', ecommerce.OrderPage.as_view(), name='order_page'),
    url(r'^order-backcall/$', ecommerce.order_backcall, name='order_backcall'),
    url(r'', include('ecommerce.urls')),  # this include should be always last
]

search_urls = [
    url(r'^autocomplete/$', search.Autocomplete.as_view(), name='autocomplete'),
]

urlpatterns = [
    url(r'', include(custom_pages)),
    url(r'admin/', include(admin_urls)),
    url(r'^gbi/', include(catalog_urls)),
    url(r'^fetch-products/$', catalog.fetch_products, name='fetch_products'),
    url(r'^order-drawing/', ecommerce.OrderDrawing.as_view(), name='order_drawing'),
    url(r'^order-price/', ecommerce.OrderPrice.as_view(), name='order_price'),
    url(r'^page/', include('pages.urls')),
    url(r'^regions/^([\w-]+)/$', pages.RegionFlatPage.as_view(), name='region_flat_page'),
    url(r'^search/', include(search_urls)),
    url(r'^shop/', include(ecommerce_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
