from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps import views as sitemaps_view
from django.views.decorators.cache import cache_page

from pages.models import Page
from pages.views import robots, SitemapPage

from stroyprombeton import sitemaps, views
from stroyprombeton.admin import stb_admin_site


admin_urls = [
    url(r'^', stb_admin_site.urls),
    url(r'^autocomplete/$', views.AdminAutocomplete.as_view()),
    url(r'^get-tree-items/$', views.Tree.as_view()),
    url(r'^redirect-to-product/$', views.RedirectToProduct.as_view()),
    url(r'^table-editor-api/$', views.TableEditorAPI.as_view()),
]

catalog_urls = [
    url(r'^categories/(?P<category_id>[0-9]+)/$',
        views.CategoryPage.as_view(), name='category'),
    url(r'^categories/(?P<category_id>[0-9]+)/pdf/$',
        views.ProductPDF.as_view(), name='product_pdf'),
    url(r'^products/(?P<product_id>[0-9]+)/$',
        views.ProductPage.as_view(), name='product'),
]

url_name = Page.CUSTOM_PAGES_URL_NAME
custom_pages = [
    url(r'^(?P<page>)$', views.IndexPage.as_view(), name=url_name),
    url(r'^(?P<page>client-feedbacks)/$', views.ClientFeedbacksPageView.as_view(), name=url_name),
    url(r'^(?P<page>drawing-success)/$', views.OrderDrawingSuccess.as_view(), name=url_name),
    url(r'^(?P<page>gbi)/$', views.CategoryTree.as_view(), name=url_name),
    url(r'^(?P<page>news)/$', views.NewsPageView.as_view(), name=url_name),
    url(r'^(?P<page>price-success)/$', views.OrderPriceSuccess.as_view(), name=url_name),
    url(r'^(?P<page>order)/$', views.OrderPage.as_view(), name=url_name),
    url(r'^(?P<page>order-drawing)/$', views.OrderDrawing.as_view(), name=url_name),
    url(r'^(?P<page>order-price)/$', views.OrderPrice.as_view(), name=url_name),
    url(r'^(?P<page>order-success)/$', views.OrderSuccess.as_view(), name=url_name),
    url(r'^(?P<page>regions)/$', views.RegionsPageView.as_view(), name=url_name),
    url(r'^(?P<page>search)/$', views.Search.as_view(), name=url_name),
    url(r'^(?P<page>sitemap)/$', SitemapPage.as_view(), name=url_name),
]
ecommerce_urls = [
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order/$', views.OrderPage.as_view(), name='order_page'),
    url(r'^order-backcall/$', views.order_backcall, name='order_backcall'),
    url(r'', include('ecommerce.urls')),  # this include should be always last
]

search_urls = [
    url(r'^autocomplete/$', views.Autocomplete.as_view(), name='autocomplete'),
]

sitemaps = {
    'categories': sitemaps.CategoryPagesSitemap,
    'custom-pages': sitemaps.CustomPagesSitemap,
    'index': sitemaps.IndexSitemap,
    'flat-pages': sitemaps.FlatPagesSitemap,
    'products': sitemaps.ProductPagesSitemap,
}

cached_view = cache_page(settings.CACHED_TIME)

urlpatterns = [
    url(r'', include(custom_pages)),
    url(r'admin/', include(admin_urls)),
    url(r'^gbi/', include(catalog_urls)),
    url(r'^fetch-products/$', views.fetch_products, name='fetch_products'),
    url(r'^page/', include('pages.urls')),
    url(r'^price-success/', views.OrderPriceSuccess.as_view(), name='order_price_success'),
    url(r'^robots\.txt$', robots),
    url(r'^search/', include(search_urls)),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^sitemap\.xml$', cached_view(sitemaps_view.index),
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps_children'}, name='sitemap'),
    url(r'^sitemap-(?P<section>.+)\.xml$', cached_view(sitemaps_view.sitemap),
        {'sitemaps': sitemaps}, name='sitemaps_children'),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
