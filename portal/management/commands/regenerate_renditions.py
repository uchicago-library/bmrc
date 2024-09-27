# your_app/management/commands/regenerate_renditions.py
from django.core.management.base import BaseCommand
from wagtail.images.models import Image
from wagtail.images import get_image_model

class Command(BaseCommand):
    help = 'Regenerate Wagtail image renditions'

    def handle(self, *args, **kwargs):
        Image = get_image_model()  # Use the correct image model
        images = Image.objects.all()
        for image in images:
            for spec in ['width-350', 'width-500', 'width-900', 'fill-150x150', 'fill-250x250', 'fill-500x500']:  # Add all the specs you use in your templates
                try:
                    rendition = image.get_rendition(spec)
                    # image.get_renditions()  # This will regenerate the renditions
                    self.stdout.write(self.style.SUCCESS(f'Regenerated renditions for {image.title}'))
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Error generating rendition for {image.title}: {e}"))
