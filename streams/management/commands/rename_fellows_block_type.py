import json

from django.apps import apps
from django.core.management.base import BaseCommand


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


def rename_block_type(value, from_type, to_type):
    """Recursively walk JSON-like data and rename StreamField block types.

    StreamField values are nested lists/dicts where each block item may look like:
    {"type": "...", "value": ...}
    """
    changed = False

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                if item.get("type") == from_type:
                    item["type"] = to_type
                    changed = True

                nested_changed = rename_block_type(item.get("value"), from_type, to_type)
                changed = changed or nested_changed

    elif isinstance(value, dict):
        for nested in value.values():
            nested_changed = rename_block_type(nested, from_type, to_type)
            changed = changed or nested_changed

    return changed


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
        # Extra diagnostics to help when troubleshooting.
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print per-model and per-row debug information.",
        )

    def handle(self, *args, **options):
        # --reverse flips the rename direction.
        from_type = TO_BLOCK if options["reverse"] else FROM_BLOCK
        to_type = FROM_BLOCK if options["reverse"] else TO_BLOCK
        dry_run = options["dry_run"]
        debug = options["debug"]

        self.stdout.write(
            self.style.WARNING(
                f"Renaming block type: {from_type} -> {to_type}{' (dry run)' if dry_run else ''}"
            )
        )
        if debug:
            self.stdout.write(self.style.WARNING("Debug mode enabled"))

        total_rows_seen = 0
        total_rows_changed = 0

        for app_label, model_name, field_name in TARGETS:
            # Access each target model dynamically so this command stays app-agnostic.
            model = apps.get_model(app_label, model_name)
            queryset = model.objects.values("id", field_name)

            if debug:
                self.stdout.write(
                    f"[debug] Scanning {app_label}.{model_name}.{field_name}"
                )

            rows_seen = 0
            rows_changed = 0

            for row in queryset.iterator():
                if debug:
                    self.stdout.write(
                        f"[debug] looking at row."
                    )

                rows_seen += 1
                total_rows_seen += 1

                row_id = row["id"]
                value = row[field_name]

                if value is None:
                    continue

                original_is_string = isinstance(value, str)
                if original_is_string:
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        self.stdout.write(
                            self.style.WARNING(
                                f"- {app_label}.{model_name} id={row_id}: invalid JSON, skipped"
                            )
                        )
                        continue
                elif debug:
                    self.stdout.write(
                        f"[debug] {app_label}.{model_name} id={row_id}: value is already parsed JSON"
                    )

                if rename_block_type(value, from_type, to_type):
                    rows_changed += 1
                    total_rows_changed += 1

                    if debug:
                        self.stdout.write(
                            f"[debug] {app_label}.{model_name} id={row_id}: renamed block type"
                        )

                    if not dry_run:
                        saved_value = json.dumps(value) if original_is_string else value
                        model.objects.filter(id=row_id).update(**{field_name: saved_value})
                    elif debug:
                        self.stdout.write(
                            f"[debug] {app_label}.{model_name} id={row_id}: dry-run, no DB update"
                        )

            self.stdout.write(
                f"- {app_label}.{model_name}: scanned={rows_seen}, changed={rows_changed}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. scanned={total_rows_seen}, changed={total_rows_changed}, dry_run={dry_run}"
            )
        )
        if total_rows_changed == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No rows changed. Data may already be migrated, or this block type may not exist in these tables."
                )
            )
