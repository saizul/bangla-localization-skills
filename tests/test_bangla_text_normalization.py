import json
import unicodedata
from collections import Counter

import pytest

from conftest import FIXTURES, load_script, run_script

SKILL = "bangla-text-normalization"
SCRIPT = "bn_normalize.py"
bn = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL
ZWJ, ZWNJ, HASANTA = "‍", "‌", "্"


def norm(text, **kw):
    counts = Counter()
    return bn.normalize(text, counts=counts, **kw), counts


def test_mojibake_fixture():
    fixed, counts = norm((F / "mojibake.txt").read_text(encoding="utf-8"))
    assert fixed == "বাংলা ভাষা - আমাদের দেশ\n"
    assert counts["mojibake"] == 4  # one per mis-decoded word


def test_mojibake_with_undefined_cp1252_bytes():
    # "দ" is E0 A6 A6; "ঁ" is E0 A6 81 -> 0x81 is undefined in cp1252 and survives as U+0081
    broken = "চাঁদ".encode().decode("latin-1")
    assert norm(broken)[0] == "চাঁদ"


def test_broken_fixture_lines():
    fixed, counts = norm((F / "broken.txt").read_text(encoding="utf-8"))
    lines = fixed.splitlines()
    assert lines[0] == "আমি ভাত খাই।"
    assert lines[1] == "আপনি কেমন আছেন?"
    assert lines[2] == "চাঁদ উঠেছে"
    assert lines[3] == "হঠাৎ বৃষ্টি"
    assert lines[4].rstrip() == "বাংলা ভাষা"
    assert lines[5] == "র" + ZWJ + HASANTA + "যাব কাজ করে।"
    assert lines[6].startswith("কোন ")  # decomposed o-kar composed by NFC
    assert lines[7].endswith("অক্ষর।")
    for code in (
        "a-aa",
        "prebase-order",
        "mark-order",
        "khanda-ta",
        "zero-width",
        "duplicate-sign",
        "danda",
        "nfc",
    ):
        assert counts[code] >= 1, code


def test_broken_fixture_notes():
    notes = {n["code"] for n in bn.detect((F / "broken.txt").read_text(encoding="utf-8"))}
    assert {"dotted-circle", "mixed-digits"} <= notes


def test_clean_fixture_is_stable():
    text = (F / "clean.txt").read_text(encoding="utf-8")
    fixed, counts = norm(text)
    assert fixed == text and not counts
    assert bn.detect(text) == []


def test_bijoy_detected():
    notes = bn.detect((F / "bijoy.txt").read_text(encoding="utf-8"))
    assert [n["code"] for n in notes] == ["bijoy"]
    assert bn.detect("Free delivery and Ges Kiv are words") == []  # needs mostly Bijoy text and markers


@pytest.mark.parametrize(
    "text,expected",
    [
        ("র" + ZWJ + HASANTA + "য", "র" + ZWJ + HASANTA + "য"),  # ra + ya-phala kept
        ("ক" + HASANTA + ZWNJ + "ষ", "ক" + HASANTA + ZWNJ + "ষ"),  # visible hasanta kept
        ("ক" + HASANTA + ZWJ + "ষ", "ক" + HASANTA + ZWJ + "ষ"),  # half form kept
        (ZWNJ + "বাংলা" + ZWJ, "বাংলা"),  # boundaries removed
        ("বা" + ZWJ + ZWJ + "ং", "বাং"),
        ("ক" + HASANTA + ZWJ + ZWJ + "ষ", "ক" + HASANTA + ZWJ + "ষ"),  # doubled joiner collapsed
        ("﻿বাংলা­", "বাংলা"),
    ],
)
def test_joiners(text, expected):
    assert norm(text)[0] == expected


def test_nukta_policy():
    pre = "বাড়ি"
    dec = "বাড়ি"
    assert norm(pre)[0] == dec
    assert norm(dec, nukta="precomposed")[0] == pre
    assert unicodedata.is_normalized("NFC", norm(pre)[0])


def test_prebase_cluster_and_no_false_reorder():
    assert norm(" \u09bfক্ষক")[0] == " ক্ষিক"  # i-kar typed before a conjunct
    assert norm("\u09c7দশ")[0] == "দেশ"
    assert norm("কেমন")[0] == "কেমন"  # already correct
    assert norm("কে")[0] == "কে"


def test_digits_option():
    assert norm("২০26 সাল", digits="bn")[0] == "২০২৬ সাল"
    assert norm("২০২৬ সাল", digits="en")[0] == "2026 সাল"


def test_ascii_pipe_only_after_bangla():
    assert norm("a | b")[0] == "a | b"
    assert norm("শেষ||")[0] == "শেষ॥"


def test_cli_check_fix_in_place(tmp_path):
    r = run_script(SKILL, SCRIPT, "check", str(F / "clean.txt"))
    assert r.returncode == 0 and "ok" in r.stdout
    r = run_script(SKILL, SCRIPT, "check", str(F / "broken.txt"), "--json")
    assert r.returncode == 1
    report = json.loads(r.stdout)["files"][0]
    assert report["changed"] and report["fixes"]["a-aa"] == 1
    r = run_script(SKILL, SCRIPT, "fix", "-", stdin=(F / "mojibake.txt").read_text(encoding="utf-8"))
    assert r.returncode == 0 and r.stdout.startswith("বাংলা ভাষা")
    target = tmp_path / "bn.json"
    target.write_text('{"a": "অামি"}', encoding="utf-8")
    r = run_script(SKILL, SCRIPT, "fix", str(target), "--in-place")
    assert r.returncode == 0 and "rewritten" in r.stdout
    assert json.loads(target.read_text(encoding="utf-8"))["a"] == "আমি"
    assert (tmp_path / "bn.json.bak").read_text(encoding="utf-8") == '{"a": "অামি"}'
    assert run_script(SKILL, SCRIPT, "check", str(tmp_path / "missing.txt")).returncode == 2
    assert run_script(SKILL, SCRIPT, "check", "-", "--in-place").returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
