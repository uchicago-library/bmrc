from django.conf import settings
from django.core.management.base import BaseCommand
from portal import delete_findingaids

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
        assert delete_findingaids(*self.server_args) == 200
