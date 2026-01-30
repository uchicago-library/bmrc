"""Custom sitemap for BMRC site"""

from django.contrib.sitemaps import Sitemap
from wagtail.models import Page

from news.models import NewsIndexPage, NewsStoryPage
from home.models import HomePage


class WagtailSitemap(Sitemap):
    """Custom sitemap for BMRC site with specific rules for priorities and change frequencies"""
    
    def items(self):
        """Return all pages that should be in the sitemap"""
        # Get all live, public pages
        pages = Page.objects.live().public()
        
        # Note: /admin/, /search/, /portal/search/, /portal/browse/, /turnstile/, /shib/
        # are Django views (not Wagtail pages), so they won't appear in this query
        
        # Note: Pagination URLs like /events/?page=2 won't appear in the sitemap because
        # page.url returns only the base URL without query parameters. Each NewsIndexPage
        # exists as a single Page object in the database, and pagination is handled in
        # the view/template layer.
        
        # Filter out pages without a proper URL (like the root page)
        return [page for page in pages if page.url]
    
    def location(self, page):
        """Return the URL for the page"""
        return page.url
    
    def lastmod(self, page):
        """Return the last modification date"""
        return page.last_published_at
    
    def changefreq(self, page):
        """Return change frequency based on page type"""
        page_specific = page.specific
        
        # NewsIndexPage changes weekly as new stories are added
        if isinstance(page_specific, NewsIndexPage):
            return 'weekly'
        
        # News stories change less frequently once published
        if isinstance(page_specific, NewsStoryPage):
            return 'monthly'
        
        # Home page changes more frequently
        if isinstance(page_specific, HomePage):
            return 'weekly'
        
        # Default for other pages
        return 'monthly'
    
    def priority(self, page):
        """Return priority based on page type and location"""
        # Use page.url (actual URL) instead of page.url_path (internal Wagtail path)
        url = page.url.lower().rstrip('/') if page.url else ''
        
        # Highest priority pages (1.0)
        high_priority_paths = ['', '/about', '/donate', '/programs', '/portal', '/portal/about']
        if url in high_priority_paths:
            return 1.0
        
        # Second highest priority (0.8) - pages under these sections
        second_priority_sections = ['/programs/', '/news/', '/events/']
        for section in second_priority_sections:
            # Check if URL is under this section but not the section itself
            if url.startswith(section.rstrip('/')):
                return 0.8
        
        # NewsStoryPage gets higher priority
        if isinstance(page.specific, NewsStoryPage):
            return 0.8
        
        # Default priority for other pages
        return 0.5
