import os
import glob
from PIL import Image as pillow_image

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from django.conf import settings

from images.models import Image
from pages.models import Page

from stroyprombeton.models import Category

IMAGES_ROOT_FOLDER_NAME = os.path.join(settings.MEDIA_ROOT, 'category_images')


def create_image_models():

    def iter_dirs(path: str):
        return (dir_ for dir_ in os.scandir(path) if dir_.is_dir())

    def iter_files(path: str):
        return (file_ for file_ in os.scandir(path) if file_.is_file())

    def get_page(category_id: int) -> Page:
        product_ = Category.objects.filter(id=category_id).first()
        return product_.page if product_ else None

    def create_image_model(file_, category_id: int, slug):
        file_short_name, _ = os.path.splitext(file_.name)

        # create Image model object based on current image
        page = get_page(category_id=category_id)

        if not page:
            return
        # don't use bulk create, because save() isn't hooked with it
        # http://bit.ly/django_bulk_create

        Image.objects.create(
            model=page,
            # autoincrement file names: '1.jpg', '2.jpg' and so on
            slug=slug,
            image=ImageFile(open(file_.path, mode='rb')),
            is_main=(file_short_name == 'main')
        )

    def convert_png_to_jpeg(path):
        file_short_name, _ = os.path.splitext(path)

        image = pillow_image.open(path).convert('RGBA')
        image_data = image.load()

        # Convert black background color to white.
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                if image_data[x, y] == (0, 0, 0, 0):
                    image_data[x, y] = (255, 255, 255, 255)

        image.save('{}.jpg'.format(file_short_name), 'JPEG')
        os.remove(path)

    for path in glob.glob(os.path.join(IMAGES_ROOT_FOLDER_NAME, '**/*.png'), recursive=True):
        convert_png_to_jpeg(path)

    # run over every image in every folder
    for dir_ in iter_dirs(IMAGES_ROOT_FOLDER_NAME):
        for slug_index, file in enumerate(iter_files(dir_.path)):
            create_image_model(
                file_=file,
                category_id=int(dir_.name),
                slug=str(slug_index)
            )
    # old folder stays in fs as backup of old photos


class Command(BaseCommand):

    def handle(self, *args, **options):
        create_image_models()
