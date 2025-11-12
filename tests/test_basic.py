from modbus_map_maker.excel import load_mapping
from modbus_map_maker.emitters import write_json, write_yaml
from pathlib import Path
import json, yaml

def test_roundtrip(tmp_path: Path):
    spec = load_mapping(str(Path(__file__).parent.parent / "examples" / "mapping.csv"))
    out = tmp_path
    write_json(spec, out / "mapping.json")
    write_yaml(spec, out / "mapping.yaml")
    data_j = json.loads((out / "mapping.json").read_text())
    data_y = yaml.safe_load((out / "mapping.yaml").read_text())
    assert len(data_j["entries"]) == len(data_y["entries"]) == 4
