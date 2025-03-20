import math
import os
import random
import re
import urllib
import xml.etree.ElementTree as ElementTree

import lxml.etree as etree
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from . import get_collections, get_findingaid, get_search
from .models import (
    Archive,
    CuratedTopicIndexPage,
    CuratedTopicPage,
    PortalBasePage,
    PortalHomePage,
)

server_args = (
    settings.MARKLOGIC_SERVER,
    settings.MARKLOGIC_USERNAME,
    settings.MARKLOGIC_PASSWORD,
    settings.PROXY_SERVER,
)

##################
# XSLT FUNCTIONS #
##################

ns = etree.FunctionNamespace('https://lib.uchicago.edu/functions/')


def bmrc_search_url(context, ns, s):
    """EXSLT has str:encode-uri, but it behaves differently than
    urllib.parse.quote_plus. I add quote_plus() as an extention function in
    XSLT so that the transform can have access to the exact function that
    produces collection URIs when they're first added to MarkLogic."""

    # build the collection URI the same way Python does when we first load
    # finding aids into MarkLogic.
    uri = '{}{}'.format(ns, urllib.parse.quote_plus(s.strip()))

    # to streamline the XSLT, return the entire search URL. (note
    # double-quoting.)
    return '/portal/search/?f={}'.format(urllib.parse.quote_plus(uri))


ns['bmrc_search_url'] = bmrc_search_url

#####################
# UTILITY FUNCTIONS #
#####################


def get_portal_breadcrumbs():
    """Get breadcrumbs for the portal homepage and its ancestors."""
    breadcrumbs = []
    try:
        for a in PortalHomePage.objects.first().get_ancestors(True):
            if a.is_root() == False:
                breadcrumbs.append((a.url, a.title))
    except AttributeError:
        pass
    return breadcrumbs


def get_min_max_page_links(page, total_pages):
    min_page_link = page - math.floor(settings.MAX_PAGE_LINKS / 2)
    max_page_link = page + math.floor(settings.MAX_PAGE_LINKS / 2)

    if min_page_link < 1:
        min_page_link = 1
        max_page_link = min(min_page_link + (settings.MAX_PAGE_LINKS - 1), total_pages)

    if max_page_link > total_pages:
        max_page_link = total_pages
        min_page_link = max(1, max_page_link - (settings.MAX_PAGE_LINKS - 1))

    return min_page_link, max_page_link


def get_min_max_page_links_range(page, total_pages):
    min_page_link = page - math.floor(settings.MAX_PAGE_LINKS / 2)
    max_page_link = page + math.floor(settings.MAX_PAGE_LINKS / 2)

    if min_page_link < 1:
        min_page_link = 1
        max_page_link = min(min_page_link + (settings.MAX_PAGE_LINKS - 1), total_pages)

    if max_page_link > total_pages:
        max_page_link = total_pages
        min_page_link = max(1, max_page_link - (settings.MAX_PAGE_LINKS - 1))

    return range(min_page_link, max_page_link + 1)


def add_to_url_params(search_results, d):
    """
    Add a parameter to the current url params.

    Args:
       search_results: object returned from MarkLogic.
       d:              a dictionary, where the keys are parameters to add.

    Returns:
       a URL query string.
    """

    params = []
    if 'b' in search_results and search_results['b']:
        p = ('b', search_results['b'])
        if not p in params:
            params.append(p)
    if 'collections-active' in search_results:
        for c in search_results['collections-active']:
            params.append(('f', c[0]))
    if 'q' in search_results and search_results['q']:
        params.append(('q', search_results['q']))
    if 'sort' in search_results and search_results['sort']:
        params.append(('sort', search_results['sort']))
    for k, v in d.items():
        params.append((k, v))

    return urllib.parse.urlencode(params)


def clear_facets_from_url_params(search_results):
    """
    Clear all facets from current URL params.

    Args:
       search_results: object returned from MarkLogic.

    Returns:
        a URL query string.
    """
    params = []
    for p in ('q', 'sort'):
        if p in search_results and search_results[p]:
            params.append((p, search_results[p]))
    return urllib.parse.urlencode(params)


def remove_from_url_params(search_results, d):
    """
    Remove a specific facet from the current URL params.

    Args:
       search_results: object returned from MarkLogic.
       d:              dictionary, where the key is the parameter to remove.

    Returns:
        a URL query string.
    """
    params = []
    if 'b' in d:
        pass
    elif search_results['b']:
        params.append(('b', search_results['b']))
    if 'q' in d:
        pass
    elif search_results['q']:
        params.append(('q', search_results['q']))
    for c in search_results['collections-active']:
        if 'f' in d and d['f'] == c[0]:
            continue
        else:
            params.append(('f', c[0]))
    return urllib.parse.urlencode(params)


#########
# VIEWS #
#########


def browse(request):
    b = request.GET.get('b', '')
    page = int(request.GET.get('page', '1'))
    sort = request.GET.get('sort', 'relevance')

    start = (page - 1) * settings.PAGE_LENGTH
    stop = start + settings.PAGE_LENGTH

    titles = {
        'archives': 'ABrowsell Archives',
        'decades': 'Browse Decades',
        'organizations': 'Browse Organizations',
        'people': 'Browse People',
        'places': 'Browse Places',
        'topics': 'Browse Topics',
    }

    assert b in titles.keys()
    assert sort in ('alpha', 'alpha-dsc', 'relevance', 'shuffle')

    collections = get_collections(
        *server_args + ('https://bmrc.lib.uchicago.edu/{}/'.format(b),)
    )

    browse_results = []
    for k in collections.keys():
        label_unformated = k.replace('https://bmrc.lib.uchicago.edu/', '').split('/')[1]
        label = urllib.parse.unquote_plus(label_unformated)
        count = len(collections[k])
        if not label.startswith('BMRC Portal'):
            browse_results.append((label, count, k))

    total_pages = math.ceil(len(browse_results) / settings.PAGE_LENGTH)

    if sort == 'alpha':
        browse_results.sort(key=lambda i: i[0].lower())
    elif sort == 'alpha-dsc':
        browse_results.sort(key=lambda i: i[0].lower(), reverse=True)
    elif sort == 'relevance':
        browse_results.sort(key=lambda i: i[1], reverse=True)
    elif sort == 'shuffle':
        random.shuffle(browse_results)

    featured_curated_topic = CuratedTopicPage.featured_curated_topic()
    featured_curated_topic_index = CuratedTopicIndexPage.objects.first()

    return render(
        request,
        'portal/browse.html',
        {
            'b': b,
            'breadcrumbs': get_portal_breadcrumbs(),
            'browse_results': browse_results[start:stop],
            'featured_curated_topic': featured_curated_topic,
            'featured_curated_topic_index': featured_curated_topic_index,
            'page': page,
            'page_length': settings.PAGE_LENGTH,
            'page_links': get_min_max_page_links_range(page, total_pages),
            'search_results': {},
            'sort': sort,
            'start': start,
            'title': titles[b],
            'total_pages': total_pages,
            'total_results': len(browse_results),
            'portal_facets': PortalBasePage.portal_facets,
            'sort_options': PortalBasePage.sort_options,
        },
    )


def facet_view_all(request):
    """e.g. http://localhost:8000/facet_view_all/?q=chicago&a=https%3A%2F%2Fbmrc.lib.uchicago.edu%2Ftopics%2F"""
    a = request.GET.get('a', '')
    collections_active = request.GET.getlist('f')
    fsort = request.GET.get('fsort', 'relevance')
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'relevance')

    assert sort in ('alpha', 'alpha-dsc', 'relevance', 'shuffle')

    search_results = {}

    # TODO: remove this?
    # add active collections to search_results.
    # if collections_active:
    #     search_results['collections-active'] = []
    #     for c in collections_active:
    #         search_results['collections-active'].append([
    #             c,
    #             urllib.parse.unquote_plus(c.split('/')[4]),
    #             0
    #         ])

    facet_name = a.replace('https://bmrc.lib.uchicago.edu/', '').split('/')[0]
    assert facet_name in (
        'archives',
        'decades',
        'organizations',
        'people',
        'places',
        'topics',
    )

    title = facet_name.capitalize()

    search_results = get_search(
        *server_args + (q, sort, 0, 1, -1, collections_active, '')
    )

    # To simplify the XQuery, append additional elements to each list here.
    # element 4 = True if the facet is currently active, false if not.
    # element 5 = a URL query string with this element appended, for building
    #             links.
    out = []
    for f in search_results['active_' + facet_name]:
        out.append(f + [True, remove_from_url_params(search_results, {'f': f[0]})])
    for f in search_results['more_' + facet_name]:
        out.append(f + [False, add_to_url_params(search_results, {'f': f[0]})])

    if fsort == 'relevance':
        out.sort(key=lambda i: i[2], reverse=True)
    elif fsort == 'alpha':
        out.sort(key=lambda i: re.sub('^The ', '', i[1]).lower())
    elif fsort == 'alpha-dsc':
        out.sort(key=lambda i: re.sub('^The ', '', i[1]).lower(), reverse=True)
    elif fsort == 'shuffle':
        random.shuffle(out)

    return render(
        request,
        'portal/facet_view_all.html',
        {
            'a': a,
            'collection': out,
            'collection_active': collections_active,
            'fsort': fsort,
            'q': q,
            'search_results': search_results,
            'title': title,
        },
    )


def search(request):
    b = request.GET.get('b', '')
    collections = request.GET.getlist('f')
    page = int(request.GET.get('page', '1'))
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', '')
    start = (page - 1) * settings.PAGE_LENGTH
    stop = start + settings.PAGE_LENGTH

    if sort == '':
        if q == '':
            sort = 'alpha'
        else:
            sort = 'relevance'

    search_results = get_search(
        *server_args
        + (
            q,
            sort,
            start,
            settings.PAGE_LENGTH,
            settings.SIDEBAR_VIEW_MORE_FACET_COUNT,
            collections,
            b,
        )
    )

    search_results['query_string_without_sort'] = remove_from_url_params(
        search_results, {'sort': None}
    )
    search_results['query_string_without_page'] = remove_from_url_params(
        search_results, {'page': None}
    )

    for f in ('topics', 'people', 'organizations', 'places', 'decades', 'archives'):
        a = 'active_' + f
        for i in range(len(search_results[a])):
            search_results[a][i].append(
                remove_from_url_params(search_results, {'f': search_results[a][i][0]})
            )
        a = 'more_' + f
        for i in range(len(search_results[a])):
            search_results[a][i].append(
                add_to_url_params(search_results, {'f': search_results[a][i][0]})
            )

    # placeholder code to redirect to a single search result.
    if False:
        if search_results['total'] == 1:
            return redirect(
                '/portal/view/?{}'.format(
                    urllib.parse.urlencode({'id': search_results['results'][0]['uri']})
                )
            )

    total_pages = math.ceil(search_results['total'] / settings.PAGE_LENGTH)

    active_facets = bool(
        sum(
            (
                len(search_results['active_topics']),
                len(search_results['active_people']),
                len(search_results['active_organizations']),
                len(search_results['active_places']),
                len(search_results['active_decades']),
                len(search_results['active_archives']),
            )
        )
    )

    if q:
        title = 'Portal Search - {}'.format(q)
    else:
        title = 'Portal Search'

    # if this search includes an archive facet, get the logo, short title and
    # html for archive contact info.
    archivebox_address = archivebox_link = archivebox_logo = name = ''
    c = [
        c
        for c in collections
        if c.startswith('https://bmrc.lib.uchicago.edu/archives/')
    ]
    if c:
        s = urllib.parse.unquote_plus(
            c[0].replace('https://bmrc.lib.uchicago.edu/archives/', '')
        )
        for a in Archive.objects.all():
            if a.name == s:
                archivebox_address = a.address
                archivebox_link = a.link
                archivebox_logo = a.logo
                name = a.name

    return render(
        request,
        'portal/search.html',
        {
            'active_facets': active_facets,
            'all_active_facets': search_results['active_topics']
            + search_results['active_people']
            + search_results['active_organizations']
            + search_results['active_places']
            + search_results['active_decades']
            + search_results['active_archives'],
            'archivebox_address': archivebox_address,
            'archivebox_link': archivebox_link,
            'archivebox_logo': archivebox_logo,
            'breadcrumbs': get_portal_breadcrumbs(),
            'clear_facets_from_url_params': clear_facets_from_url_params(
                search_results
            ),
            'page': page,
            'page_length': settings.PAGE_LENGTH,
            'page_links': get_min_max_page_links_range(page, total_pages),
            'search_results': search_results,
            'sidebar_view_less_facet_count': settings.SIDEBAR_VIEW_LESS_FACET_COUNT,
            'sidebar_view_more_facet_count': settings.SIDEBAR_VIEW_MORE_FACET_COUNT,
            'name': name,
            'sort': sort,
            'start': start,
            'title': title,
            'total_pages': total_pages,
            'url_params_clear_facets': clear_facets_from_url_params(search_results),
            'portal_facets': PortalBasePage.portal_facets,
            'sort_options': PortalBasePage.sort_options,
        },
    )


def view(request):
    id = request.GET.get('id', '')

    if id == '':
        raise Http404()

    def t(filename):
        return etree.XSLT(
            etree.parse(os.path.join(os.path.dirname(__file__), 'xslt', filename))
        )

    tn = t('navigation.xsl')
    tv = t('view.xsl')

    try:
        xml = get_findingaid(*server_args + (id,))
    except ValueError:
        raise Http404()

    findingaid = tv(
        etree.fromstring(ElementTree.tostring(xml, encoding='utf8', method='xml'))
    )
    print("ORIGINAL FINDING AID")
    print(findingaid)

    try:
        title = ''.join(findingaid.xpath('//h1')[0].itertext())
    except IndexError:
        title = ''

    prefix = '.'.join(id.split('.')[:2])
    archivebox_address = archivebox_link = archivebox_logo = name = ''
    for a in Archive.objects.all():
        if a.finding_aid_prefix == prefix:
            try:
                archivebox_address = a.address
                archivebox_link = a.link
                archivebox_logo = a.logo
                name = a.name
            except IndexError:
                pass

    navigation = tn(findingaid)

    # Somehow a self closing div is being produced in the finding aid.
    # <div class="ead_titlepage"/>
    # This is breaking the html. So we replace it with a closing div tag.
    findingaid = re.sub(
        r'<div class="[^"]*"/>',
        lambda m: m.group(0).replace('/>', '></div>'),
        str(findingaid),
    )
    print("TRANSFORMED FINDING AID")
    print(findingaid)

    return render(
        request,
        'portal/view.html',
        {
            'archivebox_address': archivebox_address,
            'archivebox_link': archivebox_link,
            'archivebox_logo': archivebox_logo,
            'breadcrumbs': get_portal_breadcrumbs(),
            'findingaid_html': findingaid,
            'navigation_html': navigation,
            'search_results': [],
            'name': name,
            'title': title,
        },
    )
