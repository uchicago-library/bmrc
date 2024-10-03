# your_app/management/commands/regenerate_renditions.py
# script generated with the help of an LLM
# to fix borken images after a databse import
# because `./manage.py wagtail_update_image_renditions` did not seem to solve it.
from django.core.management.base import BaseCommand
from wagtail.images.models import Image
from wagtail.images import get_image_model

class Command(BaseCommand):
    help = 'Regenerate Wagtail image renditions'

    def handle(self, *args, verbose=False, **kwargs):
        Image = get_image_model()  # Use the correct image model
        images = Image.objects.all()
        success_count = 0
        error_count = {}
        
        for image in images:
            for spec in ['width-350', 'width-500', 'width-900', 'fill-150x150', 'fill-250x250', 'fill-500x500']:  # Add all the specs you use in your templates
                try:
                    rendition = image.get_rendition(spec)
                    success_count += 1
                    if verbose:
                        self.stdout.write(self.style.SUCCESS(f'Regenerated renditions for {image.title}'))
                except Exception as e:
                    error_class = type(e).__name__  # Get the exception class name
                    error_count[error_class] = error_count.get(error_class, 0) + 1
                    if verbose:
                        self.stderr.write(self.style.ERROR(f"Error generating rendition for {image.title}: {str(e)}"))  # Use str(e) for the error message

        # Summary output
        self.stdout.write(self.style.SUCCESS(f'Successfully regenerated {success_count} renditions.'))
        for error, count in error_count.items():
            self.stdout.write(self.style.ERROR(f'Error: {error} - Count: {count}'))
