"""
Config storage for stroyprombeton.ru.
Every config-like option which doesn't belong to settings should be here.
"""

def cached_time() -> int:
    """Return value of days for caching in seconds."""
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
