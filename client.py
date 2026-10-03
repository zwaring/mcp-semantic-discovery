from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

CACHE_FILE = Path(__file__).parent / ".semantic-cache.json"


def _canonical_bytes(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


class SemanticClient:
    def __init__(self, server, cache_file: Path = CACHE_FILE):
        self.server = server
        self.cache_file = cache_file
        self.cache = self._load_cache()
        self.definition_lookups = 0

    def _load_cache(self) -> dict:
        if not self.cache_file.exists():
            return {}
        return json.loads(self.cache_file.read_text(encoding="utf-8"))

    def _save_cache(self) -> None:
        self.cache_file.write_text(
            json.dumps(self.cache, indent=2, sort_keys=True), encoding="utf-8"
        )

    @staticmethod
    def cache_key(concept_id: str, version: int) -> str:
        return f"{concept_id}@{version}"

    def discover(self) -> dict:
        return self.server.discover()

    def knows(self, concept_id: str, version: int) -> bool:
        return self.cache_key(concept_id, version) in self.cache

    def resolve(self, concept_id: str, version: int) -> dict:
        key = self.cache_key(concept_id, version)
        if key in self.cache:
            print(f"CACHE HIT   {key}")
            return self.cache[key]

        print(f"UNKNOWN     {key}")
        print(f"LOOKUP      definitions/get({key})")
        self.definition_lookups += 1
        definition = self.server.definitions_get(concept_id, version)
        self._validate_definition(definition, concept_id, version)
        self.cache[key] = definition
        self._save_cache()
        print(f"LEARNED     {key}")
        return definition

    def _validate_definition(
        self, definition: dict, concept_id: str, version: int
    ) -> None:
        if definition.get("id") != concept_id:
            raise ValueError("Definition ID does not match requested concept")
        if definition.get("version") != version:
            raise ValueError("Definition version does not match requested version")

        provenance = definition.get("provenance") or {}
        claimed = provenance.get("digest", "")
        if not claimed.startswith("sha256:"):
            raise ValueError("Definition does not contain a SHA-256 digest")

        payload = deepcopy(definition)
        payload["provenance"].pop("digest", None)
        actual = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
        if claimed != f"sha256:{actual}":
            raise ValueError("Definition digest verification failed")

    def consume(self, message: dict) -> str:
        concept = message.get("concept") or {}
        concept_id = concept.get("id")
        version = concept.get("version")
        if not concept_id or version is None:
            raise ValueError("Message does not identify its semantic concept")

        definition = self.resolve(concept_id, version)
        behavior = definition.get("behavior", {})
        fallback = definition.get("fallback", {})

        if message.get("complete") is False:
            action = behavior.get("on_receive") or fallback.get("behavior")
            return f"CONTINUE: {action}"
        return "FINALIZE: result is complete"
