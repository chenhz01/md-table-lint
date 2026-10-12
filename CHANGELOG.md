# Changelog

## v0.1.1 — 2026-10-12
- Documentation layer completed: README (Problem / How it works / Quickstart / why-not-X with the dated no-equivalent statement + markdownlint/prettier/parser comparisons / Minimal Fallback / Trade-offs / Limits / FAQ), ALIGNMENT.md 16-item audit.
- Self-test re-verified green, no code changes needed this round: `python self_test.py` → `SUMMARY: PASS 61/61`.

## v0.1.0 — 2026-10-11
- Initial implementation: fence-aware table detection (```/~~~ with marker tracking), escaped-pipe-aware cell splitting, rules R1 col-consistency / R2 align-row / R3 header-required (incl. orphan separator scan) / R4 pipe-escaping heuristic, line-numbered findings sorted by position, CLI (file/stdin, `--json`, exit 1 on errors, 2 on I/O failure).
- Self-test suite (functional / error / extreme-edge tiers).
