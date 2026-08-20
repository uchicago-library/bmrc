"""Seed MainNavigation with the menus that were previously hardcoded in
``bmrc/templates/includes/nav.html``.

Links are seeded as plain URL strings (not page references) so this runs
identically in every environment without needing a copy of the production
database. Editors can swap any URL for a page chooser afterwards in the admin.
"""

from django.db import migrations

# (title, url, [(item title, item url), ...]) for each top-level dropdown.
# An empty dropdown url renders as "#" (matches the old "Information" toggle).
MENUS = [
    (
        "About",
        "/about/",
        [
            ("About the BMRC", "/about/"),
            (
                "Oral History Project",
                "/about/the-founding-of-the-bmrc-oral-history-project/",
            ),
            ("Membership Information", "/about/membership-information/"),
            ("Current Members", "/about/membership"),
            ("Partnerships", "/about/partnerships/"),
            ("Board & Committees", "/about/board-committees/"),
            ("Staff", "/about/staff/"),
            ("Contact", "/contact/"),
        ],
    ),
    (
        "Information",
        "",
        [
            ("News", "/news/"),
            ("Events", "/events/"),
            ("Research Notes", "/research-notes/"),
        ],
    ),
    (
        "Programs",
        "/programs/",
        [
            ("Summer Short-term Fellowship", "/programs/summer-short-term-fellowship/"),
            (
                "Archie Motley Archival Internship Program",
                "/programs/archie-motley-archival-internship-program/",
            ),
            (
                "Color Curtain Processing Project",
                "/programs/color-curtain-processing-project/",
            ),
            ("Survey Initiative", "/programs/survey-initiative/"),
            (
                "Faculty Organizing for Community Archives Support (FOCAS) Project",
                "/programs/faculty-organizing-for-community-archives-support-focas-project/",
            ),
            (
                "Black Visual Arts Research(er)",
                "/programs/black-visual-arts-researcher/",
            ),
        ],
    ),
    (
        "Resources",
        "/resources/",
        [
            ("Archives Awareness", "/resources/archives-awareness/"),
            (
                "Legacy Management Resource Portal",
                "/resources/legacy-management-resources-portal/",
            ),
            ("Protest in the Archives", "/resources/protest-archives/"),
            ("Workshops", "/resources/workshops"),
            ("Jobs and Opportunities", "/resources/jobs"),
        ],
    ),
]


def build_menus():
    """Return the StreamField value as a list of (block_type, value) tuples."""
    menus = []
    for title, url, items in MENUS:
        menus.append(
            (
                "dropdown",
                {
                    "title": title,
                    "url": url,
                    "items": [
                        {"title": item_title, "url": item_url}
                        for item_title, item_url in items
                    ],
                },
            )
        )
    return menus


def seed_navigation(apps, schema_editor):
    MainNavigation = apps.get_model("site_settings", "MainNavigation")
    Site = apps.get_model("wagtailcore", "Site")

    for site in Site.objects.all():
        nav, _ = MainNavigation.objects.get_or_create(site=site)
        # Don't clobber menus that have already been configured.
        if nav.menus:
            continue
        nav.menus = build_menus()
        nav.save()


class Migration(migrations.Migration):

    dependencies = [
        ("site_settings", "0004_mainnavigation"),
        ("wagtailcore", "0094_alter_page_locale"),
    ]

    operations = [
        migrations.RunPython(seed_navigation, migrations.RunPython.noop),
    ]
