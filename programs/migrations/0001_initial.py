# Generated by Django 5.0.10 on 2025-02-10 21:35

import django.core.validators
import django.db.models.deletion
import re
import streams.blocks
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("wagtailcore", "0094_query_searchpromotion_querydailyhits"),
        ("wagtailimages", "0026_delete_uploadedimage"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProgramsListingPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
        migrations.CreateModel(
            name="ProgramPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "body",
                    wagtail.fields.StreamField(
                        [
                            (
                                "richtext",
                                streams.blocks.RichtextBlock(group="Format and Text"),
                            ),
                            (
                                "two_column_block",
                                wagtail.blocks.StreamBlock(
                                    [
                                        (
                                            "new_column",
                                            streams.blocks.RichtextBlock(
                                                icon="arrow-right", label="New Column"
                                            ),
                                        )
                                    ],
                                    group="Format and Text",
                                ),
                            ),
                            (
                                "info_box_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "text",
                                            streams.blocks.RichtextBlock(
                                                features=[
                                                    "h2",
                                                    "h3",
                                                    "bold",
                                                    "ol",
                                                    "ul",
                                                    "hr",
                                                    "italic",
                                                    "link",
                                                    "document-link",
                                                ],
                                                label="Featured Text",
                                                required=True,
                                            ),
                                        ),
                                        (
                                            "style_type",
                                            streams.blocks.InfoBoxStyleChoiceBlock(
                                                required=True
                                            ),
                                        ),
                                    ],
                                    group="Format and Text",
                                ),
                            ),
                            (
                                "footnote_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "text",
                                            streams.blocks.RichtextBlock(
                                                features=[
                                                    "bold",
                                                    "ol",
                                                    "ul",
                                                    "italic",
                                                    "link",
                                                    "document-link",
                                                ],
                                                label="Footnote Text",
                                                required=False,
                                            ),
                                        )
                                    ],
                                    group="Format and Text",
                                ),
                            ),
                            (
                                "image_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                required=False
                                            ),
                                        ),
                                        (
                                            "caption",
                                            streams.blocks.RichtextBlock(
                                                features=["bold", "italic", "link"],
                                                label="Caption",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "alignment",
                                            streams.blocks.ImageFormatChoiceBlock(
                                                required=False
                                            ),
                                        ),
                                    ],
                                    group="Layout and Images",
                                ),
                            ),
                            (
                                "fellows_block",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "image",
                                            wagtail.images.blocks.ImageChooserBlock(
                                                label="Profile Photo", required=False
                                            ),
                                        ),
                                        (
                                            "profile_text",
                                            streams.blocks.RichtextBlock(
                                                features=[
                                                    "h2",
                                                    "h3",
                                                    "bold",
                                                    "italic",
                                                    "link",
                                                ],
                                                label="Profile Text",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "size",
                                            wagtail.blocks.ChoiceBlock(
                                                choices=[
                                                    ("LG", "Large"),
                                                    ("MD", "Medium"),
                                                    ("SM", "Small"),
                                                ]
                                            ),
                                        ),
                                        (
                                            "anchor",
                                            wagtail.blocks.CharBlock(
                                                help_text="Slug for anchor link",
                                                max_length=50,
                                                required=False,
                                                validators=[
                                                    django.core.validators.RegexValidator(
                                                        re.compile(
                                                            "^[-a-zA-Z0-9_]+\\Z"
                                                        ),
                                                        "Enter a valid “slug” consisting of letters, numbers, underscores or hyphens.",
                                                        "invalid",
                                                    )
                                                ],
                                            ),
                                        ),
                                    ],
                                    group="Layout and Images",
                                ),
                            ),
                            (
                                "clear_block",
                                streams.blocks.ClearBlock(group="Layout and Images"),
                            ),
                            (
                                "webfeed",
                                wagtail.blocks.StructBlock(
                                    [
                                        (
                                            "webfeed_title",
                                            wagtail.blocks.CharBlock(
                                                help_text="Title for callout section",
                                                required=False,
                                            ),
                                        ),
                                        (
                                            "webfeed_code",
                                            wagtail.blocks.RawHTMLBlock(required=False),
                                        ),
                                    ],
                                    group="Layout and Images",
                                ),
                            ),
                        ],
                        blank=True,
                        null=True,
                    ),
                ),
                (
                    "excerpt",
                    wagtail.fields.RichTextField(
                        blank=True,
                        help_text="Short description to display on the programs listing page. If not set, the content body is truncated.",
                    ),
                ),
                (
                    "current",
                    models.BooleanField(
                        default=True,
                        help_text="Whether or not the program is currently active.",
                    ),
                ),
                (
                    "thumbnail",
                    models.ForeignKey(
                        blank=True,
                        help_text="Image to display for the program. Alt text is defined when editing the image itself.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
