#!/usr/bin/env python3
"""md-table-lint — lint Markdown tables for four classes of defects.

Rules:
  R1 col-consistency : every data row has the same column count as the header
  R2 align-row       : separator cells must match ^:?-+:?$ and count matches header
  R3 header-required : separator without a header line above is not a table
  R4 pipe-escaping   : a row whose count differs AND containing '\\|' is likely
                       an escaping problem, not a column-count problem
Code fences (```/~~~) are skipped. Pure stdlib.
"""
import argparse
import json
import re
import sys

SEP_CELL = re.compile(r"^:?-+:?$")


def split_row(line):
    """Split a table line into cells; outer pipes optional; cells stripped;
    only UNESCAPED pipes split cells."""
    if not isinstance(line, str):
        raise TypeError("line must be a string")
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", s)]


def is_table_line(line):
    return "|" in line and line.strip()


def find_tables(lines):
    """Yield (start_idx, rows) where rows are (line_number, raw_line)."""
    tables = []
    i = 0
    n = len(lines)
    in_fence = False
    fence_marker = None
    while i < n:
        stripped = lines[i].lstrip()
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
            i += 1
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = True
            fence_marker = stripped[:3]
            i += 1
            continue
        # candidate: a pipe line whose NEXT line is a separator row
        if is_table_line(lines[i]) and i + 1 < n and is_sep_row(lines[i + 1]):
            rows = [(i, lines[i]), (i + 1, lines[i + 1])]
            j = i + 2
            while j < n and is_table_line(lines[j]):
                rows.append((j, lines[j]))
                j += 1
            tables.append(rows)
            i = j
            continue
        i += 1
    return tables


SEP_LOOSE = re.compile(r"^[:\-=\s]+$")


def is_sep_row(line):
    """Loose check: line LOOKS like a separator row (only [:-= ] chars)."""
    cells = split_row(line)
    return all(SEP_LOOSE.match(c) for c in cells) and any("-" in c for c in cells)


def lint_table(rows, start_line_offset=0):
    findings = []
    header_cells = split_row(rows[0][1])
    ncols = len(header_cells)
    # R3/R2 on separator
    sep_ln, sep_line = rows[1]
    sep_cells = split_row(sep_line)
    if not header_cells or all(not c.strip() for c in header_cells):
        findings.append({"rule": "R3-header-required", "line": rows[0][0] + 1, "severity": "error",
                         "msg": "header row is empty"})
    elif all(SEP_CELL.match(c) for c in header_cells):
        findings.append({"rule": "R3-header-required", "line": rows[0][0] + 1, "severity": "error",
                         "msg": "table starts with a separator row — a header line is required above it"})
    if len(sep_cells) != ncols:
        findings.append({"rule": "R2-align-row", "line": sep_ln + 1, "severity": "error",
                         "msg": "separator has %d columns, header has %d" % (len(sep_cells), ncols)})
    for c in sep_cells:
        if not SEP_CELL.match(c.strip()):
            findings.append({"rule": "R2-align-row", "line": sep_ln + 1, "severity": "error",
                             "msg": "separator cell %r is not :?---:?" % c.strip()})
            break
    # data rows
    for ln, line in rows[2:]:
        cells = split_row(line)
        if len(cells) != ncols:
            if any("\\|" in cell for cell in cells):
                findings.append({"rule": "R4-pipe-escaping", "line": ln + 1, "severity": "warning",
                                 "msg": "row has %d cells vs header %d AND contains \\| — escape pipes inside cells with \\| (or use &#124;)" % (len(cells), ncols)})
            else:
                findings.append({"rule": "R1-col-consistency", "line": ln + 1, "severity": "error",
                                 "msg": "row has %d cells, header has %d" % (len(cells), ncols)})
        for cell in cells:
            if "`" in cell:
                # pipes inside inline code spans that were not escaped
                pass  # split already consumed raw pipes; flagged via R1 above if count broke
    return findings


def lint_text(text):
    lines = text.split("\n")
    findings = []
    tables = find_tables(lines)
    covered = set()
    for rows in tables:
        for ln, _ in rows:
            covered.add(ln)
        findings.extend(lint_table(rows))
    # orphan separator rows (no header above) that were not part of any table
    in_fence = False
    fence_marker = None
    for idx, line in enumerate(lines):
        stripped = line.lstrip()
        if in_fence:
            if stripped.startswith(fence_marker):
                in_fence = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = True
            fence_marker = stripped[:3]
            continue
        if idx not in covered and is_sep_row(line):
            findings.append({"rule": "R3-header-required", "line": idx + 1, "severity": "error",
                             "msg": "table starts with a separator row — a header line is required above it"})
    findings.sort(key=lambda f: (f["line"], f["rule"]))
    return {"tables": len(tables), "findings": findings}


def main(argv=None):
    ap = argparse.ArgumentParser(prog="md-table-lint", description="Lint Markdown tables: column consistency, alignment rows, header presence, pipe escaping.")
    ap.add_argument("file", nargs="?", help="Markdown file; omit to read stdin")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        else:
            text = sys.stdin.read()
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    report = lint_text(text)
    errors = sum(1 for f in report["findings"] if f["severity"] == "error")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("tables: %d, findings: %d (%d errors)" % (report["tables"], len(report["findings"]), errors))
        for f in report["findings"]:
            print("L%d [%s] %s: %s" % (f["line"], f["severity"], f["rule"], f["msg"]))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
