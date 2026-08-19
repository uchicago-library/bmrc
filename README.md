# BMRC "Wagtailified" Project
This branch is testing the EAD ingestion and conversion to a Wagtail native BMRC portal page.
Not every EAD tag is currently accounted for, so some tags in the conversion may get silently ignored,
but the structure of the mapping in new_import_aids should allow for easy updates.

## To convert your own EAD to a Wagtailified Page
1. Locally download EAD XML files and create a temporary directory in your environment
2. Upload the EADs to the temporary directory
3. Run ``` docker compose exec web ./manage.py new_import_aids "<temp import directory>/BMRC.EXAMPLE.EGGS.xml" --publish ```
4. Run the dev site locally `docker compose exec web python manage.py runserver 0.0.0.0:3000`
5. Go into wagtail admin to find the imported page under the portal page (I'm unsure how effective the search is)


# Changelog

## Core pieces

### 1. `WagtailifiedPage` (`portal/models.py`)

A Wagtail `Page` subclass that represents a single finding aid. Fields map to the EAD 2002 "Descriptive Summary" and note sections

### 2. `FindingAidComponent` (`portal/models.py`)

A self-referential model representing a single node (`<c>`/`<c01>`–`<c12>`) from an EAD `<dsc>` (Description of Subordinate Components) tree

### 3. `new_import_aids` management command (`portal/management/commands/new_import_aids.py`)

Parses a single EAD XML file with `xml.etree.ElementTree` and creates a `WagtailifiedPage` (plus its full `FindingAidComponent` tree) from it.

Note that the shared link logic is a Python port of the logic from the original `views.py`, so `indexed_terms` links generated for `WagtailifiedPage` should behave identically to the ones on the XSLT-rendered pages

