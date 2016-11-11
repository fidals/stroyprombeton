import os
import json

from django.conf import settings

from ecommerce.forms import OrderBackcallForm
from pages.models import FlatPage
from pages.views import CustomPageView, FlatPageView

from stroyprombeton import config


def get_regions():
    file_path = os.path.join(settings.BASE_DIR, 'templates/pages/index/regions.json')

    with open(file_path) as json_data:
        regions = json.load(json_data)

    return regions


class IndexPage(CustomPageView):

    template_name = 'pages/index/index.html'
    backcall_form = OrderBackcallForm

    def get_context_data(self, **kwargs):
        """Extended method. Add product's images to context."""
        context = super(IndexPage, self).get_context_data(**kwargs)

        return {
            **context,
            'news': FlatPage.objects.filter(parent__slug='news', is_active=True)[:2],
            'partners': config.PARTNERS,
            'reviews': FlatPage.objects.filter(parent__slug='user-feedbacks')[:3],
            'regions': get_regions(),
            'backcall_form': self.backcall_form(),
        }


class RegionFlatPage(FlatPageView):
    """Custom view for regions and it's flat_pages."""

    template_name = 'pages/regions/region_page.html'
