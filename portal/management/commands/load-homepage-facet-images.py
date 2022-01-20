import json, os, sys, willow

from django.core.files.images import get_image_dimensions, ImageFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from portal.models import Archive
from wagtail.images.models import Image

class Command(BaseCommand):
    help = 'Load images for the homepage facets into Wagtail.'

    def add_arguments(self, parser):
        parser.add_argument('image_dir', nargs=1, type=str)

    def handle(self, *args, **options):
        # Load logos into Wagtail, if they don't already exist. 

        for i in os.listdir(options['image_dir'][0]):
            path = os.path.join(options['image_dir'][0], i)

            for j in Image.objects.filter(title=i):
                j.delete()

            if not Image.objects.filter(title=i).exists():
                with open(
                    os.path.join(
                        options['image_dir'][0], 
                        i
                    ), 
                    'rb'
                ) as f:
                    width, height = get_image_dimensions(f)
                    Image(
                        title=i,
                        file=ImageFile(f, name=i),
                        width=width,
                        height=height
                    ).save()
