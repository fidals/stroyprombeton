"""stroyprombeton URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static

from . import views

catalog_urls = [
    url(r'^$', views.CategoryTree.as_view(), name='category_tree'),
    url(r'^categories/(?P<category_id>[0-9]+)/$', views.CategoryPage.as_view(),
        name='category'),
    url(r'^products/(?P<product_id>[0-9]+)/$', views.ProductPage.as_view(),
        name='product'),
]

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^blog/news/$', views.blog_news_list, name='news'),
    url(r'^blog/news/1/$', views.blog_news_item, name='news_item'),
    url(r'^blog/posts/1/$', views.blog_post_item, name='post_item'),
    url(r'^gbi/', include(catalog_urls)),
    url(r'^order/$', views.order_page, name='order_page'),
    url(r'^visual/', views.visual_page, name='catalog'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
