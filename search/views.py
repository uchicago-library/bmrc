import re

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from wagtail.contrib.search_promotions.models import Query
from wagtail.models import Page

PAGE_TYPE_MAPPING = {
    '/portal/curated/': 'Curated Topic',
    '/portal/exhibits/': 'Exhibits',
    '/news/': 'News',
    '/about/': 'About the BMRC',
    '/events/': 'Events',
    '/research-notes/': 'Research Notes',
    '/programs/': 'Programs',
    '/resources/': 'Resources',
    '/portal/help/': 'Research Help',
}


def get_page_type(url):
    """Determine page type based on URL."""
    """
    If the specific.url start with `/portal/curated/` The page type is 'Curated Topic'.
    If the specific.url start with `/portal/exhibits/` The page type is 'Exhibits'.
    If the specific.url start with `/news/` The page type is 'News'.
    If the specific.url start with `/about/` The page type is 'About the BMRC'.
    If the specific.url start with `/events/` The page type is 'Events'.
    If the specific.url start with `/research-notes/` The page type is 'Research Notes'.
    If the specific.url start with `/programs/` The page type is 'Programs'.
    If the specific.url start with `/resources/` The page type is 'Resources'.
    Default to the verbose name.
    TODO: Improve this logic.
    This is done so that a standard page under an exhibit page gets labeled as exhibit.
    Also so that Exhibit index pages get labeled as Exhibit as well.
    This is not future proof when new page types are added and breaks the data
    structure of the website which is counterproductive.
    """
    return next(
        (
            page_type
            for path, page_type in PAGE_TYPE_MAPPING.items()
            if url.startswith(path)
        ),
        '',  # Default value if no match found
    )


def search(request):
    search_query = request.GET.get('query', None)
    page = request.GET.get('page', 1)

    # Search
    if search_query:
        search_results = Page.objects.live().search(search_query)

        # search_results = Page.objects.live().search(search_query, operator="or")
        for result in search_results:
            specific_page = result.specific

            # Set page type using the mapping function
            # removed defaulting to the paget type because only '(portal) standard page' is left
            # code: `or specific_page.specific_class._meta.verbose_name`
            result.page_type = get_page_type(specific_page.url) or specific_page.specific_class._meta.verbose_name

            # Get body content and create simple excerpt
            if hasattr(specific_page, 'body'):
                # Convert StreamField to string and remove HTML-like content
                body_text = str(specific_page.body)
                body_text = re.sub(r'<[^>]+>', ' ', body_text)
                # Get first 200 chars, cut at nearest word boundary
                if len(body_text) > 200:
                    body_text = body_text[:200]
                    # Find last space to avoid cutting words
                    last_space = body_text.rfind(' ')
                    if last_space > 0:
                        body_text = body_text[:last_space]
                    result.body_excerpt = body_text + '...'
                else:
                    result.body_excerpt = body_text
            else:
                result.body_excerpt = ''

        query = Query.get(search_query)

        # Record hit
        query.add_hit()
    else:
        search_results = Page.objects.none()
    total_results = len(search_results)

    # Pagination
    paginator = Paginator(search_results, 10)
    try:
        search_results = paginator.page(page)
    except PageNotAnInteger:
        search_results = paginator.page(1)
    except EmptyPage:
        search_results = paginator.page(paginator.num_pages)

    return render(
        request,
        'search/search.html',
        {
            'search_query': search_query,
            'search_results': search_results,
            'total_results': total_results,
        },
    )
