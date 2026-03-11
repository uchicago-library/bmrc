import json
from collections.abc import Mapping

from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection

# ./manage.py rename_fellows_block_type --dry-run --debug --focus-id 10

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


def safe_repr(value, max_len=1200):
    """Best-effort repr for debug logs that never crashes the command."""
    try:
        text = repr(value)
    except Exception as exc:
        text = f"<repr failed: {exc.__class__.__name__}: {exc}>"

    if len(text) > max_len:
        return text[:max_len] + "...<truncated>"
    return text


def normalize_json_like(value):
    """Convert StreamField-adjacent containers (e.g. RawDataView) to list/dict.

    This keeps strings/bytes untouched while recursively normalizing mappings and
    generic iterables into plain Python containers so recursive walkers can work.
    """
    if isinstance(value, (str, bytes, bytearray)):
        return value

    if isinstance(value, Mapping):
        return {key: normalize_json_like(nested) for key, nested in value.items()}

    if isinstance(value, list):
        return [normalize_json_like(item) for item in value]

    if isinstance(value, tuple):
        return [normalize_json_like(item) for item in value]

    if hasattr(value, "__iter__"):
        try:
            return [normalize_json_like(item) for item in value]
        except TypeError:
            return value

    return value


def collect_block_types(value, found=None):
    """Collect all nested `type` values from StreamField-like JSON."""
    if found is None:
        found = set()

    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                block_type = item.get("type")
                if block_type:
                    found.add(block_type)
                collect_block_types(item.get("value"), found)
    elif isinstance(value, dict):
        for nested in value.values():
            collect_block_types(nested, found)

    return found


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
        parser.add_argument(
            "--focus-id",
            type=int,
            default=None,
            help="When set with --debug, print row-level debug only for this row id.",
        )
        parser.add_argument(
            "--debug-max-len",
            type=int,
            default=1200,
            help="Maximum characters printed for repr() values in debug output.",
        )

    def handle(self, *args, **options):
        # --reverse flips the rename direction.
        from_type = TO_BLOCK if options["reverse"] else FROM_BLOCK
        to_type = FROM_BLOCK if options["reverse"] else TO_BLOCK
        dry_run = options["dry_run"]
        debug = options["debug"]
        focus_id = options["focus_id"]
        debug_max_len = options["debug_max_len"]

        self.stdout.write(
            self.style.WARNING(
                f"Renaming block type: {from_type} -> {to_type}{' (dry run)' if dry_run else ''}"
            )
        )
        if debug:
            self.stdout.write(
                self.style.WARNING(
                    f"Debug mode enabled (focus_id={focus_id}, debug_max_len={debug_max_len})"
                )
            )

        total_rows_seen = 0
        total_rows_changed = 0

        for app_label, model_name, field_name in TARGETS:
            # Access each target model dynamically so this command stays app-agnostic.
            model = apps.get_model(app_label, model_name)

            if debug:
                self.stdout.write(
                    f"[debug] ### Scanning {app_label}.{model_name}.{field_name} via raw SQL table read"
                )

            rows_seen = 0
            rows_changed = 0

            # Iterate lazily so large tables do not load fully into memory.
            for row_id, value in iter_raw_field_rows(model, field_name):

                # Global and per-model counters for summary output.
                rows_seen += 1
                total_rows_seen += 1

                is_focus_row = focus_id is not None and row_id == focus_id
                log_row_debug = debug and (focus_id is None or is_focus_row)

                if log_row_debug:
                    value_type = type(value).__name__
                    if isinstance(value, str):
                        value_summary = f"str(len={len(value)})"
                    elif isinstance(value, list):
                        value_summary = f"list(len={len(value)})"
                    elif isinstance(value, dict):
                        value_summary = f"dict(keys={list(value.keys())[:5]})"
                    else:
                        value_summary = value_type
                    self.stdout.write(
                        f"[debug] looking at row id={row_id}, field={field_name}, value={value_summary}, value_type={value_type}."
                    )

                if is_focus_row and debug:
                    self.stdout.write(
                        self.style.WARNING(
                            f"[debug][focus] id={row_id}: exhaustive inspect start"
                        )
                    )
                    self.stdout.write(
                        f"[debug][focus] value repr: {safe_repr(value, debug_max_len)}"
                    )
                    if hasattr(value, "value"):
                        self.stdout.write(
                            f"[debug][focus] value.value type={type(value.value).__name__}"
                        )
                        self.stdout.write(
                            f"[debug][focus] value.value repr: {safe_repr(value.value, debug_max_len)}"
                        )
                    else:
                        self.stdout.write("[debug][focus] value.value: <attribute missing>")

                    if hasattr(value, "raw_data"):
                        self.stdout.write(
                            f"[debug][focus] value.raw_data type={type(value.raw_data).__name__}"
                        )
                        self.stdout.write(
                            f"[debug][focus] value.raw_data repr: {safe_repr(value.raw_data, debug_max_len)}"
                        )
                    else:
                        self.stdout.write("[debug][focus] value.raw_data: <attribute missing>")

                # Empty body -> nothing to inspect for block-type rename.
                if value is None:
                    continue

                # Normalize DB-adapter values (which may arrive as strings, Python
                # containers, or JSON-adjacent wrappers) before traversing them.
                value = normalize_json_like(value)
                if is_focus_row and debug:
                    self.stdout.write(
                        f"[debug][focus] normalized_json_like_type={type(value).__name__}"
                    )

                # Depending on DB/backend/version, the JSON payload may be either:
                # - a raw JSON string, or
                # - an already parsed Python list/dict.
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
                elif log_row_debug:
                    self.stdout.write(
                        f"[debug] {app_label}.{model_name} id={row_id}: value is already parsed JSON"
                    )

                if is_focus_row and debug:
                    normalized_type = type(value).__name__
                    self.stdout.write(
                        f"[debug][focus] normalized_type={normalized_type}, normalized_repr={safe_repr(value, debug_max_len)}"
                    )
                    discovered_types = sorted(collect_block_types(value))
                    self.stdout.write(
                        f"[debug][focus] discovered_types_count={len(discovered_types)}, has_{from_type}={from_type in discovered_types}"
                    )
                    self.stdout.write(
                        f"[debug][focus] discovered_types={discovered_types}"
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"[debug][focus] id={row_id}: exhaustive inspect end"
                        )
                    )


                # Deep-scan nested block data and rename matching block types.
                if rename_block_type(value, from_type, to_type):
                    rows_changed += 1
                    total_rows_changed += 1

                    if log_row_debug:
                        self.stdout.write(
                            f"[debug] {app_label}.{model_name} id={row_id}: renamed block type"
                        )

                    if not dry_run:
                        # Preserve original storage shape (string vs parsed object)
                        # so we do not introduce type surprises across environments.
                        saved_value = json.dumps(value) if original_is_string else value
                        model.objects.filter(id=row_id).update(**{field_name: saved_value})
                    elif log_row_debug:
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
