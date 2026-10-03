# MCP Semantic Discovery Reference

A small reference prototype for **semantic capability discovery** on top of MCP-style negotiation.

The goal is simple: when a client encounters an unfamiliar concept, it should be able to discover a machine-readable definition, validate it, cache it, and continue without requiring a software upgrade.

## Demo flow

```text
Client starts with no knowledge of `com.example/progressive-result@1`
        |
        v
server/discover
        |
        v
Server advertises the concept
        |
        v
Client sees an unknown concept
        |
        v
definitions/get
        |
        v
schema + semantics + behavior + fallback + provenance
        |
        v
validate -> cache -> continue
        |
        v
Second run: concept is already cached; no definition lookup needed
```

## Why this is different from protocol versioning

Protocol versioning answers:

> Which protocol grammar do we both speak?

Semantic discovery answers:

> I encountered a concept I do not understand. Where is its canonical definition, what behavior does it imply, and can I safely continue?

This prototype intentionally keeps those concerns separate.

## Run

Requires Python 3.11+ and no third-party packages.

```bash
python demo.py
```

To reset the learned-definition cache:

```bash
python demo.py --reset-cache
```

## Files

- `server.py` — tiny reference server that advertises a new semantic concept
- `client.py` — reference client with unknown-concept detection, resolution, validation, and caching
- `registry.py` — local definition library used by the server
- `definitions/progressive-result.json` — machine-readable concept definition
- `demo.py` — two-pass demonstration

## Definition shape

A concept definition can contain:

```json
{
  "id": "com.example/progressive-result",
  "version": 1,
  "kind": "semantic-concept",
  "description": "A result may be incomplete and followed by additional results.",
  "semantics": {
    "complete": false,
    "more_results_expected": true
  },
  "behavior": {
    "on_receive": "do_not_finalize_task",
    "next": "expect_additional_result"
  },
  "fallback": {
    "supported": true,
    "behavior": "buffer_until_complete"
  },
  "provenance": {
    "publisher": "com.example",
    "digest": "sha256:..."
  }
}
```

The natural-language description is useful to LLMs, while the structured semantics and behavior are suitable for conventional software and future model architectures that should not depend on prose alone.

## Design principles

1. **Tiny bootstrap** — clients need only know how to discover and fetch definitions.
2. **Concept identity** — each unfamiliar concept has a stable ID + version.
3. **Machine-readable semantics** — behavior is encoded structurally, not just in prose.
4. **Safe fallback** — definitions can explain how older clients should degrade gracefully.
5. **Trust and provenance** — definitions include publisher and digest metadata.
6. **Caching** — once learned, a definition is reused without another lookup.
7. **Protocol-agnostic** — this is a reference pattern, not a claim that these exact method names are already standardized MCP methods.

## Important status

This repository is an experimental reference implementation for discussion. `definitions/get` and the semantic definition envelope shown here are **proposed concepts**, not current MCP standard methods.
