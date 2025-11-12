from __future__ import annotations
from typing import List, Dict, Any
import pandas as pd
from .models import MapEntry, MapSpec

REQUIRED = ["device","name","address","dtype","scale","offset"]

def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    remap = {c: c.strip().lower() for c in df.columns}
    df = df.rename(columns=remap)
    return df

def load_mapping(path: str) -> MapSpec:
    if path.lower().endswith((".xlsx",".xls")):
        df = pd.read_excel(path, engine="openpyxl")
    else:
        df = pd.read_csv(path)
    df = _normalize_columns(df)

    for col in REQUIRED:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    entries: List[MapEntry] = []
    for _, row in df.iterrows():
        base: Dict[str, Any] = {
            "device": str(row.get("device")).strip(),
            "name": str(row.get("name")).strip(),
            "address": int(row.get("address")),
            "dtype": str(row.get("dtype")).strip().upper(),
            "scale": float(row.get("scale", 1.0)),
            "offset": float(row.get("offset", 0.0)),
        }
        # Optionals
        for opt in ["unit","rw","function","byte_order","word_order","description"]:
            if opt in df.columns and pd.notna(row.get(opt)):
                base[opt] = str(row.get(opt)).strip()
        # Capture metadata for unknown columns
        meta = {}
        for c in df.columns:
            if c not in set(list(base.keys()) + ["unit","rw","function","byte_order","word_order","description"]):
                val = row.get(c)
                if pd.notna(val):
                    meta[c] = val
        base["meta"] = meta

        entries.append(MapEntry(**base))
    return MapSpec(entries=entries)
