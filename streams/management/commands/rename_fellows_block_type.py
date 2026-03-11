import json

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

# ./manage.py rename_fellows_block_type --dry-run

FROM_BLOCK = "fellows_block"
TO_BLOCK = "image_and_text_block"
# Models/fields that may contain legacy StreamField block type keys.
TARGETS = [
    ("standard", "StandardPage", "body"),
    ("news", "NewsStoryPage", "body"),
    ("portal", "CuratedTopicIndexPage", "body"),
    ("portal", "ExhibitIndexPage", "body"),
    ("portal", "ExhibitPage", "body"),
    ("portal", "PortalStandardPage", "body"),
]


def iter_raw_field_rows(model, field_name, chunk_size=200):
    """Yield raw `(id, field_value)` rows directly from the model table.

    We intentionally bypass the model field's normal deserialization path here.
    After the codebase renames a StreamField block key, Wagtail may deserialize
    rows using the *current* block definition and hide legacy keys that still
    exist in the stored JSON. Reading straight from SQL lets us inspect the
    actual persisted payload.
    """
    pk_column = connection.ops.quote_name(model._meta.pk.column)
    field_column = connection.ops.quote_name(model._meta.get_field(field_name).column)
    table_name = connection.ops.quote_name(model._meta.db_table)

    query = f"SELECT {pk_column}, {field_column} FROM {table_name}"
    with connection.cursor() as cursor:
        cursor.execute(query)
        while True:
            rows = cursor.fetchmany(chunk_size)
            if not rows:
                break
            yield from rows


def rename_block_type(value, from_type, to_type):
    """Recursively walk JSON-like data and rename StreamField block types.

    StreamField values are nested lists/dicts where each block item may look like:
    {"type": "...", "value": ...}
    """
    changed_count = 0
    changed_block_ids = []

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if item.get("type") == from_type:
                    changed_block_ids.append(item.get("id"))
                    item["type"] = to_type
                    changed_count += 1

                nested_count, nested_ids = rename_block_type(
                    item.get("value"), from_type, to_type
                )
                changed_count += nested_count
                changed_block_ids.extend(nested_ids)

    elif isinstance(value, dict):
        for nested in value.values():
            nested_count, nested_ids = rename_block_type(nested, from_type, to_type)
            changed_count += nested_count
            changed_block_ids.extend(nested_ids)

    return changed_count, changed_block_ids


class Command(BaseCommand):
    help = "One-time rename of StreamField block type fellows_block -> image_and_text_block in page body JSON."

    def add_arguments(self, parser):
        # Safety switch: show changes without writing to the database.
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without saving.",
        )
        # Optional rollback support.
        parser.add_argument(
            "--reverse",
            action="store_true",
            help="Reverse the rename (image_and_text_block -> fellows_block).",
        )

    def handle(self, *args, **options):
        # --reverse flips the rename direction.
        from_type = TO_BLOCK if options["reverse"] else FROM_BLOCK
        to_type = FROM_BLOCK if options["reverse"] else TO_BLOCK
        dry_run = options["dry_run"]

        self.stdout.write(
            self.style.WARNING(
                f"Renaming block type: {from_type} -> {to_type}{' (dry run)' if dry_run else ''}"
            )
        )

        total_rows_seen = 0
        total_rows_changed = 0
        total_blocks_changed = 0

        for app_label, model_name, field_name in TARGETS:
            # Access each target model dynamically so this command stays app-agnostic.
            model = apps.get_model(app_label, model_name)

            rows_seen = 0
            rows_changed = 0
            blocks_changed = 0

            # Iterate lazily so large tables do not load fully into memory.
            for row_id, value in iter_raw_field_rows(model, field_name):

                # Global and per-model counters for summary output.
                rows_seen += 1
                total_rows_seen += 1

                # Empty body -> nothing to inspect for block-type rename.
                if value is None:
                    continue

                # Depending on DB/backend/version, the JSON payload may be either:
                # - a raw JSON string, or
                # - an already parsed Python list/dict.
                original_is_string = isinstance(value, (str, bytes, bytearray))
                if original_is_string:
                    try:
                        if isinstance(value, (bytes, bytearray)):
                            value = value.decode()
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"- {app_label}.{model_name} id={row_id}: invalid JSON, skipped"
                            )
                        )
                        continue

                # Deep-scan nested block data and rename matching block types.
                changed_block_count, changed_block_ids = rename_block_type(
                    value, from_type, to_type
                )
                if changed_block_count:
                    rows_changed += 1
                    total_rows_changed += 1
                    blocks_changed += changed_block_count
                    total_blocks_changed += changed_block_count

                    page = model.objects.only("title").get(id=row_id)
                    block_ids_text = ", ".join(
                        str(block_id) for block_id in changed_block_ids if block_id
                    )
                    extra = f"; block_ids=[{block_ids_text}]" if block_ids_text else ""
                    self.stdout.write(
                        f"  updated {app_label}.{model_name} page='{page.title}' id={row_id}, field={field_name}, blocks_changed={changed_block_count}{extra}"
                    )

                    if not dry_run:
                        # Preserve original storage shape (string vs parsed object)
                        # so we do not introduce type surprises across environments.
                        saved_value = json.dumps(value) if original_is_string else value
                        model.objects.filter(id=row_id).update(**{field_name: saved_value})

            self.stdout.write(
                f"- {app_label}.{model_name}: pages_scanned={rows_seen}, pages_changed={rows_changed}, blocks_changed={blocks_changed}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. pages_scanned={total_rows_seen}, pages_changed={total_rows_changed}, blocks_changed={total_blocks_changed}, dry_run={dry_run}"
            )
        )
        if total_rows_changed == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No rows changed. Data may already be migrated, or this block type may not exist in these tables."
                )
            )
