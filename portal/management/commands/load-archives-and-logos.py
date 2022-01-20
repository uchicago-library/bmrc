import json, os, sys, willow

from django.core.files.images import get_image_dimensions, ImageFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from portal.models import Archive
from wagtail.images.models import Image

class Command(BaseCommand):
    help = 'Load archive logos from a directory and archive data from JSON.'

    def add_arguments(self, parser):
        parser.add_argument('archive_logo_dir', nargs=1, type=str)
        parser.add_argument('json_data_file', nargs=1, type=str)

    def handle(self, *args, **options):
        # Load JSON data.
        with open(options['json_data_file'][0]) as f:
            ARCHIVES = json.load(f)

        # Delete all images with names starting with "BMRC."
        for i in Image.objects.all():
            if i.title.startswith('BMRC.'):
                i.delete()
    
        # Load logos into Wagtail.
        for i in os.listdir(options['archive_logo_dir'][0]):
            if i.startswith('BMRC.'):
                path = os.path.join(options['archive_logo_dir'][0], i)
    
                with open(os.path.join(options['archive_logo_dir'][0], i), 'rb') as f:
                    width, height = get_image_dimensions(f)
    
                    Image(
                        title=i,
                        file=ImageFile(f, name=i),
                        width=width,
                        height=height
                    ).save()
   
        # Delete all Archive objects. 
        Archive.objects.all().delete()

        # Look up logo images and add new Archive objects.
        for a in ARCHIVES:
            logo = None
            if a['finding_aid_prefix'] != 'BMRC':
                for i in Image.objects.all():
                    if i.title.startswith(a['finding_aid_prefix']):
                        logo = i

            Archive(
                name=a['name'],
                address=a['archivebox_address'],
                link=a['archivebox_link'],
                logo=logo,
                spotlight=a['member_spotlight_html'],
                finding_aid_prefix=a['finding_aid_prefix'],
                is_member=True
            ).save()
