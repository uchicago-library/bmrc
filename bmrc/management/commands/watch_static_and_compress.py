# copied from here https://stackoverflow.com/questions/59339571/django-automatically-performing-the-collectstatic-command
# needs to run ./manage.py watch_static_and_compress &
# ./manage.py runserver 0.0.0.0:3000

import os
import time

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from watchfiles import watch


class Command(BaseCommand):
    help = "Automatically calls compress when the staticfiles get modified."

    def handle(self, *args, **options):
        print('WATCH_STATIC: Static file watchdog started.')
        #for changes in watch([str(x) for x in settings.STATICFILES_DIRS]):
        print(*settings.STATICFILES_DIRS)
        subdirectory_path = os.path.join(settings.STATICFILES_DIRS[0], 'css')
        for changes in watch(subdirectory_path):
            # print(f'WATCH_STATIC: {changes}')
            print('WATCH_STATIC: something got changed ')
            call_command("compress", interactive=False)