from catalog.views import search
from catalog.models import search as search_models

from stroyprombeton.views.helpers import MODEL_MAP


class Autocomplete(search.Autocomplete):
    model_map = MODEL_MAP
    see_all_label = 'Показать все результаты'
    search_url = 'search'

    # Extend default ordering fields
    extra_ordering_fields = ('mark',)

    # Extend default search fields
    extra_entity_fields = {
        'product': {
            'mark',
        },
    }


class AdminAutocomplete(search.AdminAutocomplete):
    model_map = MODEL_MAP


class Search(search.Search):
    model_map = MODEL_MAP

    # Warning: Dirty fix. Search CBV need refactoring
    # Tail task: https://goo.gl/FFlpFF
    def search(self, term, limit, ordering=None):
        """Perform a search on models. Return evaluated QuerySet."""
        product_lookups = ['name__icontains', 'id__contains', 'code__contains']
        categories = search_models(term, self.category, self.lookups)
        products = search_models(term, self.product, product_lookups, ordering)

        categories = categories[:limit]
        left_limit = limit - len(categories)
        products = products[:left_limit]

        return categories, products