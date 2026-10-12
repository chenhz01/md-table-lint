#!/usr/bin/env python3
"""self_test.py for md-table-lint — [A] functional / [B] exception paths / [C] extreme edges."""
import json
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tablelint  # noqa: E402

RESULTS = []


def check(name, fn):
    try:
        fn()
        RESULTS.append((name, True))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((name, False))
        print("  [FAIL] %s -> %r" % (name, e))


def assert_eq(a, b, msg=""):
    assert a == b, msg or "%r != %r" % (a, b)


def assert_true(c, m=""):
    assert c, m


def rules(text):
    return [f["rule"] for f in tablelint.lint_text(text)["findings"]]


GOOD = "| a | b |\n| --- | --- |\n| 1 | 2 |\n"

# ---------- [A] functional ----------
def a01():
    r = tablelint.lint_text(GOOD)
    assert_eq((r["tables"], r["findings"]), (1, []))
def a02(): assert_true("R1-col-consistency" in rules("| a | b |\n| --- | --- |\n| 1 |"))
def a03(): assert_true("R1-col-consistency" in rules("| a | b |\n| --- | --- |\n| 1 | 2 | 3 |"))
def a04(): assert_true("R2-align-row" in rules("| a | b |\n| --- |\n| 1 | 2 |"))
def a05(): assert_true("R2-align-row" in rules("| a | b |\n| === | --- |\n| 1 | 2 |"))
def a06(): assert_true("R3-header-required" not in rules(GOOD), "good table stays clean")
def a07(): assert_eq(tablelint.lint_text("no tables here")["tables"], 0)
def a08(): assert_true("R4-pipe-escaping" in rules("| a | b |\n| --- | --- |\n| x \\| y | 2 | 3 |"))
def a09():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 | 2 |")
    assert_eq(r["tables"], 1)
def a10():
    r = tablelint.lint_text("```python\n| a | not | a | table |\n```\n\n| a | b |\n| --- | --- |\n| 1 | 2 |")
    assert_eq((r["tables"], r["findings"]), (1, []), "code fence content ignored")
def a11(): assert_eq(tablelint.lint_text("~~~\n| x |\n~~~\n| a | b |\n| --- | --- |\n| 1 | 2 |")["findings"], [])
def a12():
    r = tablelint.lint_text(GOOD + "\n| c | d |\n| --- | --- |\n| 3 | 4 |")
    assert_eq(r["tables"], 2)
def a13(): assert_eq(tablelint.split_row("| a | b |"), ["a", "b"])
def a14(): assert_eq(tablelint.split_row("a | b"), ["a", "b"])
def a15(): assert_eq(tablelint.split_row("| a \\| b | c |"), ["a \\| b", "c"])
def a16(): assert_true(tablelint.is_sep_row("| --- | :---: |"))
def a17(): assert_true(not tablelint.is_sep_row("| a | b |"))
def a18():
    fs = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 |")["findings"]
    assert_eq(fs[0]["line"], 3, "1-based line numbers")
def a19():
    r = tablelint.lint_text("|  |  |\n| --- | --- |\n| 1 | 2 |")
    assert_true(any(f["rule"] == "R3-header-required" for f in r["findings"]))
def a20():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| ünïcödé | 中文 |")
    assert_eq(r["findings"], [])
def a21():
    here = os.path.dirname(os.path.abspath(__file__))
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    try:
        open(path, "w", encoding="utf-8").write("| a | b |\n| --- | --- |\n| 1 |")
        code = subprocess.run([sys.executable, os.path.join(here, "tablelint.py"), path], capture_output=True, text=True)
        assert_eq(code.returncode, 1)
    finally:
        os.unlink(path)
def a22():
    here = os.path.dirname(os.path.abspath(__file__))
    fd, path = tempfile.mkstemp(suffix=".md")
    os.close(fd)
    try:
        open(path, "w", encoding="utf-8").write(GOOD)
        code = subprocess.run([sys.executable, os.path.join(here, "tablelint.py"), path], capture_output=True, text=True)
        assert_eq(code.returncode, 0)
    finally:
        os.unlink(path)
def a23():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 | 2 |")
    assert_eq([f for f in r["findings"] if f["severity"] == "error"], [])
def a24():
    assert_eq(tablelint.lint_text("| a |\n| - |\n| 1 |\n| 2 |")["tables"], 1)

# ---------- [B] exception paths ----------
def b01():
    code = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tablelint.py"), "missing.md"], capture_output=True, text=True)
    assert_eq(code.returncode, 2)
def b02():
    here = os.path.dirname(os.path.abspath(__file__))
    code = subprocess.run([sys.executable, os.path.join(here, "tablelint.py"), "--help"], capture_output=True, text=True)
    assert_eq(code.returncode, 0)
def b03():
    code = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tablelint.py")], capture_output=True, text=True, input="")
    assert_eq(code.returncode, 0, "empty stdin -> no findings, exit 0")
def b04():
    code = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tablelint.py"), "--json"], capture_output=True, text=True, input=GOOD)
    rep = json.loads(code.stdout)
    assert_eq(rep["tables"], 1)
def b05():
    try:
        tablelint.split_row(None)
        assert False
    except TypeError:
        pass
def b06(): assert_eq(tablelint.lint_text("")["findings"], [])
def b07(): assert_eq(tablelint.lint_text("||")["tables"], 0, "single empty-cell pipe line with no separator is not a table")
def b08():
    r = tablelint.lint_text("| a | b |\n| --- | --- |")
    assert_eq(r["tables"], 1, "separator at EOF still forms a table")
def b09(): assert_true(tablelint.is_sep_row("-"))
def b10(): assert_eq(rules("| a | b |\n| --- | --- |\n| 1 | 2 |\n| 3 |"), ["R1-col-consistency"])

# ---------- [C] extreme edges ----------
def c01():
    row = "| " + " | ".join("h%d" % i for i in range(500)) + " |"
    sep = "|" + "---|" * 500
    broken = "|" + "1|" * 499
    r = tablelint.lint_text(row + "\n" + sep + "\n" + broken)
    assert_true(r["findings"], "500-col table with 499-cell row flagged")
def c02():
    many = "\n\n".join("| a | b |\n| --- | --- |\n| %d | %d |" % (i, i) for i in range(500))
    assert_eq(tablelint.lint_text(many)["tables"], 500)
def c03():
    r = tablelint.lint_text("| 中文 | 表格 |\n| --- | --- |\n| 是 | 的 |")
    assert_eq(r["findings"], [])
def c04():
    r = tablelint.lint_text("| emoji \U0001f680 | b |\n| --- | --- |\n| 1 | 2 |")
    assert_eq(r["findings"], [])
def c05():
    r = tablelint.lint_text("| a |\n| --- |\n| " + "x" * 100000 + " |")
    assert_eq(r["findings"], [])
def c06():
    nested_fences = "```\n```\n| a | b |\n| --- | --- |\n| 1 |"
    assert_true("R1-col-consistency" in rules(nested_fences), "closed empty fence ends fence mode")
def c07():
    r = tablelint.lint_text("| a | b |\n|  ---  |  ---  |\n| 1 | 2 |")
    assert_eq(r["findings"], [], "whitespace-padded separators valid")
def c08():
    r = tablelint.lint_text("| a | b |")
    assert_eq(r["tables"], 0, "lone pipe line without separator is not a table")
def c09():
    fs = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 | 2 | 3 |\n| x |")["findings"]
    assert_eq(len(fs), 2)
def c10():
    r = tablelint.lint_text("| a \\| b | c |\n| --- | --- |\n| 1 | 2 |")
    assert_eq(r["findings"], [], "escaped pipe in header counts as one cell")
def c11():
    crlf = GOOD.replace("\n", "\r\n")
    assert_eq(tablelint.lint_text(crlf)["findings"], [])
def c12():
    r = tablelint.lint_text("| a | b |\n|:--|--:|\n| 1 | 2 |")
    assert_eq(r["findings"], [], "aligned separators valid")
def c13():
    r = tablelint.lint_text("| a | b |\n| --- |\n| 1 | 2 |")
    assert_true(any(f["rule"] == "R2-align-row" for f in r["findings"]), "separator column count mismatch")
def c14():
    text = "\n\n".join(["| a | b |\n| --- | --- |\n| 1 | 2 |"] * 3)
    assert_eq(tablelint.lint_text(text)["tables"], 3)
def c15():
    fs = tablelint.lint_text("| a | b |\n| --- | --- |\n| \\| only |")["findings"]
    assert_true(any(f["rule"] == "R4-pipe-escaping" for f in fs), "cell starting with escaped pipe + short count -> R4")
def c16():
    r1 = tablelint.lint_text(GOOD)
    r2 = tablelint.lint_text(GOOD)
    assert_eq(r1, r2)

for fn in sorted([v for k, v in list(globals().items()) if k.startswith(("a0", "a1", "a2", "b0", "b1", "c0", "c1"))], key=lambda f: f.__name__):
    check(fn.__name__, fn)


# ---------- [R2] round-2 additions (separator-as-header, escaped-pipe edge, output contracts) ----------
def r201():
    fs = tablelint.lint_text("| --- | --- |\n| 1 | 2 |")["findings"]
    assert_true(any(f["rule"] == "R3-header-required" for f in fs), "separator-as-first-line must be flagged")
def r202():
    assert_eq(tablelint.lint_text(GOOD)["findings"], [])
def r203():
    assert_eq(tablelint.split_row("| a \\|"), ["a \\|"], "trailing escaped pipe stays in last cell")
def r204():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 | 2 |")
    assert_true(all(set(f) == {"rule", "line", "severity", "msg"} for f in r["findings"]))
def r205():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 |")
    assert_eq(r["findings"][0]["severity"], "error")
def r206():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| x \\| y | 2 | 3 |")
    assert_eq(r["findings"][0]["severity"], "warning")
def r207():
    code = subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tablelint.py"), "--json"], capture_output=True, text=True, input="")
    rep = json.loads(code.stdout)
    assert_eq((rep["tables"], rep["findings"]), (0, []))
def r208():
    text = "| a | b |\n| --- | --- |\n| 1 | 2 |\n| 3 | 4 | 5 |\n| 6 |"
    fs = tablelint.lint_text(text)["findings"]
    assert_eq([f["line"] for f in fs], [4, 5])
def r209():
    assert_true(tablelint.is_sep_row("| :---: |"))
    assert_true(not tablelint.is_sep_row("| :x: |"))
def r210():
    deep_unicode = "| \u00fc\u00f1\u00eec\u00f6d\u00e9 | \U0001f600 |\n| --- | --- |\n| 中文 | テスト |"
    assert_eq(tablelint.lint_text(deep_unicode)["findings"], [])
def r211():
    r = tablelint.lint_text("| a | b |\n| --- | --- |\n| 1 | 2 |\n\n| c | d |\n| --- | --- |\n| 3 |")
    assert_eq(r["tables"], 2)

for fn in sorted([v for k, v in list(globals().items()) if k.startswith("r2")], key=lambda f: f.__name__):
    check(fn.__name__, fn)

passed = sum(1 for _, ok_ in RESULTS if ok_)
for n, ok_ in RESULTS:
    if not ok_:
        print("FAIL:", n)
print("SUMMARY: PASS %d/%d" % (passed, len(RESULTS)))
sys.exit(0 if passed == len(RESULTS) else 1)
