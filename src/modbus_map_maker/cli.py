from __future__ import annotations
import typer, json, yaml
from pathlib import Path
from .excel import load_mapping
from .emitters import write_json, write_yaml, emit_python, emit_c_header, emit_defs
from .template_store import (
    store_template,
    list_templates,
    find_template,
    clone_template,
)

app = typer.Typer(help="Modbus Map Maker — from CSV/Excel to JSON/YAML + code emitters")
templates_app = typer.Typer(help="Manage reusable Excel templates.")


def _get_template(name: str):
    try:
        return find_template(name)
    except FileNotFoundError as exc:
        raise typer.BadParameter(str(exc)) from exc


@templates_app.command("upload")
def templates_upload(path: str, name: str = typer.Option(None, help="Optional name for the stored template.")):
    """Store an Excel workbook so it can be reused as a template."""

    info = store_template(Path(path), name=name)
    typer.echo(f"Stored template '{info.name}' at {info.path}")


@templates_app.command("list")
def templates_list():
    """List all stored templates."""

    templates = list_templates()
    if not templates:
        typer.echo("No templates stored yet.")
        return
    for info in templates:
        typer.echo(f"{info.name}: {info.path}")


@templates_app.command("edit")
def templates_edit(name: str):
    """Open a stored template in the default application for editing."""

    info = _get_template(name)
    typer.echo(f"Opening template '{info.name}' located at {info.path}")
    typer.launch(str(info.path))


@templates_app.command("path")
def templates_path(name: str):
    """Print the path to a stored template for external tooling."""

    info = _get_template(name)
    typer.echo(str(info.path))


@templates_app.command("copy")
def templates_copy(
    name: str,
    destination: str,
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Replace the destination file if it already exists."
    ),
    open_after: bool = typer.Option(
        False, "--open", help="Open the copied workbook once it has been created."
    ),
):
    """Copy a stored template to a new location for customization."""

    try:
        target = clone_template(name, Path(destination), overwrite=overwrite)
    except FileExistsError as exc:
        raise typer.BadParameter(str(exc)) from exc

    typer.echo(f"Copied template '{name}' to {target}")

    if open_after:
        typer.launch(str(target))


app.add_typer(templates_app, name="templates")

@app.command()
def validate(path: str):
    """Validate a CSV/Excel mapping file."""
    _ = load_mapping(path)
    typer.echo("OK: mapping is valid.")


@app.command()
def to_json(path: str, out: str = "mapping.json"):
    """Convert CSV/Excel to JSON spec."""
    spec = load_mapping(path)
    write_json(spec, out)
    typer.echo(f"Wrote {out}")


@app.command()
def to_yaml(path: str, out: str = "mapping.yaml"):
    """Convert CSV/Excel to YAML spec."""
    spec = load_mapping(path)
    write_yaml(spec, out)
    typer.echo(f"Wrote {out}")


@app.command()
def emit_code(spec_path: str, out_dir: str = "build"):
    """Emit code from JSON/YAML spec."""
    p = Path(spec_path)
    if p.suffix.lower() == ".json":
        spec_data = json.loads(p.read_text(encoding="utf-8"))
    else:
        spec_data = yaml.safe_load(p.read_text(encoding="utf-8"))

    from .models import MapSpec
    spec = MapSpec(**spec_data)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    emit_python(spec, out / "python_map.py")
    emit_c_header(spec, out / "mapping.h")
    emit_defs(spec, out / "defs.txt")
    typer.echo(f"Code emitted into {out}")


@app.command()
def generate(path: str, out: str = "build"):
    """From CSV/Excel to all outputs (JSON/YAML + code)."""
    spec = load_mapping(path)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)

    write_json(spec, out_dir / "mapping.json")
    write_yaml(spec, out_dir / "mapping.yaml")
    emit_python(spec, out_dir / "python_map.py")
    emit_c_header(spec, out_dir / "mapping.h")
    emit_defs(spec, out_dir / "defs.txt")
    typer.echo(f"All outputs generated in {out_dir}")


if __name__ == "__main__":
    app()
