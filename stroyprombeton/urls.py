from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from stroyprombeton import views

catalog_urls = [
    url(r'^$', views.CategoryTree.as_view(),
        name='category_tree'),
    url(r'^categories/(?P<category_id>[0-9]+)/$', views.CategoryPage.as_view(),
        name='category'),
    url(r'^products/(?P<product_id>[0-9]+)/$', views.ProductPage.as_view(),
        name='product'),
]

search_urls = [
    url(r'^autocomplete/$', views.Autocomplete.as_view(), name='autocomplete'),
    url(r'^$', views.Search.as_view(), name='search'),
]

ecommerce_urls = [
    url(r'^cart-add/$', views.AddToCart.as_view(), name='cart_add'),
    url(r'^cart-change/$', views.ChangeCount.as_view(), name='cart_set_count'),
    url(r'^cart-flush/$', views.FlushCart.as_view(), name='cart_flush'),
    url(r'^cart-remove/$', views.RemoveFromCart.as_view(), name='cart_remove'),
    url(r'^order/$', views.OrderPage.as_view(), name='order_page'),
]

urlpatterns = [
    url(r'^order-price/', views.OrderPrice.as_view(),
        name='order_price'),
    url(r'^order-drawing/', views.OrderDrawing.as_view(),
        name='order_drawing'),
    url(r'^price-success/', views.OrderPriceSuccess.as_view(),
        name='order_price_success'),
    url(r'^drawing-success/', views.OrderDrawingSuccess.as_view(),
        name='order_drawing_success'),
    url(r'^$', views.index, name='index'),
    url(r'^blog/news/$', views.blog_news_list, name='news'),
    url(r'^blog/news/1/$', views.blog_news_item, name='news_item'),
    url(r'^blog/posts/1/$', views.blog_post_item, name='post_item'),
    url(r'^gbi/', include(catalog_urls)),
    url(r'^visual/', views.visual_page, name='catalog'),
    url(r'^shop/', include(ecommerce_urls)),
    url(r'^shop/', include('ecommerce.urls')),
    url(r'^search/', include(search_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
