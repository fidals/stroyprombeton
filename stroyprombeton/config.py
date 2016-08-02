"""
Config storage for stroyprombeton.ru.
Every config-like option which doesn't belong to settings should be here.
"""

pages = {
    'main': {
        'title': 'Завод ЖБИ «СТК-ПромБетон» | '
                 'Производство ЖБИ в Санкт-Петербурге, железобетонные изделия СПб',
        'name': '',
        'h1': '',
        'keywords': '',
        'description': '',
        'site_url': 'www.stroyprombeton.ru'
    },
}


def page_metadata(page):
    """
    Returns page metadata (e.g., name, title, h1 and so on)
    for a given page string.

    If such page doesn't have metadata, it throws ValueError.
    :param page: string page identifier
    :return: dict with metadata
    """
    try:
        return pages[page]
    except KeyError:
        raise ValueError('site data have not such page: {}.'
                         'Check your config.py'.format(page))


def cached_time() -> int:
    """Returns value of days for caching in seconds."""
    one_day_in_seconds = 60 * 60 * 24
    days_to_cache = 60

    return one_day_in_seconds * days_to_cache

HREFS = {
    'istok_plus': 'http://istok-plus.ru',
    'stk_module': 'http://xn----htbqgdmrio5g.xn--p1ai',
}

SITE_INFO = {
    'email': 'info@stroyprombeton.ru',
    'phone': {
        'msc': '649-33-79',
        'spb1': '655-73-60',
        'spb2': '655-72-95',
        'arh': '63-92-35',
        'mur': '65-50-48',
        'uri_tel1': '+78126557360',
        'uri_tel2': '+78126557295'
    },
}
