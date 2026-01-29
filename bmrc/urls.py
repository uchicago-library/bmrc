from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from portal import views as portal_views
from search import views as search_views
from .sitemap import WagtailSitemap

# Define sitemaps
sitemaps = {
    'pages': WagtailSitemap,
}

urlpatterns = [
    re_path(r'^django-admin/', admin.site.urls),

    re_path(r'^admin/', include(wagtailadmin_urls)),
    re_path(r'^documents/', include(wagtaildocs_urls)),

    re_path(r'^portal/browse/', portal_views.browse, name='portal_browse'),
    re_path(r'^portal/facet_view_all/', portal_views.facet_view_all, name='portal_facet_view_all'),
    re_path(r'^portal/search/', portal_views.search, name='portal_search'),
    re_path(r'^portal/view/', portal_views.view, name='portal_view'),

    re_path(r'^search/$', search_views.search, name='search'),

    re_path(r'^shib/', include('shibboleth.urls', namespace='shibboleth')),

    # Cloudflare Turnstile URLs
    re_path(r'^turnstile/', include('django_turnstile_site_protect.urls')),
    
    # Sitemap
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    re_path(r'', include(wagtail_urls)),

    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    re_path(r'^pages/', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
