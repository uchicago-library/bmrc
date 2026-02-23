from django.db import migrations


FROM_BLOCK = "fellows_block"
TO_BLOCK = "image_and_text_block"


def _rename_block_type(value, from_type, to_type):
    changed = False

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if item.get("type") == from_type:
                    item["type"] = to_type
                    changed = True
                nested_changed = _rename_block_type(item.get("value"), from_type, to_type)
                changed = changed or nested_changed
    elif isinstance(value, dict):
        for nested in value.values():
            nested_changed = _rename_block_type(nested, from_type, to_type)
            changed = changed or nested_changed

    return changed


def _migrate_page_body(model, from_type, to_type):
    for page in model.objects.all().iterator():
        body_data = page.body
        if hasattr(body_data, "raw_data"):
            body_data = body_data.raw_data

        if _rename_block_type(body_data, from_type, to_type):
            page.body = body_data
            page.save(update_fields=["body"])


def forwards(apps, schema_editor):
    CuratedTopicIndexPage = apps.get_model("portal", "CuratedTopicIndexPage")
    ExhibitIndexPage = apps.get_model("portal", "ExhibitIndexPage")
    ExhibitPage = apps.get_model("portal", "ExhibitPage")
    PortalStandardPage = apps.get_model("portal", "PortalStandardPage")

    _migrate_page_body(CuratedTopicIndexPage, FROM_BLOCK, TO_BLOCK)
    _migrate_page_body(ExhibitIndexPage, FROM_BLOCK, TO_BLOCK)
    _migrate_page_body(ExhibitPage, FROM_BLOCK, TO_BLOCK)
    _migrate_page_body(PortalStandardPage, FROM_BLOCK, TO_BLOCK)


def backwards(apps, schema_editor):
    CuratedTopicIndexPage = apps.get_model("portal", "CuratedTopicIndexPage")
    ExhibitIndexPage = apps.get_model("portal", "ExhibitIndexPage")
    ExhibitPage = apps.get_model("portal", "ExhibitPage")
    PortalStandardPage = apps.get_model("portal", "PortalStandardPage")

    _migrate_page_body(CuratedTopicIndexPage, TO_BLOCK, FROM_BLOCK)
    _migrate_page_body(ExhibitIndexPage, TO_BLOCK, FROM_BLOCK)
    _migrate_page_body(ExhibitPage, TO_BLOCK, FROM_BLOCK)
    _migrate_page_body(PortalStandardPage, TO_BLOCK, FROM_BLOCK)


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0011_alter_curatedtopicindexpage_body_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
