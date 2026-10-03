from __future__ import annotations

from registry import list_definitions, load_definition

PROTOCOL_VERSION = "2026-07-28"
SEMANTIC_EXTENSION = "com.example/semantic-discovery"


class ReferenceServer:
    def discover(self) -> dict:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "capabilities": {
                "tools": True,
                "extensions": [SEMANTIC_EXTENSION],
            },
            "semantic_catalog": list_definitions(),
        }

    def definitions_get(self, concept_id: str, version: int) -> dict:
        return load_definition(concept_id, version)

    def get_demo_results(self) -> list[dict]:
        return [
            {
                "concept": {
                    "id": "com.example/progressive-result",
                    "version": 1,
                },
                "result_type": "progressive",
                "complete": False,
                "sequence": 1,
                "data": {"message": "first partial result"},
            },
            {
                "concept": {
                    "id": "com.example/progressive-result",
                    "version": 1,
                },
                "result_type": "progressive",
                "complete": True,
                "sequence": 2,
                "data": {"message": "final result"},
            },
        ]
