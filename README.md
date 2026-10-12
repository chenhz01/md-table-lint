# md-table-lint

md-table-lint lints Markdown tables for four defect classes: inconsistent column counts, malformed alignment rows, missing header rows, and unescaped pipes inside cells. Code fences are skipped automatically. Use it in CI to keep docs tables renderable — a broken table silently renders as garbage text on every static-site generator. Confidence: High (≥80%) for the four rule classes, per the 61-check suite.

<p align="center"><img src="docs/demo.gif" alt="demo" width="720"></p>

## Problem

Markdown tables fail silently: a row with one missing cell still *renders*, just misaligned; a table whose header was deleted renders the separator row as literal text; a pipe inside a cell (`C:\path | other`) splits into phantom columns. Reviewers catch these by eye, when they catch them at all. Documentation sites accumulate hundreds of tables with no automated gate.

## How it works

1. **Table detection** — a table is a pipe line followed by a separator row, plus subsequent pipe lines; ` ``` `/` ~~~ ` fenced blocks are tracked and skipped, respecting the fence marker.
2. **Cell splitting** — outer pipes optional; only *unescaped* pipes split cells, so `\|` stays inside one cell.
3. **Rules** —
   - **R1 col-consistency** (error): data row cell count ≠ header cell count.
   - **R2 align-row** (error): separator cells must match `:?-+:?` and match the header count.
   - **R3 header-required** (error): a separator row with no real header above it — including orphan separators anywhere in the document.
   - **R4 pipe-escaping** (warning): a row whose count differs *and* containing `\|` is diagnosed as an escaping problem, not a column-count problem.
4. **Exit contract** — report lists findings with line numbers; exit 1 if any error, 0 if clean or warnings only.

## Quickstart (~2 min)

```bash
# step 1: lint a file (~1 s)
python tablelint.py README.md
# step 2: CI mode, machine-readable
python tablelint.py docs.md --json
# stdin works too
cat README.md | python tablelint.py
# full suite (~3 s)
python self_test.py   # SUMMARY: PASS 61/61 [Measured]
```

Library use: `lint_text(text)` → `{"tables": n, "findings": [...]}`.

## Why not X? (as of 2026-10-12)

**No direct equivalent found as of 2026-10-12** — no standalone stdlib-only Markdown-table linter covering header-presence and pipe-escaping rules was located in the searched space. Nearest adjacent options:

- **markdownlint (Node.js, MD055/MD056/MD057)** — general Markdown linting with table rules (consistent pipe counts, bordered style); requires the Node toolchain and does not separate "escaping problem" from "column-count problem" the way R4 does. Structural restatement of its documented rules.
- **prettier --check** — reformats tables and flags parse breakage indirectly; it rewrites files rather than reporting findings, and its table handling does not explain *why* a row is broken.
- **markdown-it / remark parse validation** — full parsers tolerate malformed tables by design (garbage-in-garbage-out rendering), so they never raise on the defects this linter targets.

## Minimal Fallback (PLAN B)

No Python: `awk -F'|' 'NF>1 {print NR": "NF-1" cells"}' README.md | sort | uniq -c -f1`-style cell counting catches inconsistent column counts; visually scan for lines matching `^\s*\|?\s*-{3,}` that lack a header line above. You lose fence-awareness, R4 diagnosis, and the exit-code contract.

## Design Trade-offs

Priority order: **no-false-tables > explainable findings > zero-dependency > coverage**. Tables are recognized only by the header+separator pattern (GFM), not by any pipe-containing line — stricter recognition means orphan separators are *reported* (R3) rather than mis-parsed as tables. R4 is a warning, not an error: the heuristic (count mismatch + `\|` present) is suggestive, and misclassifying an author's intent as a hard error would train people to ignore the linter.

## Limits & Second-order Effects

- GFM tables only: pipe-tables inside HTML blocks, grid tables, and multi-line cells are out of scope.
- Inline code containing pipes (`a | b` in backticks) breaks cell counts — currently surfaced via R1/R4, not auto-fixed.
- Fence detection tracks ` ``` `/` ~~~ ` markers only; indented code blocks containing table-like text can confuse detection.
- Second-order: teams that add the linter may stop rendering docs before publishing — a lint-clean table can still be *ugly* (huge alignment padding, wide cells); linting checks structure, not readability. Keep a visual check in the release path.
- R3's orphan-separator scan reports line numbers, not fixes; auto-repair was deliberately left out to keep the tool read-only.

## FAQ

**Why is R4 only a warning?** Because "count differs AND contains `\|`" is a heuristic hint that escaping was attempted, not proof; the author may genuinely want a different column count.

**Does it modify files?** No — read-only by construction; exit codes carry the CI verdict.

### When NOT to use this tool?

- Your docs use HTML tables or grid tables — out of scope, findings will be misses, not false positives.
- You want table *formatting* (alignment padding, style normalization) — use prettier or similar.
- Your Markdown dialect is not GFM — separator-row semantics may differ.
- You need AST-level doc linting across headings/links/lists too — use markdownlint and treat this as the table specialist.

## License

MIT — see `LICENSE`. Contact: hcac4735@agent.qq.com

---

[Core Assumptions]
- GFM pipe-table syntax is the dominant Markdown table form in docs repos.
- A separator row is an unambiguous table marker; its appearance without a header is always a defect.
- Unescaped pipes inside cells are more often mistakes than intent, hence R1/R4 defaults.
- No stdlib-only equivalent covering the four rules was found as of 2026-10-12.

---

Part of the [zhengming-toolbox](https://github.com/chenhz01/zhengming-toolbox) — 55 purpose-built AI-engineering tools across neglected niches.

Related tools: [event-replay-verifier](https://github.com/chenhz01/event-replay-verifier) · [idempotency-key-spec](https://github.com/chenhz01/idempotency-key-spec) · [timezone-safety-check](https://github.com/chenhz01/timezone-safety-check)
