from __future__ import annotations
from typing import Iterable
from jinja2 import Environment, PackageLoader, select_autoescape
import json, yaml, os
from .models import MapSpec, MapEntry

env = Environment(
    loader=PackageLoader("modbus_map_maker", "templates"),
    autoescape=select_autoescape()
)

def write_json(spec: MapSpec, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(spec.model_dump(), f, indent=2)

def write_yaml(spec: MapSpec, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(spec.model_dump(), f, sort_keys=False)

def emit_python(spec: MapSpec, out_path: str) -> None:
    tpl = env.get_template("python_map.j2")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tpl.render(entries=spec.entries))

def emit_c_header(spec: MapSpec, out_path: str) -> None:
    tpl = env.get_template("c_struct.h.j2")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tpl.render(entries=spec.entries))

def emit_defs(spec: MapSpec, out_path: str) -> None:
    tpl = env.get_template("plc_defs.txt.j2")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(tpl.render(by_device=spec.by_device()))
