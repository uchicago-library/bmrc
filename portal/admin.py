from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from portal.models import Archive


class AcrchiveAdminViewSet(SnippetViewSet):
    """Archive admin."""

    model = Archive
    menu_label = 'Archives'
    icon = 'group'
    menu_order = 290
    add_to_settings_menu = False
    exclude_from_explorer = False
    list_display = (
        'name',
        'address',
        'link',
        'logo',
        'spotlight',
        'finding_aid_prefix',
        'is_member',
        'order',
    )
    search_fields = (
        'name',
        'address',
        'link',
        'spotlight',
        'finding_aid_prefix',
    )

    panels = (
        FieldPanel('name'),
        FieldPanel('address'),
        FieldPanel('link'),
        FieldPanel('logo'),
        FieldPanel('spotlight'),
        FieldPanel('finding_aid_prefix'),
        FieldPanel('is_member'),
        FieldPanel('order'),
    )


register_snippet(AcrchiveAdminViewSet)
