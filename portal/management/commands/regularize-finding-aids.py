import os, pathlib, shutil 
import lxml.etree as etree
import xml.etree.ElementTree as ElementTree
from django.core.management.base import BaseCommand

ElementTree.register_namespace('', 'urn:isbn:1-931666-22-9')

class Command(BaseCommand):
    help = 'Regularize a directory hierarchy of finding aids.'

    def add_arguments(self, parser):
        parser.add_argument('input_dir', nargs=1, type=str)
        parser.add_argument('output_dir', nargs=1, type=str)

    def handle(self, *args, **options):
        def replace_path(path, search, replace):
            """E.g. 
                '/data/web/ead/clone/portal/uoc/file.xml', 
                'data/web/ead/clone/portal', 
                '/home/jej/portal'
            """
            # get absolute paths, resolve symlinks. 
            p = pathlib.Path(os.path.realpath(path))
            s = pathlib.Path(os.path.realpath(search))
            r = pathlib.Path(os.path.realpath(replace))

            # confirm that search is a directory.
            assert os.path.isdir(str(s))
         
            # confirm that path starts with search.
            assert s.parts == p.parts[:len(s.parts)]

            # confirm that neither search or replace are desendants of each
            # other.
            assert s.parts != r.parts[:len(s.parts)]
            assert r.parts != s.parts[:len(r.parts)]

            # return a string with the old directory path replaced by the new
            # one.
            return os.path.join(*(r.parts + p.parts[len(s.parts):]))

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

        # confirm that all files in input directory are EAD.
        for root, dirs, files in os.walk(options['input_dir'][0]):
            for file in files:
                xml = etree.parse(os.path.join(root, file))
                assert xml.getroot().tag in ('{urn:isbn:1-931666-22-9}ead', 'ead')

        # if the output directory already exists, clear it and start fresh.
        if os.path.isdir(options['output_dir'][0]):
            shutil.rmtree(options['output_dir'][0])

        # process files.
        for root, dirs, files in os.walk(options['input_dir'][0]):
            for file in files:
                print(file)

                filepath_a = os.path.abspath(os.path.join(root, file))
                filepath_b = replace_path(
                    os.path.join(root, file),
                    options['input_dir'][0],
                    options['output_dir'][0]
                )

                # make new directories. 
                try:
                    os.makedirs((os.path.dirname(filepath_b)))
                except FileExistsError:
                    pass

                # get XML string. 
                xml_string = etree.tostring(
                    regularize_transform(
                        namespace_transform(
                            etree.parse(filepath_a)
                        )
                    ),
                    encoding='utf-8', 
                    pretty_print=True
                ).decode('utf-8')

                # write it using ElementTree to get namespaces to output correctly.
                xml = ElementTree.fromstring(xml_string)
                ElementTree.ElementTree(xml).write(
                    filepath_b,
                    encoding='utf-8',
                    xml_declaration=True
                )
