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
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from images.models import Image
from pages.utils import save_custom_pages
from pages.models import CustomPage, FlatPage, Page
from stroyprombeton.models import Category, Product, CategoryPage, ProductPage


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
        'password': '1fe92635845th',
        'db': 'stb_prod',
        'host': 'serv.fidals.ru',
        'port': 3306,
        'charset': 'utf8mb4'
    }

    @staticmethod
    def purge_tables():
        call_command('flush', '--noinput')

    @transaction.atomic
    def handle(self, *args, **options):
        self.purge_tables()
        with self.connect_to_the_mysql_db() as cursor:
            data = self.get_data_from_db(cursor)
            self.insert_data_to_DB(data)

    def get_data_from_json(self) -> dict:
        with open(self.path_to_JSON, encoding='utf-8') as stb_json:
            return json.load(stb_json)

    def get_data_from_db(self, cur: pymysql):
        tables = {
            'categories': 'id, parent_id, mark, name, title, h1, date, text, ord, is_active',
            'posts': 'name, title, h1, keywords, description, is_active, date, text',
            'products':
                '''
                id, section_id, nomen, mark, length,
                width, height, weight, volume, diameter_out, diameter_in,
                price, title, keywords, description, date, text, price_date, name
                '''.replace('\n', ''),
            'static_pages': 'alias, name, title, h1, keywords, description, is_active, date, text',
            'territories': 'id, translit_name, name',
            'objects': 'territory_id, alias, name, text, date',
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

        def make_dict(data: list, table: str) -> list:
            columns_names = [field.strip() for field in tables[table].split(', ')]
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
        
        def get_date(date):
            return date if date else datetime.now()

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
                    date_published=get_date(category_data['date']),
                    h1=is_exist(category_data['h1']) or is_exist(category_data['name']),
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
                    id=product_data['id'],
                    category=Category.objects.get(
                        id=to_int(product_data['section_id'])
                    ),
                    code=to_int(product_data['nomen']),
                    date_price_updated=get_date(product_data['price_date']),
                    diameter_in=to_int(product_data['diameter_in']),
                    diameter_out=to_int(product_data['diameter_out']),
                    height=to_int(product_data['height']),
                    mark=product_data['mark'],
                    name=is_exist(product_data['title']) or is_exist(product_data['name']),
                    price=to_float(product_data['price']),
                    specification=is_exist(product_data['description']),
                    volume=to_float(product_data['volume']),
                    weight=to_float(product_data['weight']),
                    width=to_int(product_data['width']),
                    length=to_int(product_data['length']),
                    page=None,
                )
                page = ProductPage.objects.create(
                    content=is_exist(product_data['text']),
                    h1=is_exist(product_data['title']) or is_exist(product_data['name']),
                    date_published=get_date(product_data['date']),
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

        def create_news(data: list):
            for page in data:
                FlatPage.objects.create(
                    slug=slugify(unidecode(page['name'])),
                    content=is_exist(page['text']),
                    parent=CustomPage.objects.get(slug='news'),
                    date_published=get_date(page['date']),
                    description=is_exist(page['description']),
                    h1=page['h1'] or page['title'] or page['name'],
                    is_active=bool(page['is_active']),
                    keywords=is_exist(page['keywords']),
                    title=page['title'] or page['name']
                )

        def create_pages(data: list):
            for static_pages in data:
                FlatPage.objects.create(
                    content=static_pages['text'],
                    date_published=get_date(static_pages['date']),
                    description=is_exist(static_pages['description']),
                    h1=is_exist(static_pages['h1']),
                    is_active=bool(static_pages['is_active']),
                    keywords=is_exist(static_pages['keywords']),
                    slug=static_pages['alias'],
                    title=static_pages['title'] or static_pages['name']
                )

        def create_regions(regions):
            regions_page = CustomPage.objects.get(
                slug=settings.CUSTOM_PAGES['regions']['slug'])

            created_regions = {}
            for region in regions:
                slug = slugify(region['translit_name'])
                position = settings.REGIONS[slug]
                region_page = FlatPage.objects.create(
                    h1=region['name'],
                    slug=slugify(region['translit_name']),
                    parent=regions_page,
                    position=position,
                    is_active=bool(position < 1000)
                )
                old_id = region['id']
                created_regions.update({old_id: region_page})
            return created_regions

        def create_region_objects(region_pages, region_objects_data):
            for object_data in region_objects_data:
                old_id = object_data['territory_id']
                FlatPage.objects.create(
                    h1=object_data['name'],
                    slug=slugify(object_data['alias']),
                    content=object_data['text'],
                    date_published=get_date(object_data['date']),
                    parent=region_pages[old_id]
                )

        # save_custom_pages()
        # create_news(data['posts'])
        # create_pages(data['static_pages'])
        # region_pages = create_regions(data['territories'])
        # create_region_objects(
        #     region_pages=region_pages,
        #     region_objects_data=data['objects']
        # )
        create_categories(data['categories'])
        create_products(data['products'])
        # fill_images_data()

        print('Was created {} categories, {} products, {} pages'.format(
            Category.objects.count(),
            Product.objects.count(),
            FlatPage.objects.count(),
        ))

    def connect_to_the_mysql_db(self) -> pymysql.connect:
        """Connection to the database and create the cursor."""
        try:
            conn = pymysql.connect(**self.MYSQL_CONFIG)
            return conn

        except pymysql.err.OperationalError:
            print('Entered incorrect password.')
            self.connect_to_the_mysql_db()
