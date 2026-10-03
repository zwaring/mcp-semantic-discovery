from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).parent
DEFINITIONS = ROOT / "definitions"


def _canonical_bytes(value) -> bytes:
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


def knowledge_fingerprint(catalog: list[dict] | None = None) -> str:
    """Hash the ordered concept identities + digests, not the full documents."""
    catalog = catalog if catalog is not None else list_definitions()
    compact = [
        {"id": item["id"], "version": item["version"], "digest": item["digest"]}
        for item in sorted(catalog, key=lambda x: (x["id"], x["version"]))
    ]
    return "sha256:" + hashlib.sha256(_canonical_bytes(compact)).hexdigest()


def catalog_delta(known: list[dict]) -> dict:
    """Return only concepts whose identity/version/digest differ from the client view."""
    server_catalog = list_definitions()
    known_map = {(x["id"], x["version"]): x.get("digest") for x in known}
    server_map = {(x["id"], x["version"]): x.get("digest") for x in server_catalog}

    added_or_changed = [
        item
        for item in server_catalog
        if known_map.get((item["id"], item["version"])) != item["digest"]
    ]
    removed = [
        {"id": concept_id, "version": version}
        for concept_id, version in known_map
        if (concept_id, version) not in server_map
    ]
    return {
        "fingerprint": knowledge_fingerprint(server_catalog),
        "added_or_changed": added_or_changed,
        "removed": removed,
    }
