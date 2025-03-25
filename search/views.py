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

def get_page_type(page):
    """
    Determine the page type based on the page's URL or fall back to its verbose name.

    Args:
        page: Wagtail Page object.

    Returns:
        str: The page type from PAGE_TYPE_MAPPING if the page's URL starts with a mapped path,
             otherwise the page's specific model verbose name.
    """
    url = page.url
    for path, page_type in PAGE_TYPE_MAPPING.items():
        if url.startswith(path):
            return page_type
    return page.specific_class._meta.verbose_name


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
            result.page_type = get_page_type(result)

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
