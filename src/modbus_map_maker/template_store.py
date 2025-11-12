"""Utilities for managing reusable Excel mapping templates.

Templates are stored on disk so they can be reused as a starting point for
future mapping files. The storage location defaults to a folder inside the
user's home directory but can be overridden during tests (or by advanced
users) via the ``MODBUS_MAP_MAKER_TEMPLATE_DIR`` environment variable.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
import shutil
from pathlib import Path
from typing import Iterable, List, Optional

ENV_TEMPLATE_DIR = "MODBUS_MAP_MAKER_TEMPLATE_DIR"
_DEFAULT_DIRNAME = ".modbus_map_maker"


@dataclass(slots=True)
class TemplateInfo:
    """Metadata describing a stored template."""

    name: str
    path: Path


def _template_root() -> Path:
    """Return the directory that holds stored templates."""

    override = os.environ.get(ENV_TEMPLATE_DIR)
    if override:
        root = Path(override).expanduser()
    else:
        root = Path.home() / _DEFAULT_DIRNAME / "templates"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _slugify(text: str) -> str:
    text = text.strip()
    if not text:
        return "template"
    # Normalize to ASCII and collapse to lowercase, dash separated tokens
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"[^a-zA-Z0-9-]", "", text)
    text = text.strip("-").lower()
    return text or "template"


def _unique_path(directory: Path, slug: str, suffix: str) -> Path:
    candidate = directory / f"{slug}{suffix}"
    if not candidate.exists():
        return candidate
    index = 2
    while True:
        candidate = directory / f"{slug}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def store_template(source: Path, name: Optional[str] = None) -> TemplateInfo:
    """Copy an Excel file into the template storage directory.

    Args:
        source: Path to the Excel workbook that should be stored.
        name: Optional friendly name. If omitted the source stem is used.

    Returns:
        TemplateInfo describing the stored template.
    """

    if not source.exists():
        raise FileNotFoundError(source)

    suffix = source.suffix.lower()
    if suffix not in {".xlsx", ".xls"}:
        raise ValueError("Only .xlsx or .xls files can be stored as templates")

    slug = _slugify(name or source.stem)
    directory = _template_root()
    destination = _unique_path(directory, slug, suffix)
    shutil.copy2(source, destination)
    return TemplateInfo(name=destination.stem, path=destination)


def list_templates() -> List[TemplateInfo]:
    """Return all stored templates sorted alphabetically."""

    directory = _template_root()
    templates: List[TemplateInfo] = []
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in {".xlsx", ".xls"}:
            templates.append(TemplateInfo(name=file.stem, path=file))
    return sorted(templates, key=lambda info: info.name.lower())


def find_template(name: str) -> TemplateInfo:
    """Retrieve metadata for a stored template by its slug name."""

    directory = _template_root()
    matches: Iterable[Path] = directory.glob(f"{name}.*")
    for file in matches:
        if file.is_file() and file.suffix.lower() in {".xlsx", ".xls"}:
            return TemplateInfo(name=file.stem, path=file)
    raise FileNotFoundError(f"Template '{name}' was not found")


def remove_template(name: str) -> None:
    """Delete a stored template by name."""

    info = find_template(name)
    info.path.unlink(missing_ok=True)


def clone_template(
    name: str,
    destination: Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Copy a stored template to a user-selected location for editing.

    Args:
        name: Slug of the stored template to copy.
        destination: Target file or directory where the copy should be placed.
        overwrite: Whether to replace an existing file at the destination.

    Returns:
        Path to the copied workbook.
    """

    info = find_template(name)

    if destination.exists():
        if destination.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
            target = destination / info.path.name
        else:
            target = destination
            target.parent.mkdir(parents=True, exist_ok=True)
    else:
        if destination.suffix:
            target = destination
            target.parent.mkdir(parents=True, exist_ok=True)
        else:
            destination.mkdir(parents=True, exist_ok=True)
            target = destination / info.path.name

    if target.exists() and not overwrite:
        raise FileExistsError(
            f"Destination '{target}' already exists. Use overwrite=True to replace it."
        )

    shutil.copy2(info.path, target)
    return target

