from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).parent
DEFINITIONS = ROOT / "definitions"


def _canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_definition(concept_id: str, version: int) -> dict:
    if (concept_id, version) != ("com.example/progressive-result", 1):
        raise KeyError(f"Unknown concept: {concept_id}@{version}")

    path = DEFINITIONS / "progressive-result.json"
    definition = json.loads(path.read_text(encoding="utf-8"))

    payload = deepcopy(definition)
    payload["provenance"].pop("digest", None)
    digest = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
    definition["provenance"]["digest"] = f"sha256:{digest}"
    return definition


def list_definitions() -> list[dict]:
    definition = load_definition("com.example/progressive-result", 1)
    return [
        {
            "id": definition["id"],
            "version": definition["version"],
            "kind": definition["kind"],
            "publisher": definition["provenance"]["publisher"],
            "digest": definition["provenance"]["digest"],
        }
    ]
