import json, os, sys
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from portal import (get_browse_archives_from_file, get_browse_from_file,
                    get_browse_decades_from_file)
from portal.models import Archive

server_args = (
   settings.MARKLOGIC_SERVER,
   settings.MARKLOGIC_USERNAME,
   settings.MARKLOGIC_PASSWORD,
   settings.PROXY_SERVER
)

class Command(BaseCommand):
    help = 'Get browses for a file on disk.'

    def add_arguments(self, parser):
        parser.add_argument('browse', nargs=1, type=str)
        parser.add_argument('filepath', nargs=1, type=str)

    def handle(self, *args, **options):
        '''Get browses for testing.'''

        ARCHIVES = []
        for a in Archive.objects.all():
            ARCHIVES.append({
                'finding_aid_prefix': a.finding_aid_prefix,
                'name': a.name
            })

        if options['browse'][0] == 'https://bmrc.lib.uchicago.edu/organizations':
            sys.stdout.write(
                json.dumps(
                    get_browse_from_file(
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/organizations/{}',
                        '//ead:corpname[not(ancestor::ead:publisher) and not(ancestor::ead:repository)]',
                        {'ead': 'urn:isbn:1-931666-22-9'}
                    )
                )
            )
        elif options['browse'][0] == 'https://bmrc.lib.uchicago.edu/decades':
            sys.stdout.write(
                json.dumps(
                    get_browse_decades_from_file(
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/decades/{}'
                    )
                )
            )
        elif options['browse'][0] == 'https://bmrc.lib.uchicago.edu/archives':
            sys.stdout.write(
                json.dumps(
                    get_browse_archives_from_file(
                        ARCHIVES,
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/archives/{}'
                    )
                )
            )
        elif options['browse'][0] == 'https://bmrc.lib.uchicago.edu/people':
            sys.stdout.write(
                json.dumps(
                    get_browse_from_file(
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/people/{}',
                        ' | '.join((
                            '//ead:famname',
                            '//ead:name',
                            '//ead:persname'
                        )),
                        {'ead': 'urn:isbn:1-931666-22-9'}
                    )
                )
            )
        elif options['browse'][0] == 'https://bmrc.lib.uchicago.edu/places':
            sys.stdout.write(
                json.dumps(
                    get_browse_from_file(
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/places/{}',
                        '//ead:geogname',
                        {'ead': 'urn:isbn:1-931666-22-9'}
                    )
                )
            )
        elif options['browse'][0] == 'https://bmrc.lib.uchicago.edu/topics':
            sys.stdout.write(
                json.dumps(
                    get_browse_from_file(
                        options['filepath'][0],
                        'https://bmrc.lib.uchicago.edu/topics/{}',
                        ' | '.join((
                            '//ead:genreform',
                            '//ead:occupation',
                            '//ead:subject'
                        )),
                        {'ead': 'urn:isbn:1-931666-22-9'}
                    )
                )
            )
