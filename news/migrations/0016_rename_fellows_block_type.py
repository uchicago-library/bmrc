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
    NewsStoryPage = apps.get_model("news", "NewsStoryPage")
    _migrate_page_body(NewsStoryPage, FROM_BLOCK, TO_BLOCK)


def backwards(apps, schema_editor):
    NewsStoryPage = apps.get_model("news", "NewsStoryPage")
    _migrate_page_body(NewsStoryPage, TO_BLOCK, FROM_BLOCK)


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0015_alter_newsstorypage_body"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
