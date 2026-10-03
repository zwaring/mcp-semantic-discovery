from __future__ import annotations

import argparse
from pathlib import Path

from client import CACHE_FILE, SemanticClient
from server import ReferenceServer


def run_pass(label: str) -> int:
    print(f"\n=== {label} ===")
    server = ReferenceServer()
    client = SemanticClient(server)

    discovery = client.discover()
    print("DISCOVER    protocol=", discovery["protocol_version"])
    print("CATALOG     ", [f"{x['id']}@{x['version']}" for x in discovery["semantic_catalog"]])

    for message in server.get_demo_results():
        outcome = client.consume(message)
        print(f"MESSAGE {message['sequence']}: {outcome}")

    print(f"LOOKUPS     {client.definition_lookups}")
    return client.definition_lookups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset-cache", action="store_true")
    args = parser.parse_args()

    if args.reset_cache and CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f"Removed cache: {CACHE_FILE}")

    first = run_pass("PASS 1: client encounters an unknown concept")
    second = run_pass("PASS 2: client reuses learned semantics")

    print("\n=== RESULT ===")
    if first == 1 and second == 0:
        print("PASS: first run learned one concept; second run required zero definition lookups.")
    else:
        print(f"Unexpected lookup counts: first={first}, second={second}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
