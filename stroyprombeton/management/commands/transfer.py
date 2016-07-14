"""Management command for transfer data from MySql to PostgreSQL"""

import os
import json
import pymysql
from getpass import getpass
from datetime import datetime

from django.core.management.base import BaseCommand
from django.conf import settings

from stroyprombeton.models import Category, Product, Static_page
from pages.models import Post


class Command(BaseCommand):

    path_to_JSON = os.path.join(settings.BASE_DIR, 'stb.json')
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

    def handle(self, *args, **options):
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
                'id, parent_id, mark, name, title, h1, date, is_active,',
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
                  int(obj) if obj is not None else obj)

        to_float = (lambda obj:
                    float(obj) if obj is not None else obj)

        def create_category_data(data: list):
            for category in data:
                Category.objects.create(
                    id=to_int(category['id']),
                    name=category['name'],
                    content=category['text'],
                    _date_published=to_datetime(category['date']),
                    h1=category['h1'],
                    is_active=bool(category['is_active']),
                    position=to_int(category['ord']),
                    specification=category['mark'],
                    title=category['title']
                )

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
            for product in data:
                Product.objects.create(
                    category=Category.objects.get(
                        id=to_int(product['section_id'])
                    ),
                    code=to_int(product['nomen']),
                    content=product['text'],
                    date_price_updated=to_datetime(product['price_date']),
                    _date_published=to_datetime(product['date']),
                    diameter_in=to_int(product['diameter_in']),
                    diameter_out=to_int(product['diameter_out']),
                    height=to_int(product['height']),
                    keywords=product['keywords'],
                    mark=product['mark'],
                    name=product['title'],
                    price=to_float(product['price']),
                    specification=product['description'],
                    volume=to_float(product['volume']),
                    weight=to_float(product['weight']),
                    width=to_int(product['width']),
                    length=to_int(product['length'])
                )

        def create_post_data(data: list):
            for post in data:
                Post.objects.create(
                    content=post['text'],
                    _date_published=to_datetime(post['date']),
                    description=post['description'],
                    h1=post['h1'],
                    is_active=bool(post['is_active']),
                    keywords=post['keywords'],
                    name=post['name'],
                    title=post['title']
                )

        def create_static_page_data(data: list):
            for static_page in data:
                Static_page.objects.create(
                    content=static_page['text'],
                    _date_published=to_datetime(static_page['date']),
                    description=static_page['description'],
                    h1=static_page['h1'],
                    is_active=bool(static_page['is_active']),
                    keywords=static_page['keywords'],
                    name=static_page['name'],
                    slug=static_page['alias'],
                    title=static_page['title']
                )

        create_category_data(data['categories'])
        create_product_data(data['products'])
        create_post_data(data['posts'])
        create_static_page_data(data['static_pages'])

    def connect_to_the_mysql_db(self) -> pymysql.connect:
        """Connection to the database and create the cursor."""
        password = getpass(
            prompt='Enter password for stroyprombeton database: ')
        self.MYSQL_CONFIG['password'] = password

        try:
            conn = pymysql.connect(**self.MYSQL_CONFIG)
            return conn

        except pymysql.err.OperationalError:
            print('Entered incorrect password.')
            self.connect_to_the_mysql_db()
