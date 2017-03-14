from catalog.views import search
from catalog.models import search as search_models
from ecommerce.forms import OrderBackcallForm

from stroyprombeton.views.helpers import MODEL_MAP


class AbstractSearch:

    model_map = MODEL_MAP

    # Warning: Dirty fix. Search CBV need refactoring
    # Tail task: https://goo.gl/FFlpFF
    def search(self, term, limit, ordering=None):
        stripped_term = term.strip()

        product_lookups = [
            'search_field__icontains',
            'id__contains',
            'code__contains',
        ]

        categories = search_models(stripped_term, self.category, self.lookups)
        products = search_models(stripped_term, self.product, product_lookups, ordering)

        categories = categories[:limit]
        left_limit = limit - len(categories)
        products = products[:left_limit]

        return categories, products


class Autocomplete(AbstractSearch, search.Autocomplete):

    see_all_label = 'Показать все результаты'

    # Extend default ordering fields
    extra_ordering_fields = ('mark', 'specification',)

    # Extend default search fields
    extra_entity_fields = {
        'product': {
            'mark',
            'specification',
        },
    }


class AdminAutocomplete(search.AdminAutocomplete):
    model_map = MODEL_MAP


class Search(AbstractSearch, search.Search):

    def get_context_data(self, **kwargs):
        context = super(Search, self).get_context_data(**kwargs)

        return {
            **context,
            'backcall_form': OrderBackcallForm(),
        }
