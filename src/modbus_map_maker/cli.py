from __future__ import annotations
import typer, json, yaml
from pathlib import Path
from .excel import load_mapping
from .emitters import write_json, write_yaml, emit_python, emit_c_header, emit_defs

app = typer.Typer(help="Modbus Map Maker — from CSV/Excel to JSON/YAML + code emitters")

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
