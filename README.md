# modbus-map-maker

CLI & library to **convert Modbus register maps** from CSV/Excel into **validated JSON/YAML** and emit **code stubs** (Python, C) and **PLC-style DEF lines**.

> One command to go from your spreadsheet to reproducible mappings and code.

## Quickstart

```bash
# 1) Create venv and install (editable for development)
python -m venv .venv && source .venv/bin/activate
pip install -e .

# 2) Try the example
modbus-map-maker generate examples/mapping.csv --out build

# 3) See outputs
tree build
# mapping.json, mapping.yaml, python_map.py, mapping.h, defs.txt
```

## CLI

```
Usage: modbus-map-maker [OPTIONS] COMMAND [ARGS]...

Commands:
  generate      From CSV/Excel to all outputs (JSON/YAML + code).
  validate      Validate a CSV/Excel mapping file.
  to-json       Convert CSV/Excel to JSON spec.
  to-yaml       Convert CSV/Excel to YAML spec.
  emit-code     Emit code from a JSON/YAML spec.
```

### CSV/Excel expected columns

Minimal columns (case-insensitive, extra columns are kept as metadata):

- `device` (str) — e.g. `RTUINV1_1`
- `name` (str) — e.g. `INV1_ET`
- `address` (int) — register starting address
- `dtype` (str enum) — one of: `INT16, UINT16, INT32, UINT32, INT32R, FLOAT32, FLOAT32R`
- `scale` (float) — multiplier (ex: `0.001`)
- `offset` (float) — addend (default 0)
- `unit` (str) — optional
- `rw` (str enum) — `R` or `W` or `RW` (optional)
- `function` (str enum) — `HR` (holding register) or `IR` (input register) (default HR)

Endianness:
- `byte_order` = `big|little` (default `big`)
- `word_order` = `normal|swapped` (default `normal`). `INT32R`/`FLOAT32R` implies swapped.

### Endianness helper

`dtype=INT32R` or `FLOAT32R` is a shorthand for `INT32/FLOAT32` with `word_order=swapped`.

## Outputs

- `mapping.json` / `mapping.yaml`: normalized spec, validated by Pydantic.
- `python_map.py`: list of dicts with rich metadata, ready to use.
- `mapping.h`: C header with a struct array (name, addr, type, scale, offset, unit).
- `defs.txt`: PLC-style `DEF_SCHEDA` / `DEF_CANALE` compatible stubs.

## Development

```bash
pytest -q
```

## Build & Publish (TestPyPI)

```bash
pip install build twine
python -m build
python -m twine upload -r testpypi dist/*
# then: pip install -i https://test.pypi.org/simple/ modbus-map-maker
```

## License

MIT
