import os, sys
import lxml.etree as etree
import xml.etree.ElementTree as ElementTree
from ... import get_findingaid
from django.conf import settings
from django.core.management.base import BaseCommand

ElementTree.register_namespace('ead', 'urn:isbn:1-931666-22-9')

server_args = (
    settings.MARKLOGIC_SERVER,
    settings.MARKLOGIC_USERNAME,
    settings.MARKLOGIC_PASSWORD,
    settings.PROXY_SERVER
)

class Command(BaseCommand):
    help = 'Regularize a finding aid, from the database or on disk.'

    def add_arguments(self, parser):
        parser.add_argument('path_or_identifier', nargs=1, type=str)

    def handle(self, *args, **options):
        # add namespace.
        namespace_transform = etree.XSLT(
            etree.parse(
                os.path.join(
                        'portal',
                        'xslt',
                        'dtd2schema.xsl'
                    )   
                )   
            )   

        # regularize.
        regularize_transform = etree.XSLT(
            etree.parse(
                os.path.join(
                        'portal',
                        'xslt',
                        'regularize.xsl'
                    )   
                )   
            )   

        # assume the command line argument is a path if a directory separator
        # is present. (To process a file in the current directory, pass it as
        # ./<filename.xml>)
        if os.sep in options['path_or_identifier'][0]:
            xml = etree.parse(options['path_or_identifier'][0])
            sys.stdout.write(
                etree.tostring(
                    regularize_transform(
                        namespace_transform(
                            xml
                        )
                    ),
                    encoding='utf-8', 
                    pretty_print=True
                ).decode('utf-8')
            )
        # otherwise assume the command line argument is an identifier- try to 
        # retrieve it from the database. Convert it to lxml etree for xslt
        # processing.
        else:
            xml = etree.fromstring(
                ElementTree.tostring(
                    get_findingaid(*server_args + (options['path_or_identifier'][0],)),
                    encoding='utf-8',
                    method='xml'
                ).decode('utf-8')
            )
            sys.stdout.write(
                etree.tostring(
                    regularize_transform(
                        xml
                    ),
                    encoding='utf-8', 
                    pretty_print=True
                ).decode('utf-8')
            )
