"""Management command for transfer data from MySql to PostgreSQL"""

import os
import json
import pymysql
from getpass import getpass
from datetime import datetime
from unidecode import unidecode

from django.utils.text import slugify
from django.db import transaction
from django.core.management.base import BaseCommand
from django.conf import settings

from stroyprombeton.models import Category, Product, Territory
from pages.models import Page

custom_page_data = {
    'news': {
        'slug': 'news',
        'h1': 'Новости компании',
        'title': 'Завод ЖБИ «СТК-ПромБетон»',
        'menu_title': 'Новости компании'
    },
    'obekty': {
        'route': 'territory_page',
        'slug': 'obekty',
        'h1': 'Регионы, в которые поставлялась продукция «СТК-ПромБетон»',
        'title': 'Регионы, в которые поставлялась продукция «СТК-ПромБетон»',
        'menu_title': 'Наши объекты',
        'position': 4,
        'type': Page.CUSTOM_TYPE,
    },
    'index': {
        'slug': 'index',
        'route': 'index',
        'title': 'Завод ЖБИ «СТК-ПромБетон» | Производство ЖБИ в Санкт-Петербурге, железобетонные изделия СПб',
        'h1': 'Завод железобетонных изделий «СТК-Промбетон»',
        'menu_title': 'Главная',
        'type': Page.CUSTOM_TYPE,
    },
    'category_tree': {
        'slug': 'category_tree',
        'route': 'category_tree',
        'title': 'Каталог товаров',
        'h1': 'Все категории',
        'type': Page.CUSTOM_TYPE,
        'menu_title': 'Каталог',
    },
    'search': {
        'slug': 'search',
        'type': Page.CUSTOM_TYPE,
        'title': 'Результаты поиска',
    },
}


class Command(BaseCommand):
    path_to_JSON = os.path.join(settings.BASE_DIR, 'stb.json')

    navigation_items_positions = {
        'ordering': 1,
        'delivery': 2,
        'proizvodstvo-gbi': 3,
        'about': 5,
        'contacts': 6
    }

    MYSQL_CONFIG = {
        'user': 'proger',
        'password': '',
        'db': 'stroyprombeton',
        'host': 'serv.fidals.ru',
        'port': 3306,
        'charset': 'utf8mb4'
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--liveserver',
            action='store_true',
            dest='liveserver',
            default=False
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.truncate_data()
        if options['liveserver']:
            with self.connect_to_the_mysql_db() as cursor:
                data = self.get_data_from_db(cursor)
                self.insert_data_to_DB(data)
        else:
            data = self.get_data_from_json()
            self.insert_data_to_DB(data)

    def get_data_from_json(self) -> dict:
        with open(self.path_to_JSON) as stb_json:
            return json.load(stb_json)

    def get_data_from_db(self, cur: pymysql):
        tables = {
            'categories': ' '.join([
                'id, parent_id, mark, name, title, h1, date,',
                'text, ord'
            ]),
            'posts': ' '.join([
                'name, title, h1, keywords, description, is_active, date,',
                'text'
            ]),
            'products': ' '.join([
                'section_id, nomen, mark, length, width, height, weight,',
                'volume, diameter_out, diameter_in, price, title,',
                'keywords, description, date, text, price_date',
            ]),
            'static_pages': ' '.join([
                'alias, name, title, h1, keywords, description, is_active,',
                'date, text'
            ])
        }

        def get_data(table: str) -> tuple:
            """Select all data from database."""
            cur.execute('select {} from {}'.format(tables[table], table))
            return cur.fetchall()

        def remove_esc_char(data: tuple) -> list:
            """Make data mutable and remove all escape characters."""
            remove_esc_char = (lambda string: string.replace('\n', '').
                               replace('\r', '').replace('\t', ''))

            check = (lambda raw:
                     remove_esc_char(raw) if isinstance(raw, str) else raw)

            return [
                [check(raw) for raw in obj]
                for obj in data
            ]

        def make_dict(data: list, table: str) -> dict:
            columns_names = tables[table].split(', ')
            return [
                {columns_names[i]: obj[i] for i in range(len(obj))}
                for obj in data
            ]

        return {
            table: make_dict(remove_esc_char(get_data(table)), table)
            for table in tables
        }

    def insert_data_to_DB(self, data: dict):
        """Insert data in category, product, post and static_page tables."""

        to_datetime = (lambda date:
                       datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                       if date and not isinstance(date, datetime) else date)

        to_int = (lambda obj:
                  int(obj) if obj else obj)

        to_float = (lambda obj:
                    float(obj) if obj else obj)

        is_exist = lambda obj: obj if obj else ''

        def create_category_data(data: list):
            for category_data in data:
                category = Category.objects.create(
                    id=to_int(category_data['id']),
                    name=category_data['name'],
                    position=to_int(category_data['ord']),
                    specification=category_data['mark'],
                )
                category.page.content = category_data['text']
                category.page._date_published = to_datetime(category_data['date'])
                category.page.h1 = is_exist(category_data['h1'])
                category.page.menu_title = category_data['title']
                category.page.is_active = bool(category_data['is_active'])
                category.save()

            get_category = (lambda id_:
                            Category.objects.all().get(id=to_int(id_)))

            def create_parent(category):
                current = get_category(category['id'])
                current.parent = get_category(category['parent_id'])
                current.save()

            def has_parent(category):
                return bool(category['parent_id'])

            for category in filter(has_parent, data):
                create_parent(category)

        def create_product_data(data: list):
            for product_data in data:
                product = Product.objects.create(
                    category=Category.objects.get(
                        id=to_int(product_data['section_id'])
                    ),
                    code=to_int(product_data['nomen']),
                    date_price_updated=to_datetime(product_data['price_date']),
                    diameter_in=to_int(product_data['diameter_in']),
                    diameter_out=to_int(product_data['diameter_out']),
                    height=to_int(product_data['height']),
                    mark=product_data['mark'],
                    name=product_data['title'],
                    price=to_float(product_data['price']),
                    specification=product_data['description'],
                    volume=to_float(product_data['volume']),
                    weight=to_float(product_data['weight']),
                    width=to_int(product_data['width']),
                    length=to_int(product_data['length'])
                )
                product.page.content = product_data['text']
                product.page._date_published = to_datetime(product_data['date'])
                product.page.keywords = is_exist(product_data['keywords'])
                product.save()

        def create_post_data(data: list):
            news = Page.objects.create(**custom_page_data['news'])
            for post_data in data:
                Page.objects.create(
                    slug=slugify(unidecode(post_data['name'])),
                    content=is_exist(post_data['text']),
                    parent=news,
                    _date_published=to_datetime(post_data['date']),
                    description=is_exist(post_data['description']),
                    h1=is_exist(post_data['h1']),
                    is_active=bool(post_data['is_active']),
                    keywords=is_exist(post_data['keywords']),
                    title=post_data['title'] or post_data['name']
                )

        def create_static_page_data(data: list):
            navigation = Page.objects.create(slug='navi')
            Page.objects.create(**custom_page_data['obekty'], parent=navigation)
            Page.objects.create(**custom_page_data['index'], parent=navigation)
            Page.objects.create(**custom_page_data['category_tree'])
            Page.objects.create(**custom_page_data['search'])

            for static_page_data in data:
                static_page = Page.objects.create(
                    content=static_page_data['text'],
                    _date_published=to_datetime(static_page_data['date']),
                    description=is_exist(static_page_data['description']),
                    h1=is_exist(static_page_data['h1']),
                    is_active=bool(static_page_data['is_active']),
                    keywords=is_exist(static_page_data['keywords']),
                    slug=static_page_data['alias'],
                    title=static_page_data['title'] or static_page_data['name']
                )
                if static_page.slug in self.navigation_items_positions:
                    static_page.parent = navigation
                    static_page.menu_title = static_page_data['title'] or static_page_data['name']
                    static_page.position = self.navigation_items_positions[static_page.slug]
                    static_page.save()

        create_category_data(data['categories'])
        create_product_data(data['products'])
        create_post_data(data['posts'])
        create_static_page_data(data['static_pages'])

        print('Was created {} categories, {} products, {} pages'.format(
            Category.objects.count(),
            Product.objects.count(),
            Page.objects.count(),
        ))

    def connect_to_the_mysql_db(self) -> pymysql.connect:
        """Connection to the database and create the cursor."""
        self.MYSQL_CONFIG['password'] = getpass(
            prompt='Enter password for stroyprombeton database: ')

        try:
            conn = pymysql.connect(**self.MYSQL_CONFIG)
            return conn

        except pymysql.err.OperationalError:
            print('Entered incorrect password.')
            self.connect_to_the_mysql_db()

    def truncate_data(self):
        Category.objects.all().delete()
        Product.objects.all().delete()
        Page.objects.all().delete()
        Territory.objects.all().delete()
