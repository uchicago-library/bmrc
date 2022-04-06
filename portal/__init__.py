import functools, io, json, os, re, requests, requests_cache, requests_toolbelt, sys, urllib
import lxml.etree as etree

#import config.default

from xml.etree import ElementTree
from collections import namedtuple
ElementTree.register_namespace('search', 'http://marklogic.com/appservices/search')

def merge_dicts_with_lists(a, b):
    '''Merge dicts of lists. Given two dicts with list values, return
    a new dict with keys from either input list, and values containing
    a unique list of elements from either input dict.

       Params:
           a, b - dicts of lists, e.g.:
           {
             'one': ['a', 'b', 'c']
             'two': ['c', 'd', 'e']
           },
           {
             'one': ['c', 'd', 'e'],
             'three': ['f', 'g', 'h']
           }
       Returns:
           A new dict, e.g.:
           {
             'one': ['a', 'b', 'c', 'd', 'e'],
             'two': ['c', 'd', 'e'],
             'three': ['f', 'g', 'h']
           }
    '''
    assert all([type(v) == list for v in a.values()])
    assert all([type(v) == list for v in b.values()])

    d = {}
    for k in set(a.keys()) | set(b.keys()):
        d[k] = list(set(a.get(k, [])) | set(b.get(k, [])))
    return d

def merge_most_frequently_occurring_capitalizations(d):
    '''Collapse entries in a browse list based on their most popular
    capitalizations.

       Params:
           d - a browse dict, e.g.:
           {
             'https://bmrc.lib.uchicago.edu/Clark%20Kent': ['id_1', 'id_2', 'id_3'],
             'https://bmrc.lib.uchicago.edu/clark%20kent': ['id_3', 'id_4', 'id_5']
           }
        Returns:
           A new dict, e.g.:
           {
             'https://bmrc.lib.uchicago.edu/clark%20kent': ['id_1', 'id_2', id_3', 'id_4', 'id_5']
           }
    '''
    lookup = {}
    for k in d.keys():
        lookup_key = k.upper()
        if not lookup_key in lookup:
            lookup[lookup_key] = []
        lookup[lookup_key].append(k)

    output = {}
    for keys in lookup.values():
        # the key with the most entries in dict is the most common
        # capitalization.
        cap_k = sorted([(len(d[k]), k) for k in keys])[-1][1]

        output[cap_k] = []

        for k in keys:
            for ead_id_title_pair in d[k]:
                if ead_id_title_pair not in output[cap_k]:
                    output[cap_k].append(ead_id_title_pair)
    return output

def setup_cache():
    return
    requests_cache.install_cache(
        allowable_methods=('GET', 'POST'),
        expire_after=3600
    )

def clear_cache():
    requests_cache.clear()

def get_finding_aid_from_disk(filepath):
    '''Get the XML for a given finding aid from disk.

    Params:
        filepath - a string, the path to an EAD file on disk.

    Returns:
        An lxml XML document. 
    '''
    return etree.parse(filepath).getroot()

def get_browse_archives_from_file(archive_config, filepath, uri_format_str):
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
    archives = {bmrc_uri: []}

    eadid = os.path.basename(filepath)

    xml = get_finding_aid_from_disk(filepath)
    
    # Confirm that the document passed to this function is namespaced
    # EAD 2002.
    assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

    prefix = '.'.join(eadid.split('.')[:2])
    
    uri = uri_format_str.format(
        urllib.parse.quote_plus(archive_lookup[prefix])
    )
    if not uri in archives:
        archives[uri] = []
    if not eadid in archives[uri]:
        archives[uri].append(eadid)
    if not eadid in archives[bmrc_uri]:
        archives[bmrc_uri].append(eadid)

    return archives

def get_browse_archives_from_dir(archive_config, dir, uri_format_str):
    '''Process finding aids to get Marklogic collection data for decade browses.

       Args:
         dir             e.g. 'findingaids'
         uri_format_str  e.g. 'https://bmrc.lib.uchicago.edu/decades/{}'

       Returns: 
         dict
    '''
    browses = []
    for root, subdirs, filenames in os.walk(dir):
        for filename in filenames:
            if filename.startswith('BMRC') and filename.endswith('.xml'):
                eadid = filename
                try:
                    browses.append(
                        get_browse_archives_from_file(
                            archive_config,
                            os.path.join(root, filename),
                            uri_format_str
                        )
                    )
                except ValueError:
                    continue
    return functools.reduce(merge_dicts_with_lists, browses)

def get_browse_from_file(filepath, uri_format_str, xpath, namespaces):
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

    xml = get_finding_aid_from_disk(filepath)
    assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

    eadid = os.path.basename(filepath)

    browse = {}
    for el in xml.xpath(xpath, namespaces=namespaces):
        # get all descendant text nodes, normalize and trim whitespace.
        k = ' '.join(''.join(el.itertext()).split())
        if k == '':
            continue

        u = uri_format_str.format(urllib.parse.quote_plus(k))
        if not u in browse:
            browse[u] = []
        if not eadid in browse[u]:
            browse[u].append(eadid)
    return browse


def get_browse_from_dir(dir, uri_format_str, xpath, namespaces):
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

    browses = []
    for collection in os.listdir(dir):
        for eadid in os.listdir(os.path.join(dir, collection)):
            try:
                browses.append(
                    get_browse_from_file(
                        os.path.join(dir, collection, eadid),
                        uri_format_str,
                        xpath,
                        namespaces
                    )
                )
            except ValueError:
                continue
    output = functools.reduce(merge_dicts_with_lists, browses)
    output = merge_most_frequently_occurring_capitalizations(output)
    return output

def get_browse_decades_from_file(filepath, uri_format_str):
    '''Process finding aids to get Marklogic collection data for decade browses.

       Args:
         filepath        path to EAD file on disk. 
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

    xml = get_finding_aid_from_disk(filepath)

    eadid = os.path.basename(filepath)

    # Confirm that the document passed to this function is namespaced
    # EAD 2002.
    assert xml.tag == '{urn:isbn:1-931666-22-9}ead'

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
            if not eadid in decade_browse[uri]:
                decade_browse[uri].append(eadid)
    return decade_browse

def get_browse_decades_from_dir(dir, uri_format_str):
    '''Process finding aids to get Marklogic collection data for decade browses.

       Args:
         dir             e.g. 'findingaids'
         uri_format_str  e.g. 'https://bmrc.lib.uchicago.edu/decades/{}'

       Returns: 
         dict
    '''
    browses = []
    for collection in os.listdir(dir):
        for eadid in os.listdir(os.path.join(dir, collection)):
            try:
                browses.append(
                    get_browse_decades_from_file(
                        os.path.join(dir, collection, eadid),
                        uri_format_str
                    )
                )
            except ValueError:
                continue
    return functools.reduce(merge_dicts_with_lists, browses)

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

def delete_findingaids(server, username, password, proxy_server):
    """Delete all finding aids in the system.

    Args:
        server:          The Marklogic server, with port number. 
        username:        Username for Marklogic.
        password:        Password for Marklogic.
        proxy_server:    A proxy server for connecting to Marklogic (You may
                         find this useful for local development.)
    """
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
            'delete_findingaids.xqy'
        )
    ) as f:
        r = requests.post(
            '{}/v1/eval'.format(
                server
            ),
            auth = (username, password),
            data = {
                'xquery': f.read()
            },
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            proxies=proxies
        )
        return r.status_code

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
