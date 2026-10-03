from __future__ import annotations

from registry import catalog_delta, knowledge_fingerprint, list_definitions, load_definition

PROTOCOL_VERSION = "2026-07-28"
SEMANTIC_EXTENSION = "com.example/semantic-discovery"


class ReferenceServer:
    def discover(self, client_fingerprint: str | None = None) -> dict:
        catalog = list_definitions()
        fingerprint = knowledge_fingerprint(catalog)
        return {
            "protocol_version": PROTOCOL_VERSION,
            "capabilities": {
                "tools": True,
                "extensions": [SEMANTIC_EXTENSION],
            },
            "semantic_knowledge": {
                "fingerprint": fingerprint,
                "matches_client": client_fingerprint == fingerprint,
                "delta_supported": True,
            },
        }

    def definitions_delta(self, known_catalog: list[dict]) -> dict:
        return catalog_delta(known_catalog)

    def definitions_get(self, concept_id: str, version: int) -> dict:
        return load_definition(concept_id, version)

    def get_demo_results(self) -> list[dict]:
        return [
            {
                "concept": {"id": "com.example/progressive-result", "version": 1},
                "result_type": "progressive",
                "complete": False,
                "sequence": 1,
                "data": {"message": "first partial result"},
            },
            {
                "concept": {"id": "com.example/progressive-result", "version": 1},
                "result_type": "progressive",
                "complete": True,
                "sequence": 2,
                "data": {"message": "final result"},
            },
        ]
