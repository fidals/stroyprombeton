from catalog.views import search

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
