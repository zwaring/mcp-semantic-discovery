from __future__ import annotations

import argparse

from client import CACHE_FILE, SemanticClient
from server import ReferenceServer


def run_pass(label: str) -> tuple[int, int]:
    print(f"\n=== {label} ===")
    server = ReferenceServer()
    client = SemanticClient(server)

    discovery = client.negotiate()
    print("DISCOVER    protocol=", discovery["protocol_version"])
    print("KNOWLEDGE   ", discovery["semantic_knowledge"]["fingerprint"])

    for message in server.get_demo_results():
        outcome = client.consume(message)
        print(f"MESSAGE {message['sequence']}: {outcome}")

    print(f"DELTA LOOKUPS      {client.delta_lookups}")
    print(f"DEFINITION LOOKUPS {client.definition_lookups}")
    return client.delta_lookups, client.definition_lookups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-cache", action="store_true")
    args = parser.parse_args()

    if args.reset_cache and CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f"Removed cache: {CACHE_FILE}")

    first = run_pass("PASS 1: fingerprints differ; client learns the missing concept")
    second = run_pass("PASS 2: fingerprints match; negotiation takes the fast path")

    print("\n=== RESULT ===")
    if first == (1, 1) and second == (0, 0):
        print("PASS: first run requested one delta and one definition; second run required neither.")
    else:
        print(f"Unexpected lookup counts: first={first}, second={second}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
