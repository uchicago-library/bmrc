# Generated by Django 5.0.10 on 2025-03-25 17:57

import django.db.models.deletion
import modelcluster.fields
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0012_alter_homepage_highlight_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="highlight_title",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="Title for the banner displayed above the footer. Supports bold text but that makes it blue.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="homepagecarouselimages",
            name="page",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="banner_options",
                to="home.homepage",
            ),
        ),
    ]
