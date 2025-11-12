from pathlib import Path

import pandas as pd

from modbus_map_maker.template_store import (
    store_template,
    list_templates,
    find_template,
    clone_template,
)


def _make_sample_excel(path: Path) -> None:
    data = {
        "device": ["DEV"],
        "name": ["POINT"],
        "address": [1],
        "dtype": ["INT16"],
        "scale": [1.0],
        "offset": [0.0],
    }
    df = pd.DataFrame(data)
    df.to_excel(path, index=False)


def test_store_and_find_template(tmp_path, monkeypatch):
    store_dir = tmp_path / "templates"
    monkeypatch.setenv("MODBUS_MAP_MAKER_TEMPLATE_DIR", str(store_dir))

    source = tmp_path / "mapping.xlsx"
    _make_sample_excel(source)

    info = store_template(source, name="Production Map")
    assert info.path.exists()
    assert info.slug.startswith("production-map")
    assert info.display_name == "Production Map"

    templates = list_templates()
    assert len(templates) == 1
    listed = templates[0]
    assert listed.slug == info.slug
    assert listed.display_name == "Production Map"
    assert listed.path == info.path

    fetched = find_template(info.slug)
    assert fetched.path == info.path
    assert fetched.display_name == "Production Map"


def test_clone_template(tmp_path, monkeypatch):
    store_dir = tmp_path / "templates"
    monkeypatch.setenv("MODBUS_MAP_MAKER_TEMPLATE_DIR", str(store_dir))

    source = tmp_path / "mapping.xlsx"
    _make_sample_excel(source)

    info = store_template(source)

    destination_dir = tmp_path / "workspace"
    cloned_path = clone_template(info.slug, destination_dir)

    assert cloned_path.exists()
    assert cloned_path.parent == destination_dir
    assert cloned_path.name == info.path.name
    assert cloned_path != info.path

    # cloning without overwrite should fail when file exists
    try:
        clone_template(info.slug, cloned_path)
    except FileExistsError:
        pass
    else:
        raise AssertionError("Expected FileExistsError when destination exists")

    # overwriting should succeed
    overwritten = clone_template(info.slug, cloned_path, overwrite=True)
    assert overwritten == cloned_path
