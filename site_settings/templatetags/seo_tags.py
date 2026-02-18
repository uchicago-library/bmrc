from django import template

register = template.Library()


@register.filter
def get_page_description(page):
    """
    Get the page's search_description. If not available, traverse up the page tree
    until a page with a description is found.
    
    Args:
        page: A Wagtail Page instance
        
    Returns:
        The search_description of the page or its nearest ancestor, or empty string if none found
    """
    if not page:
        return ""
    
    # Check the current page
    if hasattr(page, 'search_description') and page.search_description:
        return page.search_description
    
    # Traverse up the page tree
    current = page
    while current:
        if hasattr(current, 'search_description') and current.search_description:
            return current.search_description
        
        # Get the parent page
        try:
            current = current.get_parent()
        except (AttributeError, TypeError):
            # No parent or error getting parent
            break
    
    # No description found in the tree
    return ""
