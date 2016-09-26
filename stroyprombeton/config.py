"""
Config storage for stroyprombeton.ru.
Every config-like option which doesn't belong to settings should be here.
"""


def cached_time() -> int:
    """Return value of days for caching in seconds."""

    one_day_in_seconds = 60 * 60 * 24
    days_to_cache = 60

    return one_day_in_seconds * days_to_cache

SITE_INFO = {
    'email': 'info@stroyprombeton.ru',
    'phone': {
        'moscow_1': '8 (499) 322-31-98',
        'moscow_1_url': '+74993223198',
        'spb_1': '8 (812) 648-13-80',
        'spb_1_url': '+78126481380'
    },
}

PARTNERS = [
    {
        'url': 'http://xn----htbqgdmrio5g.xn--p1ai/',
        'logo': 'images/partner-stkmodul-logo.png',
        'text': 'Нерудные материалы',
        'alt': 'СТК-Модуль',
    },
    {
        'url': 'http://stkm-energo.ru/',
        'logo': 'images/partner-modulenergo-logo.png',
        'text': 'Модуль энерго',
        'alt': 'Монтаж и строительство энергообъектов',
    },
    {
        'url': 'http://www.stk-metal.ru/',
        'logo': 'images/partner-stkmetall-logo.png',
        'text': 'СТК-Металл',
        'alt': 'Поставка металлоконструкций',
    },
]

REVIEWS = [
    {
        'title': 'СТК-Модуль 1',
        'text': '«Тут можно разместить какую-то выборочную цитату из\
                 «благодарственного письма, а само письмо открывать по клику на\
                 «цитату, либо по кнопке.»',
    },
    {
        'title': 'СТК-Модуль 2',
        'text': '«Пацаны ваще ребята. Особенно вон тот - в белом.»',
    },
    {
        'title': 'СТК-Модуль 3',
        'text': '«Умеют. Могут.»',
    },
]
