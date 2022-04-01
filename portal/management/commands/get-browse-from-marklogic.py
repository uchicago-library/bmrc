import json
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from portal import get_collections

class Command(BaseCommand):
    help = 'Browse the portal by database collection.'

    def add_arguments(self, parser):
        parser.add_argument('database_collection_uri_startswith', nargs=1, type=str)

    def handle(self, *args, **options):
        self.stdout.write(
            json.dumps(
                get_collections(
                   settings.MARKLOGIC_SERVER,
                   settings.MARKLOGIC_USERNAME,
                   settings.MARKLOGIC_PASSWORD,
                   settings.PROXY_SERVER,
                   options['database_collection_uri_startswith'][0]
                )
            )
        )
