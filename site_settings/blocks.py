"""Blocks for site-wide settings (currently the main navigation menu)."""

from wagtail import blocks


class NavLinkBlock(blocks.StructBlock):
    """A single link inside a navigation dropdown menu."""

    title = blocks.CharBlock(required=True, help_text="Text shown for the link.")
    page = blocks.PageChooserBlock(
        required=False,
        help_text="Link to an internal page. Takes precedence over URL.",
    )
    url = blocks.CharBlock(
        required=False,
        label="URL",
        help_text="Manual or external URL. Used only when no page is set. "
        "Accepts absolute paths (e.g. /about/) and full URLs.",
    )

    class Meta:
        icon = "link"
        label = "Link"


class NavDropdownBlock(blocks.StructBlock):
    """A top-level navigation dropdown menu and its links."""

    title = blocks.CharBlock(
        required=True, help_text="Text shown for the dropdown toggle."
    )
    page = blocks.PageChooserBlock(
        required=False,
        help_text="Optional link for the dropdown toggle itself. "
        "Takes precedence over URL.",
    )
    url = blocks.CharBlock(
        required=False,
        label="URL",
        help_text="Optional manual URL for the dropdown toggle. "
        "Used only when no page is set.",
    )
    items = blocks.ListBlock(NavLinkBlock(), label="Links")

    class Meta:
        icon = "list-ul"
        label = "Dropdown menu"
