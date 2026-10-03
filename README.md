# MCP Semantic Discovery Reference

## ELI5 — What is this project?

Imagine two people are talking. One person uses a new phrase the other person has never heard before — like **“no cap.”**

Instead of ending the conversation, the other person asks:

> “What does that mean?”

They learn that it means **“genuinely” or “truthfully,”** remember it, and keep talking. The next time they hear it, they already understand it.

This project explores how AI agents and MCP clients could do the same thing.

Today, software usually has to already know the protocol features and concepts another system will use. When something new appears, the usual answer is to update the software or move to a newer protocol version.

This prototype asks a different question:

> **What if an agent could quickly discover what changed, learn the meaning of a new concept, remember it, and continue — without requiring a full software upgrade?**

At the beginning of a conversation, the two systems compare a tiny **knowledge fingerprint** — similar to asking, “Do we already understand the same vocabulary?”

- If the fingerprints match, they immediately continue.
- If they differ, they ask only **what changed**.
- If a new concept is actually needed, the client retrieves its definition.
- The client validates and remembers that definition.
- Future conversations can skip the learning step.

The larger idea is to make communication between AI systems more adaptable: **teach the missing meaning instead of replacing the whole protocol.**

---

A small reference prototype for **semantic capability discovery** on top of MCP-style negotiation.

The goal: when a client encounters an unfamiliar concept, it can discover a machine-readable definition, validate it, cache it, and continue without requiring a software upgrade. A compact **knowledge fingerprint** makes subsequent negotiations nearly free when nothing has changed.

## Demo flow

```text
Client starts with its local semantic fingerprint
        |
        v
server/discover(client_fingerprint)
        |
        +---- fingerprints match ----> continue immediately
        |
        `---- fingerprints differ
                    |
                    v
              definitions/delta
                    |
                    v
          IDs/versions/digests that changed
                    |
                    v
        unknown concept is actually used
                    |
                    v
              definitions/get
                    |
                    v
 schema + semantics + behavior + fallback + provenance
                    |
                    v
           validate -> cache -> continue
```

This separates three costs:

1. **Fast agreement** — compare one fingerprint.
2. **Change discovery** — request only a small metadata delta if fingerprints differ.
3. **Learning** — fetch a full definition only when an unfamiliar concept is actually needed.

## Why this is different from protocol versioning

Protocol versioning answers:

> Which protocol grammar do we both speak?

Semantic discovery answers:

> Is our shared vocabulary identical? If not, what changed, what does the unfamiliar concept mean, and can I safely continue?

The fingerprint is computed from sorted concept IDs, versions, and definition digests. It is analogous to content-addressed synchronization: identical knowledge produces identical fingerprints without exchanging the entire catalog.

## Run

Requires Python 3.11+ and no third-party packages.

```bash
python demo.py --reset-cache
```

Expected behavior:

```text
PASS 1
FINGERPRINT DIFF: requesting semantic delta
DELTA        ['com.example/progressive-result@1']
UNKNOWN      com.example/progressive-result@1
LOOKUP       definitions/get(...)
LEARNED      com.example/progressive-result@1
DELTA LOOKUPS      1
DEFINITION LOOKUPS 1

PASS 2
FINGERPRINT MATCH: semantic vocabulary already synchronized
CACHE HIT    com.example/progressive-result@1
DELTA LOOKUPS      0
DEFINITION LOOKUPS 0

PASS: first run requested one delta and one definition; second run required neither.
```

## Files

- `server.py` — reference server with fingerprint-first discovery and delta support
- `client.py` — client with negotiation, unknown-concept resolution, validation, and caching
- `registry.py` — definition library, fingerprint calculation, and catalog-delta calculation
- `definitions/progressive-result.json` — machine-readable concept definition
- `demo.py` — two-pass demonstration of slow-path learning followed by fast-path agreement

## Proposed primitives

The prototype intentionally uses a tiny semantic bootstrap:

- `semantic_knowledge.fingerprint` — compact identity of the vocabulary understood by a participant
- `definitions/delta` — return only concept metadata that differs
- `definitions/get` — retrieve one full definition when it is actually needed

These names are experimental and are **not current MCP standard methods**.

## Definition shape

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

The natural-language description is useful to LLMs, while structured semantics and behavior allow deterministic clients and other model architectures to participate without depending on prose alone.

## Design principles

1. **Tiny bootstrap** — learn only a few discovery primitives.
2. **Fast common case** — one fingerprint comparison when knowledge is already synchronized.
3. **Delta synchronization** — exchange only what changed.
4. **Lazy learning** — fetch full definitions only when a changed concept is actually used.
5. **Concept identity** — stable ID + version + digest.
6. **Machine-readable semantics** — behavior is structural, not just prose.
7. **Safe fallback** — definitions explain graceful degradation.
8. **Trust and provenance** — definitions carry publisher and digest metadata.
9. **Caching** — learned semantics survive future connections.
10. **Protocol-agnostic** — this demonstrates a pattern rather than claiming these exact methods are standardized MCP.

## Important status

This repository is an experimental reference implementation for discussion. The semantic fingerprint, `definitions/delta`, `definitions/get`, and definition envelope shown here are proposed concepts, not current MCP standard methods.
