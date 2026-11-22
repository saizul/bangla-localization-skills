import json

import pytest

from conftest import FIXTURES, load_script, run_script

SKILL = "bangla-seo-content"
SCRIPT = "banglish_variants.py"
bv = load_script(SKILL, SCRIPT)


@pytest.mark.parametrize(
    "word,expected_first,also",
    [
        ("বাংলাদেশ", "bangladesh", []),
        ("ঢাকা", "dhaka", []),
        ("কলম", "kolom", ["kalom"]),
        ("আমরা", "amra", []),
        ("সরকারি", "sorkari", ["sarkari", "shorkari"]),
        ("চাকরি", "chakri", ["chakori"]),
        ("চট্টগ্রাম", "chottogram", ["chattogram"]),
        ("ভালোবাসা", "bhalobasa", ["valobasa", "bhalobasha"]),
        ("শাড়ি", "shari", ["sari"]),
        ("বাড়ি", "bari", ["badi"]),
        ("আয়না", "ayna", []),
        ("নামাজ", "namaj", ["namaz"]),
    ],
)
def test_word_variants(word, expected_first, also):
    variants = bv.word_variants(word, 10)
    assert variants[0] == expected_first
    for v in also:
        assert v in variants


def test_precomposed_and_decomposed_nukta_match():
    decomposed = "বাড়ি"  # বাড়ি with ড + nukta
    precomposed = "বাড়ি"  # বাড়ি with U+09DC
    assert bv.word_variants(decomposed, 5) == bv.word_variants(precomposed, 5)


def test_multiword_keyword_and_latin_tokens():
    variants = bv.keyword_variants("iPhone ১৫ এর দাম", 6)
    assert variants[0] == "iphone 15 er dam"
    kv = bv.keyword_variants("ভালোবাসার গল্প", 8)
    assert "bhalobasar golpo" in kv and "valobasar golpo" in kv
    assert len(kv) == len(set(kv)) <= 8


def test_zero_width_ignored():
    assert bv.word_variants("বাং‍লা", 3)[0] == "bangla"


def test_cli(tmp_path):
    r = run_script(SKILL, SCRIPT, "--json", "--max", "3", "সরকারি চাকরি")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert data["সরকারি চাকরি"][0] == "sorkari chakri" and len(data["সরকারি চাকরি"]) == 3
    r = run_script(SKILL, SCRIPT, "--file", str(FIXTURES / SKILL / "seeds.txt"), "--csv")
    lines = r.stdout.splitlines()
    assert lines[0] == "keyword,variant" and any("bari bhara" in ln for ln in lines)
    assert not any("seed keywords" in ln for ln in lines)
    r = run_script(SKILL, SCRIPT, "--file", "-", stdin="ঢাকা\n")
    assert r.stdout.strip() == "ঢাকা: dhaka"
    assert run_script(SKILL, SCRIPT, "hello world").returncode == 2
    assert run_script(SKILL, SCRIPT, "--file", str(tmp_path / "nope.txt")).returncode == 2
    assert run_script(SKILL, SCRIPT).returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
