from portal.models import Archive
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, 
    modeladmin_register,
)
from wagtail.images.edit_handlers import ImageChooserPanel


class ArchiveAdmin(ModelAdmin):
    """Archive admin."""

    model = Archive
    menu_label = 'Archives'
    menu_icon = 'group'
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
        ImageChooserPanel('logo'),
        FieldPanel('spotlight'),
        FieldPanel('finding_aid_prefix'),
        FieldPanel('is_member'),
        FieldPanel('order'),
    )

modeladmin_register(ArchiveAdmin)
