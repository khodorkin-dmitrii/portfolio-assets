#!/usr/bin/env python3
"""Validate project asset manifests without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_ROOT = REPOSITORY_ROOT / "projects"
SUPPORTED_SCHEMA_VERSION = 1
TYPE_DIRECTORIES = {
    "film": "films",
    "person": "people",
    "planet": "planets",
    "species": "species",
    "starship": "starships",
    "vehicle": "vehicles",
}
ALLOWED_EXTENSIONS = {".webp", ".png", ".jpg", ".jpeg"}
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSIONED_FILE = re.compile(
    r"^(?P<artwork>[a-z0-9]+(?:-[a-z0-9]+)*)-"
    r"(?P<variant>card|full)-v(?P<version>[1-9][0-9]*)"
    r"(?P<extension>\.(?:webp|png|jpe?g))$"
)


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


class ManifestValidator:
    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = manifest_path
        self.project_root = manifest_path.parent
        self.project_id = self.project_root.name
        self.label = manifest_path.relative_to(REPOSITORY_ROOT).as_posix()
        self.errors: list[str] = []

    def error(self, location: str, message: str) -> None:
        suffix = f" ({location})" if location else ""
        self.errors.append(f"{self.label}{suffix}: {message}")

    def validate(self) -> list[str]:
        try:
            with self.manifest_path.open(encoding="utf-8") as manifest_file:
                data = json.load(manifest_file)
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            self.error("", f"cannot read valid UTF-8 JSON: {exc}")
            return self.errors

        if not isinstance(data, dict):
            self.error("", "top-level JSON value must be an object")
            return self.errors

        for field in ("schemaVersion", "contentVersion", "projectId", "entities"):
            if field not in data:
                self.error(field, "required field is missing")

        schema_version = data.get("schemaVersion")
        if schema_version != SUPPORTED_SCHEMA_VERSION or not is_integer(schema_version):
            self.error("schemaVersion", f"must be the integer {SUPPORTED_SCHEMA_VERSION}")

        content_version = data.get("contentVersion")
        if not is_integer(content_version) or content_version <= 0:
            self.error("contentVersion", "must be a positive integer")

        manifest_project_id = data.get("projectId")
        if manifest_project_id != self.project_id:
            self.error("projectId", f"must match directory name {self.project_id!r}")

        entities = data.get("entities")
        if not isinstance(entities, list):
            self.error("entities", "must be an array")
            return self.errors

        seen_entities: set[tuple[str, int]] = set()
        sortable_entities: list[tuple[str, int]] = []
        for entity_index, entity in enumerate(entities):
            location = f"entities[{entity_index}]"
            sortable_key = self.validate_entity(entity, location, seen_entities)
            if sortable_key is not None:
                sortable_entities.append(sortable_key)

        if len(sortable_entities) == len(entities) and sortable_entities != sorted(sortable_entities):
            self.error("entities", "must be ordered by type and numeric id")

        return self.errors

    def validate_entity(
        self,
        entity: Any,
        location: str,
        seen_entities: set[tuple[str, int]],
    ) -> tuple[str, int] | None:
        if not isinstance(entity, dict):
            self.error(location, "must be an object")
            return None

        for field in ("type", "id", "images"):
            if field not in entity:
                self.error(f"{location}.{field}", "required field is missing")

        entity_type = entity.get("type")
        entity_id = entity.get("id")
        entity_type_valid = isinstance(entity_type, str) and entity_type in TYPE_DIRECTORIES
        entity_id_valid = is_integer(entity_id) and entity_id > 0

        if not entity_type_valid:
            allowed = ", ".join(TYPE_DIRECTORIES)
            self.error(f"{location}.type", f"must be one of: {allowed}")
        if not entity_id_valid:
            self.error(f"{location}.id", "must be a positive integer SWAPI resource id")

        if entity_type_valid and entity_id_valid:
            entity_key = (entity_type, entity_id)
            if entity_key in seen_entities:
                self.error(location, f"duplicate entity key {entity_key!r}")
            seen_entities.add(entity_key)
        else:
            entity_key = None

        images = entity.get("images")
        if not isinstance(images, list):
            self.error(f"{location}.images", "must be an array")
        else:
            self.validate_images(images, location, entity_type, entity_id)

        return entity_key

    def validate_images(
        self,
        images: list[Any],
        entity_location: str,
        entity_type: Any,
        entity_id: Any,
    ) -> None:
        seen_artwork_ids: set[str] = set()
        seen_orders: set[int] = set()
        valid_orders: list[int] = []

        for image_index, artwork in enumerate(images):
            location = f"{entity_location}.images[{image_index}]"
            if not isinstance(artwork, dict):
                self.error(location, "must be an object")
                continue

            for field in ("id", "displayOrder", "variants"):
                if field not in artwork:
                    self.error(f"{location}.{field}", "required field is missing")

            artwork_id = artwork.get("id")
            artwork_id_valid = isinstance(artwork_id, str) and bool(KEBAB_CASE.fullmatch(artwork_id))
            if not artwork_id_valid:
                self.error(f"{location}.id", "must be a lowercase kebab-case string")
            elif artwork_id in seen_artwork_ids:
                self.error(f"{location}.id", f"duplicate artwork id {artwork_id!r}")
            else:
                seen_artwork_ids.add(artwork_id)

            label = artwork.get("label")
            if "label" in artwork and (not isinstance(label, str) or not label.strip()):
                self.error(f"{location}.label", "must be a non-empty string when present")

            display_order = artwork.get("displayOrder")
            if not is_integer(display_order) or display_order < 0:
                self.error(f"{location}.displayOrder", "must be a non-negative integer")
            elif display_order in seen_orders:
                self.error(f"{location}.displayOrder", f"duplicate display order {display_order}")
            else:
                seen_orders.add(display_order)
                valid_orders.append(display_order)

            variants = artwork.get("variants")
            if not isinstance(variants, dict):
                self.error(f"{location}.variants", "must be an object")
                continue

            for variant_name in ("card", "full"):
                variant_location = f"{location}.variants.{variant_name}"
                if variant_name not in variants:
                    self.error(variant_location, "required variant is missing")
                    continue
                self.validate_variant(
                    variants[variant_name],
                    variant_location,
                    variant_name,
                    artwork_id if artwork_id_valid else None,
                    entity_type,
                    entity_id,
                )

            unexpected_variants = sorted(set(variants) - {"card", "full"})
            for variant_name in unexpected_variants:
                self.error(f"{location}.variants.{variant_name}", "unsupported variant")

        if len(valid_orders) == len(images) and valid_orders != sorted(valid_orders):
            self.error(f"{entity_location}.images", "must be ordered by displayOrder")

    def validate_variant(
        self,
        variant: Any,
        location: str,
        variant_name: str,
        artwork_id: str | None,
        entity_type: Any,
        entity_id: Any,
    ) -> None:
        if not isinstance(variant, dict):
            self.error(location, "must be an object")
            return

        for field in ("path", "width", "height"):
            if field not in variant:
                self.error(f"{location}.{field}", "required field is missing")

        path_value = variant.get("path")
        path_is_safe = self.validate_path(path_value, f"{location}.path")

        for dimension in ("width", "height"):
            value = variant.get(dimension)
            if not is_integer(value) or value <= 0:
                self.error(f"{location}.{dimension}", "must be a positive integer")

        if not path_is_safe:
            return

        assert isinstance(path_value, str)
        relative_path = PurePosixPath(path_value)
        file_match = VERSIONED_FILE.fullmatch(relative_path.name)
        if file_match is None:
            self.error(
                f"{location}.path",
                "filename must match <artwork-id>-<variant>-v<positive-version>.<extension>",
            )
        else:
            if artwork_id is not None and file_match.group("artwork") != artwork_id:
                self.error(f"{location}.path", "filename artwork id does not match artwork record")
            if file_match.group("variant") != variant_name:
                self.error(f"{location}.path", f"filename must use the {variant_name!r} variant")

        if entity_type in TYPE_DIRECTORIES and is_integer(entity_id) and entity_id > 0:
            parts = relative_path.parts
            expected_tail = (TYPE_DIRECTORIES[entity_type], str(entity_id), relative_path.name)
            if len(parts) != 4 or parts[0] != "images" or tuple(parts[1:]) != expected_tail:
                expected = f"images/{TYPE_DIRECTORIES[entity_type]}/{entity_id}/{relative_path.name}"
                self.error(f"{location}.path", f"must match entity category and id: {expected!r}")

        file_path = self.project_root.joinpath(*relative_path.parts)
        if not file_path.is_file():
            self.error(f"{location}.path", f"referenced file does not exist: {path_value!r}")

    def validate_path(self, path_value: Any, location: str) -> bool:
        if not isinstance(path_value, str) or not path_value:
            self.error(location, "must be a non-empty relative POSIX path")
            return False
        if "\\" in path_value:
            self.error(location, "must use forward slashes")
            return False
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", path_value) or path_value.startswith(("//", "/")):
            self.error(location, "must not be an absolute URL or path")
            return False
        if "?" in path_value or "#" in path_value:
            self.error(location, "must not contain a query or fragment")
            return False

        raw_parts = path_value.split("/")
        relative_path = PurePosixPath(path_value)
        if any(part in {"", ".", ".."} for part in raw_parts):
            self.error(location, "must not contain empty, current, or parent path segments")
            return False
        if relative_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
            self.error(location, f"extension must be one of: {allowed}")
            return False

        resolved_path = self.project_root.joinpath(*relative_path.parts).resolve()
        try:
            resolved_path.relative_to(self.project_root.resolve())
        except ValueError:
            self.error(location, "must stay within the project directory")
            return False
        return True


def main() -> int:
    manifests = sorted(PROJECTS_ROOT.glob("*/manifest.json"))
    if not manifests:
        print("ERROR: no projects/*/manifest.json files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    for manifest_path in manifests:
        errors.extend(ManifestValidator(manifest_path).validate())

    if errors:
        print(f"Asset validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    noun = "manifest" if len(manifests) == 1 else "manifests"
    print(f"Validated {len(manifests)} project {noun} successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
