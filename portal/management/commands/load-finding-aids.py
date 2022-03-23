import io, json, os, sys
import lxml.etree as etree
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from portal import (get_archives_for_xml, get_collections_for_xml,
                    get_decades_for_xml, load_findingaid)
from portal.models import Archive

server_args = (
   settings.MARKLOGIC_SERVER,
   settings.MARKLOGIC_USERNAME,
   settings.MARKLOGIC_PASSWORD,
   settings.PROXY_SERVER
)

class Command(BaseCommand):
    help = 'Load finding aids into the BMRC Portal MarkLogic...'

    def add_arguments(self, parser):
        parser.add_argument('finding_aid_dir', nargs=1, type=str)

    def handle(self, *args, **options):
        '''Load finding aids into the BMRC Portal MarkLogic database.'''

        ARCHIVES = []
        for a in Archive.objects.all():
            ARCHIVES.append({
                'finding_aid_prefix': a.finding_aid_prefix,
                'name': a.name
            })

        sys.stdout.write('Building organization name browse...\n')
        organizations = get_collections_for_xml(
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/organizations/{}',
            '//ead:corpname[not(ancestor::ead:publisher) and not(ancestor::ead:repository)]',
            {'ead': 'urn:isbn:1-931666-22-9'}
        )
        sys.stdout.write('Building decade browse...\n')
        decades = get_decades_for_xml(
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/decades/{}'
        )
        sys.stdout.write('Building archives browse...\n')
        archives = get_archives_for_xml(
            ARCHIVES,
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/archives/{}'
        )
        sys.stdout.write('Building person browse...\n')
        people = get_collections_for_xml(
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/people/{}',
            ' | '.join((
                '//ead:famname',
                '//ead:name',
                '//ead:persname'
            )),
            {'ead': 'urn:isbn:1-931666-22-9'}
        )
        sys.stdout.write('Building place browse...\n')
        places = get_collections_for_xml(
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/places/{}',
            '//ead:geogname',
            {'ead': 'urn:isbn:1-931666-22-9'}
        )
        sys.stdout.write('Building topic browse...\n')
        topics = get_collections_for_xml(
            options['finding_aid_dir'][0],
            'https://bmrc.lib.uchicago.edu/topics/{}',
            ' | '.join((
                '//ead:occupation',
                '//ead:subject'
            )),
            {'ead': 'urn:isbn:1-931666-22-9'}
        )
        browses = {**archives, **decades, **organizations, **people, **places, **topics}
    
        for d in os.listdir(options['finding_aid_dir'][0]):
            for eadid in os.listdir(
                os.path.join(options['finding_aid_dir'][0], d)
            ):
                try:
                    transformed_xml = etree.parse(os.path.join(options['finding_aid_dir'][0], d, eadid))
                except etree.XMLSyntaxError:
                    continue
    
                collections = []
                for uri, eadids in browses.items():
                    if eadid in eadids:
                        collections.append(uri)
    
                with io.BytesIO(
                    etree.tostring(
                        transformed_xml, 
                        encoding='utf-8', 
                        method='xml'
                    )
                ) as fh:
                    sys.stdout.write('LOADING {}...\n'.format(eadid))
                    load_findingaid(
                        *server_args +
                        (
                            fh, 
                            eadid,
                            collections
                        )
                    )
