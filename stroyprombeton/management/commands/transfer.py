"""Management command for transfer data from MySql to PostgreSQL"""

import os
import json
import pymysql
from getpass import getpass
from datetime import datetime
from unidecode import unidecode

from django.db import transaction
from django.conf import settings
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from stroyprombeton import config
from stroyprombeton.models import Category, Product, Region, CategoryPage, ProductPage

from pages.models import Page, FlatPage, CustomPage
from images.models import Image


CUSTOM_PAGES = {
    'news': {
        'slug': 'news',
        'h1': 'Новости компании',
        'title': 'Завод ЖБИ «СТК-ПромБетон»',
        'menu_title': 'Новости компании'
    },
    'index': {
        'slug': '',
        'title': 'Завод ЖБИ «СТК-ПромБетон» | Производство ЖБИ в Санкт-Петербурге, железобетонные изделия СПб',
        'h1': 'Завод железобетонных изделий «СТК-Промбетон»',
        'menu_title': 'Главная',
        'type': Page.CUSTOM_TYPE,
    },
    'category_tree': {
        'slug': 'gbi',
        'title': 'Каталог товаров',
        'h1': 'Все категории',
        'type': Page.CUSTOM_TYPE,
        'menu_title': 'Каталог',
        'content': '''
            <p class="about-catalog-p">В этом году наш завод в течение 1-го
            квартала активно работал по производству и поставке мостовых
            железобетонных конструкций по заказу нефтедобывающих компаний. Это
            блоки шкафных стенок, блоки насадок, диафрагмы и ригели. Вся
            продукция «несерийная» и производилась по чертежам Заказчика.
            Поставка изделий осуществлялась по железной дороге для
            строительства объектов на полуострове Ямал. Следует отметить, что
            мы изначально ориентированы на выпуск продукции для транспортного
            строитеьства в широком спектре изделий, включая индивидуальные
            заказы.</p>
            <p class="about-catalog-p">В апреле наше предприятие выпускало
            изделия для реконструкции мостов на Октябрьской железной дороге
            (короба, шкафные блоки, элементы лестничных сходов). Специфика
            поставок на объекты дороги имеет особенность – работу необходимо
            выполнять строго по графику, так как установка конструкций
            осуществляется в так называемые «окна». Мы уже не первый год
            работаем на этом направлении, что позволяет нам успешно справляться
            со взятыми на себя обязательствами.</p>
            ''',
    },
    'search': {
        'slug': 'search',
        'type': Page.CUSTOM_TYPE,
        'title': 'Результаты поиска',
    },
    'order': {
        'slug': 'order',
        'type': Page.CUSTOM_TYPE,
        '_title': 'Корзина Интернет-магазин СТК-ПромБетон',
        'h1': 'Оформление заказа',
    },
}

IMAGES_ROOT_FOLDER_NAME = os.path.join(settings.MEDIA_ROOT, 'products')


# TODO - launch and test it
def fill_images_data():

    def iter_decimal_dirs(path: str):
        return (
            dir_ for dir_ in os.scandir(path)
            if dir_.is_dir() and dir_.name.isdecimal()
        )

    def iter_files(path: str):
        return (file_ for file_ in os.scandir(path) if file_.is_file())

    def get_page(product_id: int) -> Page:
        try:
            product_ = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            # images folder can contain unsupported ids
            return
        return product_.page

    def create_image_model(file_, product_id: int, slug):
        file_short_name, _ = os.path.splitext(file_.name)

        # skip compressed or doubled images: '222-th.jpg', for example
        if file_short_name.endswith('-th'):
            return

        # create Image model object based on current image
        page = get_page(product_id=product_id)
        if not page:
            return

        Image.objects.create(
            model=page,
            # autoincrement file names: '1.jpg', '2.jpg' and so on
            slug=slug,
            image=ImageFile(open(file_.path, mode='rb')),
            is_main=(file_short_name == dir_.name)
        )

    if not os.path.isdir(IMAGES_ROOT_FOLDER_NAME):
        return

    # run over every image in every folder
    for dir_ in iter_decimal_dirs(IMAGES_ROOT_FOLDER_NAME):
        for slug_index, file in enumerate(iter_files(dir_.path)):
            create_image_model(
                file_=file,
                product_id=int(dir_.name),
                slug=str(slug_index)
            )
    # old folder stays in fs as backup of old photos


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
        with open(self.path_to_JSON, encoding='utf-8') as stb_json:
            return json.load(stb_json)

    def get_data_from_db(self, cur: pymysql):
        tables = {
            'categories': ' '.join([
                'id, parent_id, mark, name, title, h1, date, text, ord'
            ]),
            'posts': ' '.join([
                'name, title, h1, keywords, description, is_active, date, text'
            ]),
            'products': ' '.join([
                'section_id, nomen, mark, length, width, height, weight,',
                'volume, diameter_out, diameter_in, price, title,',
                'keywords, description, date, text, price_date',
            ]),
            'static_pages': ' '.join([
                'alias, name, title, h1, keywords, description, is_active, date, text'
            ]),
        }

        def get_data(table: str) -> tuple:
            """Select all data from database."""
            cur.execute('select {} from {}'.format(tables[table], table))
            return cur.fetchall()

        def remove_esc_char(data: tuple) -> list:
            """Make data mutable and remove all escape characters."""
            remove_esc_char = (lambda string: string.replace('\n', '').
                               replace('\r', '').replace('\t', ''))

            check = (lambda raw: remove_esc_char(raw) if isinstance(raw, str) else raw)

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
                       if date and not isinstance(date, datetime) else datetime.now())

        to_int = (lambda obj: int(obj) if obj else 0)
        to_float = (lambda obj: float(obj) if obj else 0)
        is_exist = lambda obj: obj if obj else ''

        def create_categories(data: list):
            for category_data in data:
                category = Category.objects.create(
                    id=to_int(category_data['id']),
                    name=category_data['name'],
                    specification=category_data['mark'] or '',
                    page=None
                )
                page = CategoryPage.objects.create(
                    position=to_int(category_data['ord']),
                    content=is_exist(category_data['text']),
                    date_published=to_datetime(category_data['date']),
                    h1=is_exist(category_data['h1']),
                    menu_title=is_exist(category_data['title']),
                    is_active=bool(category_data['is_active']),
                )
                try:
                    category.page = page
                    category.save()
                except:
                    page.slug = '{}-{}'.format(page.slug, category.id)
                    page.save()
                    category.page = page
                    category.save()

            def has_parent(category):
                return bool(category['parent_id'])

            for data in filter(has_parent, data):
                child = Category.objects.get(id=to_int(data['id']))
                child.parent = Category.objects.get(id=to_int(data['parent_id']))
                child.save()

        def create_products(data: list):
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
                    length=to_int(product_data['length']),
                    page=None,
                )
                page = ProductPage.objects.create(
                    content=is_exist(product_data['text']),
                    h1=is_exist(product_data['title']),
                    date_published=to_datetime(product_data['date']),
                    keywords=is_exist(product_data['keywords']),
                )
                try:
                    product.page = page
                    product.save()
                except:
                    page.slug = '{}-{}'.format(page.slug, product.id)
                    page.save()
                    product.page = page
                    product.save()

        def create_flat_pages(data: list):
            news = CustomPage.objects.create(**CUSTOM_PAGES['news'])
            user_feedbacks = CustomPage.objects.create(slug='user-feedbacks')

            for page_data in data:
                FlatPage.objects.create(
                    slug=slugify(unidecode(page_data['name'])),
                    content=is_exist(page_data['text']),
                    parent=news,
                    date_published=to_datetime(page_data['date']),
                    description=is_exist(page_data['description']),
                    h1=page_data['h1'] or page_data['title'] or page_data['name'],
                    is_active=bool(page_data['is_active']),
                    keywords=is_exist(page_data['keywords']),
                    title=page_data['title'] or page_data['name']
                )

            # TODO: https://goo.gl/WsyhMo
            for item in config.USER_FEEDBACKS:
                FlatPage.objects.create(
                    slug=slugify(unidecode(item['title'])),
                    content=item['content'],
                    parent=user_feedbacks,
                    title=item['title'],
                )

        def create_static_pages(data: list):
            navigation = Page.objects.create(slug='navi')
            CustomPage.objects.create(**CUSTOM_PAGES['category_tree'])
            CustomPage.objects.create(**CUSTOM_PAGES['index'], parent=navigation)
            CustomPage.objects.create(**CUSTOM_PAGES['search'])
            CustomPage.objects.create(**CUSTOM_PAGES['order'])

            for static_pages in data:
                static_page = Page.objects.create(
                    content=static_pages['text'],
                    date_published=to_datetime(static_pages['date']),
                    description=is_exist(static_pages['description']),
                    h1=is_exist(static_pages['h1']),
                    is_active=bool(static_pages['is_active']),
                    keywords=is_exist(static_pages['keywords']),
                    slug=static_pages['alias'],
                    title=static_pages['title'] or static_pages['name']
                )
                if static_page.slug in self.navigation_items_positions:
                    static_page.parent = navigation
                    static_page.menu_title = static_pages['title'] or static_pages['name']
                    static_page.position = self.navigation_items_positions[static_page.slug]
                    static_page.save()

        def create_regions():
            file_path = os.path.join(settings.BASE_DIR, 'templates/pages/index/regions.json')

            with open(file_path) as json_data:
                json_data = json.load(json_data)

            for i in json_data:
                Region.objects.create(
                    name=json_data[i]['name'],
                )

        create_categories(data['categories'])
        create_products(data['products'])
        create_flat_pages(data['posts'])
        create_static_pages(data['static_pages'])
        create_regions()
        fill_images_data()

        print('Was created {} categories, {} products, {} pages, {} regions'.format(
            Category.objects.count(),
            Product.objects.count(),
            Page.objects.count(),
            Region.objects.count(),
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
        Region.objects.all().delete()
