import json

import pytest

from conftest import FIXTURES, load_script, run_script

SKILL = "bangla-spellcheck-style"
SCRIPT = "bn_style_check.py"
sc = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL


def rules(findings):
    return [(f["rule"], f["found"]) for f in findings]


def test_bad_fixture():
    findings = sc.check_text((F / "bad.md").read_text(encoding="utf-8"))
    found = rules(findings)
    for wrong in ("সরকারী", "চাকুরী", "জানুয়ারী", "দূর্নীতি", "সহযোগীতা", "ষ্টেশন", "পৌছে"):
        assert ("spelling", wrong) in found, wrong
    kinds = {r for r, _ in found}
    assert {"spelling", "punctuation", "register", "style"} <= kinds
    first = findings[0]
    assert (first["line"], first["col"], first["suggest"]) == (1, 3, "সরকারি")


def test_good_fixture_clean():
    assert sc.check_text((F / "good.md").read_text(encoding="utf-8")) == []


@pytest.mark.parametrize(
    "text,wrong,right",
    [
        ("সরকারীভাবে জানানো হয়েছে", "সরকারী", "সরকারি"),  # inflected form
        ("বাড়ীতে কেউ নেই", "বাড়ী", "বাড়ি"),
        ("তার ব্যাবসা ভালো", "ব্যাবসা", "ব্যবসা"),
        ("দেরি করা উচিৎ নয়", "উচিৎ", "উচিত"),
        ("টেবিলের নীচে", "নীচে", "নিচে"),
    ],
)
def test_spelling_rules(text, wrong, right):
    hits = [f for f in sc.check_text(text) if f["rule"] == "spelling"]
    assert [(f["found"], f["suggest"]) for f in hits] == [(wrong, right)]


@pytest.mark.parametrize(
    "text",
    [
        "বেসরকারি প্রতিষ্ঠানে চাকরি",  # correct forms
        "জাতীয় সংগীত ও সুন্দরী প্রতিযোগিতা",  # tatsama ঈ stays
        "কষ্ট করে নষ্ট জিনিস স্পষ্ট দেখুন",  # native ষ্ট is correct
        "উচিতের চেয়ে বেশি",  # non-suffix rule must not match inflections... of correct word
        "দূরত্ব অনেক",  # দূর (far) is correct
    ],
)
def test_no_false_positives(text):
    assert [f for f in sc.check_text(text) if f["rule"] == "spelling"] == []


def test_decomposed_input_matches():
    decomposed = "বাড়ী"  # বাড়ী with ড + nukta
    precomposed = "বাড়ী"
    for text in (decomposed, precomposed):
        assert [f["rule"] for f in sc.check_text(text)] == ["spelling"]


def test_register_mixing():
    assert rules(sc.check_text("তিনি বলিলেন যে কাজটি হয়েছে।"))[0][0] == "register"
    assert sc.check_text("তিনি বলিলেন যে কাজটি হইয়াছে।") == []  # pure sadhu
    assert sc.check_text("তিনি বললেন যে কাজটি হয়েছে।") == []  # pure cholito


def test_tone():
    text = (F / "ui_formal.json").read_text(encoding="utf-8")
    formal = [f["found"] for f in sc.check_text(text, tone="formal")]
    assert formal == ["করো", "তোমার"]
    informal = [f["found"] for f in sc.check_text(text, tone="informal")]
    assert informal == ["আপনার", "আপনার"]
    assert sc.check_text(text) == []


def test_punctuation_and_digits():
    found = rules(sc.check_text("কাজ শেষ.\nআবার দেখা হবে |\nঠিক আছে ।\nশেষ।আবার"))
    assert ("punctuation", ".") in found and ("punctuation", "|") in found
    assert ("punctuation", " ।") in found and ("punctuation", "।") in found
    assert sc.check_text("অপেক্ষা করুন...") == []
    digits = sc.check_text("মোট 25 টি পণ্য", digits="bn")
    assert digits[0]["suggest"] == "২৫"
    assert sc.check_text("মোট ২৫টি", digits="en")[0]["suggest"] == "25"
    assert sc.check_text("English only. Fine.") == []


def test_apply_fixes():
    fixed = sc.apply_fixes("সরকারী বাড়ীতে যান |\n")
    assert fixed == "সরকারি বাড়িতে যান।\n"


def test_cli():
    r = run_script(SKILL, SCRIPT, str(F / "bad.md"), "--json")
    assert r.returncode == 1
    assert len(json.loads(r.stdout)["files"][0]["findings"]) >= 10
    assert run_script(SKILL, SCRIPT, str(F / "good.md"), "--fail-on", "info").returncode == 0
    r = run_script(SKILL, SCRIPT, str(F / "ui_formal.json"), "--tone", "formal")
    assert r.returncode == 1 and "tone" in r.stdout
    r = run_script(SKILL, SCRIPT, "-", "--fix", stdin="দূর্ঘটনা ঘটেছে |")
    assert r.stdout == "দুর্ঘটনা ঘটেছে।"
    assert run_script(SKILL, SCRIPT, "a.md", "b.md", "--fix").returncode == 2
    assert run_script(SKILL, SCRIPT, str(F / "missing.md")).returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
