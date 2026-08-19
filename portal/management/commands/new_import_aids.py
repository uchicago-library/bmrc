import html
import urllib.parse
import xml.etree.ElementTree as ET

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Page

from portal.models import Archive, FindingAidComponent, WagtailifiedPage


LANGUAGE_MAP = {
    "eng": "English",
    "fre": "French",
    "ger": "German",
    "spa": "Spanish",
}


CONTROLACCESS_FACET_MAP = {
    "persname": "people",
    "famname": "people",
    "name": "people",
    "corpname": "organizations",
    "geogname": "places",
    "subject": "topics",
    "occupation": "topics",
    "genreform": "topics",
    "function": "topics",
    "title": "topics",
}

BLOCK_CHILD_TAGS = {
    "p",
    "list",
    "chronlist",
    "table",
    "head",
    "head01",
    "head02",
    "note",
}

PORTAL_BASE_URI = "https://bmrc.lib.uchicago.edu/"


def bmrc_search_url(namespace_uri, term):
    uri = "{}{}".format(
        namespace_uri,
        urllib.parse.quote_plus(term.strip()),
    )
    return "/portal/search/?f={}".format(
        urllib.parse.quote_plus(uri)
    )


def strip_ns(tag):
    """strips namespace from a tag"""
    return tag.split("}")[-1] if "}" in tag else tag


def text_of(elem):
    """returns all text contained in an XML element"""
    if elem is None:
        return ""

    return "".join(elem.itertext()).strip()


def ead_element_to_html(elem):
    """
    generic ead-to-html conversion, allows for the mapping to be
    more generalized and easier to update.
    """

    if elem is None:
        return ""

    tag = strip_ns(elem.tag)

    if tag == "p":
        return f"<p>{html.escape(text_of(elem))}</p>"

    if tag in {"head", "head01", "head02"}:
        return f"<h3>{html.escape(text_of(elem))}</h3>"

    if tag == "list":
        items = []

        for child in elem:
            if strip_ns(child.tag) == "item":
                items.append(
                    f"<li>{html.escape(text_of(child))}</li>"
                )

        if items:
            return "<ul>" + "".join(items) + "</ul>"

    if tag in CONTROLACCESS_FACET_MAP:
        term = text_of(elem)

        if not term:
            return ""

        facet = CONTROLACCESS_FACET_MAP[tag]
        namespace_uri = f"{PORTAL_BASE_URI}{facet}/"
        url = bmrc_search_url(namespace_uri, term)

        return (
            f'<a href="{html.escape(url, quote=True)}">'
            f"{html.escape(term)}"
            f"</a>"
        )
    block_children = [
        child for child in elem if strip_ns(child.tag) in BLOCK_CHILD_TAGS
    ]

    if block_children:
        return "".join(
            ead_element_to_html(child) for child in block_children
        )

    content = text_of(elem)

    if not content:
        return ""

    return f'<div class="ead-{tag}">{html.escape(content)}</div>'


def elements_to_html(elems):
    """
    converts one or more elements to html
    """

    if elems is None:
        return ""

    if not isinstance(elems, list):
        elems = [elems]

    return "".join(
        ead_element_to_html(elem)
        for elem in elems
        if elem is not None
    )


def controlaccess_to_html(elems):
    """
    builds the link list... should work the same as the xslt transform
    """

    if elems is None:
        return ""

    if not isinstance(elems, list):
        elems = [elems]

    items_html = []

    for elem in elems:
        if elem is None:
            continue

        for child in elem.iter():
            tag = strip_ns(child.tag)

            if tag not in CONTROLACCESS_FACET_MAP:
                continue

            term = text_of(child)

            if not term:
                continue

            facet = CONTROLACCESS_FACET_MAP[tag]
            namespace_uri = f"{PORTAL_BASE_URI}{facet}/"
            url = bmrc_search_url(namespace_uri, term)

            items_html.append(
                f'<li>'
                f'<a href="{html.escape(url, quote=True)}">'
                f'{html.escape(term)}'
                f'</a>'
                f'</li>'
            )

    if not items_html:
        return ""

    return "<ul>" + "".join(items_html) + "</ul>"


COMPONENT_TAGS = {"c"} | {
    f"c{n:02d}"
    for n in range(1, 13)
}


def get_child_components(elem):
    """gets direct child <c>/<c01>-<c12> elements, in document order."""
    return [
        child
        for child in elem
        if strip_ns(child.tag) in COMPONENT_TAGS
    ]


def import_component(
    c_elem,
    page,
    parent=None,
    sort_order=0,
):
    did = c_elem.find("{*}did")

    level = c_elem.get("level", "")

    unitid = (
        text_of(did.find("{*}unitid"))
        if did is not None
        else ""
    )

    unittitle = (
        text_of(did.find("{*}unittitle"))
        if did is not None
        else ""
    )

    unitdate = (
        text_of(did.find("{*}unitdate"))
        if did is not None
        else ""
    )

    extent = (
        text_of(
            did.find(".//{*}physdesc/{*}extent")
        )
        if did is not None
        else ""
    )

    scope_and_contents = elements_to_html(
        c_elem.findall("{*}scopecontent")
    )

    container_type = ""
    container_number = ""

    if did is not None:
        containers = did.findall("{*}container")

        container_type = ", ".join(
            c.get("type", "") for c in containers if c.get("type", "")
        )
        container_number = ", ".join(
            text_of(c) for c in containers if text_of(c)
        )

    component = FindingAidComponent.objects.create(
        page=page,
        parent=parent,
        sort_order=sort_order,
        level=level,
        unitid=unitid,
        unittitle=unittitle,
        unitdate=unitdate,
        extent=extent,
        scope_and_contents=scope_and_contents,
        container_type=container_type,
        container_number=container_number,
    )

    for i, child in enumerate(
        get_child_components(c_elem)
    ):
        import_component(
            child,
            page,
            parent=component,
            sort_order=i,
        )


def import_dsc(archdesc, page):
    dsc = archdesc.find("{*}dsc")

    if dsc is None:
        return

    for i, c_elem in enumerate(
        get_child_components(dsc)
    ):
        import_component(
            c_elem,
            page,
            parent=None,
            sort_order=i,
        )


class Command(BaseCommand):
    help = "import ead and create wagtailified page"

    def add_arguments(self, parser):
        parser.add_argument(
            "xml_path",
            type=str,
            help="Path to the EAD XML file.",
        )

        parser.add_argument(
            "--publish",
            action="store_true",
            help=(
                "Publish the page "
                "(default: save as draft only)."
            ),
        )

    def handle(self, *args, **options):
        xml_path = options["xml_path"]
        publish = options["publish"]

        PARENT_PAGE_ID = 11

        try:
            tree = ET.parse(xml_path)

        except (
            ET.ParseError,
            FileNotFoundError,
            OSError,
        ) as e:
            raise CommandError(
                f"Could not parse '{xml_path}': {e}"
            )

        root = tree.getroot()

        archdesc = root.find(".//{*}archdesc")

        if archdesc is None:
            raise CommandError(
                "No <archdesc> element found — "
                "is this a valid EAD file?"
            )

        did = archdesc.find("{*}did")

        if did is None:
            raise CommandError(
                "No <did> element found under <archdesc>."
            )

        title = text_of(
            did.find("{*}unittitle")
        )

        identifier = text_of(
            did.find("{*}unitid")
        )

        repository_name = text_of(
            did.find(
                ".//{*}repository/{*}corpname"
            )
        )

        lang_elem = did.find(
            ".//{*}langmaterial/{*}language"
        )

        langcode = (
            lang_elem.get("langcode")
            if lang_elem is not None
            else None
        )

        language = LANGUAGE_MAP.get(
            langcode,
            text_of(lang_elem),
        )

        size = text_of(
            did.find(
                ".//{*}physdesc/{*}extent"
            )
        )

        inclusive_dates = ""
        bulk_dates = ""
        fallback_date = ""

        for unitdate in did.findall(
            "{*}unitdate"
        ):
            udtype = unitdate.get("type")

            if udtype == "inclusive":
                inclusive_dates = text_of(unitdate)

            elif udtype == "bulk":
                bulk_dates = text_of(unitdate)

            elif not udtype:
                fallback_date = text_of(unitdate)

        date_range = (
            inclusive_dates
            or fallback_date
        )

        FIELD_MAP = {
            "historical_note": [
                "bioghist",
            ],

            "scope_and_contents": [
                "scopecontent",
            ],

            "processing_information": [
                "processinfo",
            ],

            "conditions_governing_access": [
                "accessrestrict",
            ],

            "conditions_governing_use": [
                "userestrict",
            ],

            "related_archival_materials": [
                "relatedmaterial",
            ],
        }

        mapped_fields = {}

        for field_name, ead_tags in FIELD_MAP.items():

            elements = []

            for tag in ead_tags:
                elements.extend(
                    archdesc.findall(
                        f"{{*}}{tag}"
                    )
                )

            mapped_fields[field_name] = (
                elements_to_html(elements)
            )

        indexed_terms = controlaccess_to_html(
            archdesc.findall("{*}controlaccess")
        )

        archive = None

        if identifier and "." in identifier:
            prefix = identifier.rsplit(
                ".",
                1,
            )[0]

            archive = Archive.objects.filter(
                finding_aid_prefix=prefix
            ).first()

        try:
            parent_page = Page.objects.get(
                id=PARENT_PAGE_ID
            ).specific

        except Page.DoesNotExist:
            raise CommandError(
                "No page found"
            )

        if (
            identifier
            and WagtailifiedPage.objects.filter(
                identifier=identifier
            ).exists()
        ):
            raise CommandError(
                f"A page with identifier "
                f"'{identifier}' already exists — "
                "aborting to avoid a duplicate."
            )

        new_page = WagtailifiedPage(
            title=(
                title
                or identifier
                or "Untitled Finding Aid"
            ),

            identifier=identifier,
            repository=repository_name,
            language=language,
            size=size,

            predominant_dates=bulk_dates,
            date_range=date_range,

            historical_note=mapped_fields[
                "historical_note"
            ],

            scope_and_contents=mapped_fields[
                "scope_and_contents"
            ],

            processing_information=mapped_fields[
                "processing_information"
            ],

            conditions_governing_access=mapped_fields[
                "conditions_governing_access"
            ],

            conditions_governing_use=mapped_fields[
                "conditions_governing_use"
            ],

            related_archival_materials=mapped_fields[
                "related_archival_materials"
            ],

            indexed_terms=indexed_terms,

            archive=archive,
        )

        parent_page.add_child(
            instance=new_page
        )

        import_dsc(
            archdesc,
            new_page
        )

        if publish:
            new_page.save_revision().publish()
            status = "published"

        else:
            new_page.save_revision()
            status = "saved as draft"

        self.stdout.write(
            self.style.SUCCESS(
                f"Created page '{new_page.title}' "
                f"(id={new_page.id}) — {status}."
            )
        )