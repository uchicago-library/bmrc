import json, sys
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from portal import get_collections, delete_findingaid

class Command(BaseCommand):
    help = 'Delete all finding aids from the BMRC Portal MarkLogic database.'

    def __init__(self, *args, **kwargs):
        self.server_args = (
           settings.MARKLOGIC_SERVER,
           settings.MARKLOGIC_USERNAME,
           settings.MARKLOGIC_PASSWORD,
           settings.PROXY_SERVER
        )
        super(Command, self).__init__(*args, **kwargs)
    def handle(self, *args, **options):
        collections = get_collections(
            *self.server_args + ('https://bmrc.lib.uchicago.edu/archives/',)
        )
        for collection, findingaids in collections.items():
            for findingaid in findingaids:
                sys.stdout.write('DELETING {}...\n'.format(findingaid[0]))
                delete_findingaid(*self.server_args + (findingaid[0],))
