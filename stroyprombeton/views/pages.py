from django.conf import settings

import pages.views
from ecommerce.forms import OrderBackcallForm
from pages.models import FlatPage


def get_regions():
    return (
        FlatPage.objects
        .filter(parent__slug='regions', is_active=True)
        .order_by('position')
    )


class IndexPage(pages.views.CustomPageView):
    template_name = 'pages/index/index.html'
    backcall_form = OrderBackcallForm

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)

        return {
            **context,
            'news': FlatPage.objects.filter(parent__slug='news', is_active=True)
                        .order_by('-date_published')[:2],
            'partners': settings.PARTNERS,
            'reviews': FlatPage.objects.filter(parent__slug='client-feedbacks')[:3],
            'regions': get_regions,
            'backcall_form': self.backcall_form()
        }


class NewsPageView(pages.views.CustomPageView):
    template_name = 'pages/page.html'


class RegionsPageView(pages.views.CustomPageView):
    template_name = 'pages/regions/region_page.html'

    def get_context_data(self, **kwargs):
        context = super(RegionsPageView, self).get_context_data(**kwargs)

        return {
            **context,
            'regions': get_regions
        }
