import io, json, os, re, requests, requests_cache, requests_toolbelt, sys, urllib
import lxml.etree as etree

#import config.default

from xml.etree import ElementTree
from collections import namedtuple
#ElementTree.register_namespace('ead', 'urn:isbn:1-931666-22-9')
ElementTree.register_namespace('search', 'http://marklogic.com/appservices/search')

# load global variables to connect to marklogic (e.g. username,
# password)

# get config.yaml. 
# get institutions.

def setup_cache():
    return
    requests_cache.install_cache(
        allowable_methods=('GET', 'POST'),
        expire_after=3600
    )

def clear_cache():
    requests_cache.clear()

def get_transformed_xml(fname):
    '''Add a namespace to the given EAD 2002 and return an ElementTree.'''
    return etree.parse(fname).getroot()

def get_archives_for_xml(archive_config, dir, uri_format_str):
    '''Get a dict of finding aids grouped by archive.

       Params:
           archive_config  - a list of dicts, data about archives from the
                             configuration for this app.
           dir             - a string, the full path to the directory
                             containing those finding aids. This directory may 
                             contain subdirectories (e.g. for storing each
                             archive's finding aids together) however, this 
                             function will use the finding aid prefix to
                             determine which archive produced the finding aid.
           uri_format_str  - a string, the format string to generate a unique
                             identifier for each archive.

        Returns:
            A dict, where each key is the unique identifier for the archive
            and the value is a list of EADIDs produced by that institution.
    '''

    archive_lookup = {}
    for a in archive_config:
        archive_lookup[a['finding_aid_prefix']] = a['name']

    bmrc_uri = uri_format_str.format(
        urllib.parse.quote_plus('BMRC Portal')
    )
    archives = {
        bmrc_uri: []
    }

    for root, subdirs, filenames in os.walk(dir):
        for filename in filenames:
            if filename.startswith('BMRC') and filename.endswith('.xml'):
                eadid = filename

                try:
                    xml = get_transformed_xml(
                        os.path.join(root, eadid)
                    )
                except ValueError:
                    continue
    
                # Confirm that the document passed to this function is namespaced
                # EAD 2002.
                assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

                prefix = '.'.join(eadid.split('.')[:2])
    
                uri = uri_format_str.format(
                    urllib.parse.quote_plus(archive_lookup[prefix])
                )
                if not uri in archives:
                    archives[uri] = []
                archives[uri].append(eadid)
                archives[bmrc_uri].append(eadid)

    return archives

def get_collections_for_xml(dir, uri_format_str, xpath, namespaces):
    '''Process finding aids to get Marklogic collection data for browses.

       Args:
         dir             e.g. 'findingaids'
         uri_format_str  e.g. 'https://bmrc.lib.uchicago.edu/places/{}'
         xpath           e.g. '//ead:geogname'

       Returns: 
         A Python dictionary-

         Keys are a URI built from a normalized version of the browse value,
         using the most frequently occurring capitalization. Dictionary 
         values are a list of EADIDs containing that key.

         Values are normalized by first concatenating all descendant text nodes
         (not just immediate children) of each found element. Strip leading and
         trailing whitespace, and replace all whitespace inside each string
         with a single space. 

         The most often occurring capitalization of that normalized value
         is quoted with urllib.parse.quote_plus() and embedded in the
         uri_format_str param. For example, with a uri_format_str of
         'https://bmrc.lib.uchicago.edu/people/{}', a resulting browse URI
         might be 'https://bmrc.lib.uchicago.edu/people/Jane+Doe'.
    '''

    browse_label_candidates = {}
    browse = {}

    for collection in os.listdir(dir):
        for eadid in os.listdir(os.path.join(dir, collection)):
            try:
                xml = get_transformed_xml(
                    os.path.join(dir, collection, eadid)
                )
            except ValueError:
                continue

            # Confirm that the document passed to this function is namespaced
            # EAD 2002.
            assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

            for el in xml.xpath(xpath, namespaces=namespaces):
                # get all descendant text nodes, normalize and trim whitespace.
                label_candidate = ' '.join(''.join(el.itertext()).split())

                if label_candidate == '':
                    continue

                # convert the candidate string to uppercase for a temporary key.
                key = label_candidate.upper()

                if not key in browse_label_candidates:
                    browse_label_candidates[key] = []
                browse_label_candidates[key].append(label_candidate)

                if not key in browse:
                    browse[key] = []
                if not eadid in browse[key]:
                    browse[key].append(eadid)

    # find the most frequently occuring capitalization, and use that to build a
    # definitive URI for the keys of the output dictionary.
    def most_frequent(l): 
        return max(set(l), key = l.count)

    output = {}
    for key, eadids in browse.items():
        uri = uri_format_str.format(
            urllib.parse.quote_plus(
                most_frequent(browse_label_candidates[key])
            )
        )
        output[uri] = eadids
    return output

def get_decades_for_xml(dir, uri_format_str):
    '''Process finding aids to get Marklogic collection data for decade browses.

       Args:
         dir             e.g. 'findingaids'
         uri_format_str  e.g. 'https://bmrc.lib.uchicago.edu/decades/{}'

       Returns: 
         A Python dictionary-

         Keys are a URI built from a normalized version of the browse value,
         using the most frequently occurring capitalization. Dictionary 
         values are a list of EADIDs containing that key.

         Values are normalized by first concatenating all descendant text nodes
         (not just immediate children) of each found element. Strip leading and
         trailing whitespace, and replace all whitespace inside each string
         with a single space. 

         The most often occurring capitalization of that normalized value
         is quoted with urllib.parse.quote_plus() and embedded in the
         uri_format_str param. For example, with a uri_format_str of
         'https://bmrc.lib.uchicago.edu/people/{}', a resulting browse URI
         might be 'https://bmrc.lib.uchicago.edu/people/Jane+Doe'.
    '''

    def lexer(text):
        token = namedtuple('Token', ['type','value'])
    
        YEAR = r'(?P<YEAR>[0-9]{4})'
        COMMA = r'(?P<COMMA>,)'
        DASH = r'(?P<DASH>-)'
    
        tokenizer = re.compile('|'.join([YEAR, COMMA, DASH]))
        for m in tokenizer.finditer(text):
            yield token(m.lastgroup, m.group())

    decade_browse = {}

    for collection in os.listdir(dir):
        for eadid in os.listdir(os.path.join(dir, collection)):
            try:
                xml = get_transformed_xml(
                    os.path.join(dir, collection, eadid)
                )
            except ValueError:
                continue

            # Confirm that the document passed to this function is namespaced
            # EAD 2002.
            assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

            # what is xpath for dates?
            # ignore type=bulk?
            # check normal attribute?
            for el in xml.xpath('//ead:unitdate[not(@type="bulk")]', namespaces={'ead': 'urn:isbn:1-931666-22-9'}):
                # get all descendant text nodes, normalize and trim whitespace.
                node_text = ' '.join(''.join(el.itertext()).split())

                # get tokens.
                tokens = []
                for token in lexer(node_text):
                    tokens.append(token)

                # convert tokens to a list of years.
                years = []
                for t in range(len(tokens)):
                    if tokens[t].type == 'YEAR':
                        if len(years) == 0:
                            years.append(int(tokens[t].value))
                        elif tokens[t-1].type == 'COMMA':
                            years.append(int(tokens[t].value))
                        elif tokens[t-1].type == 'DASH':
                            y = years[-1] + 1
                            while y <= int(tokens[t].value):
                                years.append(y)
                                y += 1

                # convert to list of decades.
                decades = []
                for year in years:
                    decades.append('{}0s'.format(str(year)[:3]))
                decades = sorted(list(set(decades)))
 
                for decade in decades:
                    uri = uri_format_str.format(decade)
                    if not uri in decade_browse:
                        decade_browse[uri] = []
                    decade_browse[uri].append(eadid)
    return decade_browse

def get_findingaid(server, username, password, proxy_server, uri):
    """Get a finding aid from Marklogic.
  
    Args: 
        server:        The Marklogic server, with port number. 
        username:      Username for Marklogic.
        password:      Password for Marklogic.
        proxy_server:  A running proxy server for connecting to Marklogic (You
                       may find this useful for local development.)
        uri:           Marklogic URI for this finding aid.

    Returns:
        XML as ElementTree.
    """
    setup_cache()

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    r = requests.get(
        '{}/v1/documents?{}'.format(
            server,
            urllib.parse.urlencode({
                'uri': uri
            })
        ),
        auth=(username, password),
        headers={
            'Content-Type': 'application/xml'
        },
        proxies=proxies
    )

    if r.status_code == 404:
        raise ValueError
    else: 
        return ElementTree.fromstring(r.text)

def delete_findingaid(server, username, password, proxy_server, uri):
    """Delete a finding aid from Marklogic.

    Args:
        server:        The Marklogic server, with port number. 
        username:      Username for Marklogic.
        password:      Password for Marklogic.
        proxy_server:  A proxy server for connecting to
                       Marklogic (You may find this useful for
                       local development.)
        uri:           Marklogic URI for this finding aid.
    """

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    r = requests.delete(
        '{}/v1/documents?{}'.format(
            server,
            urllib.parse.urlencode({
                'uri': uri
            })
        ),
        auth=(username, password),
        proxies=proxies
    )

    assert r.status_code == 204

def load_findingaid(server, username, password, proxy_server, fh, uri, collections):
    """Load a finding aid into Marklogic.

    Args:
        server:        The Marklogic server, with port number. 
        username:      Username for Marklogic.
        password:      Password for Marklogic.
        proxy_server:  A proxy server for connecting to
                       Marklogic (You may find this useful for
                       local development.)
        fh:            File to upload.
        uri:           Marklogic URI for this finding aid.
        collections:   A list of collections to add this finding aid to.
    """

    url_params = [
        ('uri', uri)
    ]
    for collection in collections:
        url_params.append(
            ('collection', collection)
        )

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    r = requests.put(
        '{}/v1/documents?{}'.format(
            server,
            urllib.parse.urlencode(url_params)
        ),
        auth=(username, password),
        data = fh.read(),
        headers={
            'Content-Type': 'application/xml'
        },
        proxies=proxies
    )

    assert r.status_code in (201, 204)

def get_collection(server, username, password, proxy_server, docs, b, sort, limit):
    """Get collections and finding aids from Marklogic- this is more complicated, 
       its for the sidebar.

    Args:
        server:          The Marklogic server, with port number. 
        username:        Username for Marklogic.
        password:        Password for Marklogic.
        proxy_server:    A proxy server for connecting to Marklogic (You may
                         find this useful for local development.)
        docs:            Get collections for this list of documents. 
        b:               Search for collections beginning with this string.
        sort:            Sort.
        limit:           Limit.

    Returns:
        Returns a dictionary, where keys are the short identifier for a
        collection (e.g. "chm", for the Chicago History Museum.) Each key
        includes an array of finding aids, where each element itself contains
        an array with two values. The first is an identifier for the finding
        aid, and the second is a title string.

        E.g.:
        {
            "bronzeville": [
                [
                    "bronzeville/finding_aid_identifier_1",
                    "Bronzeville Finding Aid #1 Title"
                ],
                [
                    "bronzeville/finding_aid_identifier_2",
                    "Bronzeville Finding Aid #2 Title"
                ]
            ],
            "chm": [
                [
                    "chm/finding_aid_identifier_1",
                    "Chicago History Museum Finding Aid #1 Title"
                ],
                [
                    "chm/finding_aid_identifier_2",
                    "Chicago History Museum Finding Aid #2 Title"
                ]
            ],
        }
    """
    #setup_cache()

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    with open(
        os.path.join(
            os.path.dirname(__file__),
            'xquery',
            'get_collection.xqy'
        )
    ) as f:
        r = requests.post(
            '{}/v1/eval'.format(
                server
            ),
            auth = (username, password),
            data = {
                'vars': json.dumps({'b': b, 'docs': docs, 'sort': sort, 'limit': limit}),
                'xquery': f.read()
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            proxies=proxies
        )
    try:
        multipart_data = requests_toolbelt.multipart.decoder.MultipartDecoder.from_response(r)
    except requests_toolbelt.multipart.decoder.NonMultipartContentTypeException:
        print(r.content)
        sys.exit()
    try:  
        return json.loads(multipart_data.parts[0].content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        print(r.content)
        sys.exit()

def get_collections(server, username, password, proxy_server, collection):
    """Get collections and finding aids from Marklogic.

    Args:
        server:          The Marklogic server, with port number. 
        username:        Username for Marklogic.
        password:        Password for Marklogic.
        proxy_server:    A proxy server for connecting to Marklogic (You may
                         find this useful for local development.)
        collection:      Search for collections beginning with this string.

    Returns:
        Returns a dictionary, where keys are the short identifier for a
        collection (e.g. "chm", for the Chicago History Museum.) Each key
        includes an array of finding aids, where each element itself contains
        an array with two values. The first is an identifier for the finding
        aid, and the second is a title string.

        E.g.:
        {
            "bronzeville": [
                [
                    "bronzeville/finding_aid_identifier_1",
                    "Bronzeville Finding Aid #1 Title"
                ],
                [
                    "bronzeville/finding_aid_identifier_2",
                    "Bronzeville Finding Aid #2 Title"
                ]
            ],
            "chm": [
                [
                    "chm/finding_aid_identifier_1",
                    "Chicago History Museum Finding Aid #1 Title"
                ],
                [
                    "chm/finding_aid_identifier_2",
                    "Chicago History Museum Finding Aid #2 Title"
                ]
            ],
        }
    """
    setup_cache()

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    with open(
        os.path.join(
            os.path.dirname(__file__),
            'xquery',
            'get_collections.xqy'
        )
    ) as f:
        r = requests.post(
            '{}/v1/eval'.format(
                server
            ),
            auth = (username, password),
            data = {
                'vars': json.dumps({'browse': collection}),
                'xquery': f.read()
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            proxies=proxies
        )

    multipart_data = requests_toolbelt.multipart.decoder.MultipartDecoder.from_response(r)
    return json.loads(multipart_data.parts[0].content)

def get_collection_document_matrix(server, username, password, proxy_server):
    """Get collections and finding aids from Marklogic.

    Args:
        server:          The Marklogic server, with port number. 
        username:        Username for Marklogic.
        password:        Password for Marklogic.
        proxy_server:    A proxy server for connecting to Marklogic (You may
                         find this useful for local development.)
    """
    # setup_cache()

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    with open(
        os.path.join(
            os.path.dirname(__file__),
            'xquery',
            'get_collection_document_matrix.xqy'
        )
    ) as f:
        r = requests.post(
            '{}/v1/eval'.format(
                server
            ),
            auth = (username, password),
            data = {
                'vars': json.dumps({}),
                'xquery': f.read()
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            proxies=proxies
        )

    multipart_data = requests_toolbelt.multipart.decoder.MultipartDecoder.from_response(r)
    return json.loads(multipart_data.parts[0].content)

def get_search(server, username, password, proxy_server, q, sort, start, page_length, sidebar_facet_limit, collections, b):
    """Get a search result from Marklogic.
    
    Params: 
        server                    The Marklogic server, with port number. 
        username                  Username for Marklogic.
        password                  Password for Marklogic.
        proxy_server              A proxy server for connecting to Marklogic
                                  (You may find this useful for local
                                  development.)
        q                         Query to submit to Marklogic.
        sort                      Sort for search results.
        start                     An integer, start from this result.
        page_length               An integer, include at most this many
                                  results.
        sidebar_facet_limit       Limit number of links for each sidebar group.
        collections               A list of collections to restrict the search
                                  to.
     
    Returns:
        XML as ElementTree.
    """

    #if exactphrase:
    #    q = '"{}"'.format(q)

    # setup_cache()

    if proxy_server:
        proxies = {
            'http': 'socks5://{}'.format(proxy_server),
            'https': 'socks5://{}'.format(proxy_server)
        }
    else:
        proxies = {}

    with open(
        os.path.join(
            os.path.dirname(__file__),
            'xquery',
            'get_search.xqy'
        )
    ) as f:
        r = requests.post(
            '{}/v1/eval'.format(
                server
            ),
            auth = (username, password),
            data = {
                'vars': json.dumps({'b': b, 'collections_active_raw': collections, 'q': q, 'size': page_length, 'sidebar-facet-limit': sidebar_facet_limit, 'sort': sort, 'start': start}),
                'xquery': f.read()
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            proxies=proxies
        )

    try:
        multipart_data = requests_toolbelt.multipart.decoder.MultipartDecoder.from_response(r)
    except requests_toolbelt.multipart.decoder.NonMultipartContentTypeException:
        print(r.content)
        sys.exit()
    try:  
        return json.loads(multipart_data.parts[0].content.decode('utf-8'))
    except json.decoder.JSONDecodeError:
        print(r.content)
        sys.exit()
