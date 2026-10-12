# Alignment Audit (Rules 85-100 / 16 items) — md-table-lint v0.1.1

| # | Check | Status | Evidence |
|---|-------|--------|----------|
| 1 | Safety/Ethics section | N/A | Not a security-research repo; read-only by construction (never writes files); fails closed (exit 2) on unreadable input |
| 2 | Privacy/dezero | PASS | No secrets/tokens/real names in any file; only contact line uses hcac4735@agent.qq.com (README License section); grep `(sk-\|ghp_\|api[_-]?key\s*=\s*['"][A-Za-z0-9])` → 0 hits |
| 3 | Copyright boundary | PASS | markdownlint / prettier / remark comparisons are structural restatements of their documented behavior, no >50-char copied text; MIT LICENSE present, "zhengming contributors" |
| 4 | Fact-check annotation | PASS | 61-check suite "~3 s" marked [Measured] with repro `python self_test.py`; "~1 s" lint timing marked ~; rendering claims qualitative |
| 5 | Confidence grading | PASS | Opener [High ≥80%] tied to the suite; R4 heuristic framed as "suggestive, not proof"; ≥2 explicit labels |
| 6 | PLAN B built-in | PASS | "Minimal Fallback (PLAN B)" section: awk cell-counting one-liner + visual separator scan, zero setup |
| 7 | Timeout preset | PASS | Quickstart states "~2 min" with ~1 s / ~3 s step markers |
| 8 | Rule-conflict arbitration | PASS | "Design Trade-offs" opens with priority order: no-false-tables > explainable findings > zero-dependency > coverage |
| 9 | Version changelog | PASS | CHANGELOG.md v0.1.0 + v0.1.1; v0.1.1 records documentation completion and suite re-verification |
| 10 | Exemption instruction | N/A | Session-level rule; static repo content not applicable |
| 11 | External-knowledge cutoff | PASS | "No direct equivalent found as of 2026-10-12" stated explicitly; markdownlint rule numbers cited as documented behavior |
| 12 | Assumption explicitness | PASS | "[Core Assumptions]" section with 4 items |
| 13 | Logic-check trio | PASS | self_test.py three-tier suite (functional / error / extreme-edge, incl. fence toggling, escaped pipes, empty input); `python self_test.py` → `SUMMARY: PASS 61/61` |
| 14 | Socratic question | PASS | FAQ "When NOT to use this tool?" with 4 anti-use-cases (HTML/grid tables, formatting needs, non-GFM dialects, full AST linting) |
| 15 | Pareto improvement | PASS | v0.1.1 documentation round: README explains the R4 warning-vs-error rationale and no-false-tables recognition strategy absent from the module docstring; traceable in CHANGELOG |
| 16 | Ultimate fallback (≤60-word opener) | PASS | First paragraph = 59 words, contains what-it-is and the "silently renders as garbage text" judgment sentence |

Second-order effects (rule 16 bonus): PASS — "Limits & Second-order Effects" covers lint-clean-but-unreadable tables, dropped visual checks, and the deliberate no-auto-repair stance.

Scan evidence: `grep -rEn "(sk-|ghp_|api[_-]?key\s*=\s*['\"][A-Za-z0-9])" .` → 0 hits; `grep -rn "hcac4735@agent.qq.com" README.md` → 1 hit.
