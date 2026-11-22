import json

import pytest

from conftest import FIXTURES, load_script, run_script

SKILL = "bangla-ui-translation"
SCRIPT = "check_placeholders.py"
cp = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL


def checks(findings, severity=None):
    return {(f["key"], f["check"]) for f in findings if severity is None or f["severity"] == severity}


def test_good_json_has_no_findings():
    assert cp.run([F / "en.json", F / "bn_good.json"]) == []


def test_bad_json_findings():
    findings = cp.run([F / "en.json", F / "bn_bad.json"])
    errors = checks(findings, "error")
    assert ("greeting", "placeholder") in errors
    assert ("cart.items", "icu") in errors
    assert ("terms", "tags") in errors
    assert ("upload", "placeholder") in errors
    warnings = checks(findings, "warning")
    assert ("nav.settings", "missing") in warnings
    assert ("old_banner", "stale") in warnings
    assert ("save", "untranslated") in warnings
    assert ("reply", "icu") in warnings
    assert ("deleted", "punctuation") in checks(findings, "info")


def test_translated_placeholder_name_is_explained():
    out = cp.compare_strings("k", "Hello, {name}!", "হ্যালো, {নাম}!")
    assert any("must stay in English" in f["message"] for f in out)


def test_bangla_digit_printf_is_error():
    out = cp.compare_strings("k", "%1$s files", "%১$sটি ফাইল")
    assert any("Bangla digits" in f["message"] for f in out)


@pytest.mark.parametrize(
    "en,bn",
    [
        ("Uploaded %1$s of %2$s", "%2$sটির মধ্যে %1$sটি আপলোড হয়েছে"),
        ("Hi %(name)s", "হ্যালো %(name)s"),
        ("50% off today", "আজ ৫০% ছাড়"),
        ("{count, plural, one {# item} other {# items}}", "{count, plural, other {#টি পণ্য}}"),
        ("Welcome {{user}}, see $t(common.help)", "স্বাগতম {{user}}, দেখুন $t(common.help)"),
        ("Read <0>more</0>", "<0>আরও</0> পড়ুন"),
        ("It's {n, number} km", "দূরত্ব {n, number} কিমি"),
    ],
)
def test_valid_translations_pass(en, bn):
    assert [f for f in cp.compare_strings("k", en, bn) if f["severity"] == "error"] == []


def test_missing_printf_and_extra():
    out = cp.compare_strings("k", "Hello %s", "হ্যালো %d")
    msgs = " ".join(f["message"] for f in out)
    assert "missing printf placeholder '%s'" in msgs and "unexpected printf placeholder '%d'" in msgs


def test_icu_parser():
    args, opts, errors = cp.icu_parse(
        "{a} {count, plural, =0 {none} one {# {b}} other {# {c}}} {d, date, short}"
    )
    assert args == {"a", "count", "b", "c", "d"}
    assert opts == {"count:plural": {"=0", "one", "other"}}
    assert errors == []
    _, _, errors = cp.icu_parse("{count, plural, one {x}")
    assert errors
    args, _, _ = cp.icu_parse("Don't '{literal}' {real}")
    assert args == {"real"}


def test_unknown_plural_category_warns():
    out = cp.compare_strings("k", "{n, plural, one {#} other {#}}", "{n, plural, few {#} other {#}}")
    assert any(f["check"] == "icu" and f["severity"] == "warning" for f in out)


def test_flatten_json_and_arb():
    flat = cp.flatten_json({"a": {"b": "x", "@b": {"description": "meta"}}, "l": ["p", "q"], "n": 3})
    assert flat == {"a.b": "x", "l[0]": "p", "l[1]": "q"}


def test_po_single_file_good():
    assert cp.run([F / "bn_BD.po"]) == []


def test_po_parse_multiline_and_context():
    entries, header = cp.parse_po((F / "bn_BD.po").read_text(encoding="utf-8"))
    assert header["Plural-Forms"].startswith("nplurals=2")
    keys = {e["key"] for e in entries}
    assert "verb\x04Post" in keys
    multi = next(e for e in entries if e["msgid"].startswith("Your order"))
    assert multi["msgid"] == "Your order has been placed. We will email you when it ships."
    assert multi["msgstr"][0].endswith("ইমেইল করব।")


def test_pot_vs_po_bad():
    findings = cp.run([F / "app.pot", F / "bn_BD_bad.po"])
    found = {f["check"] for f in findings}
    assert {"plural-forms", "missing", "stale", "untranslated", "fuzzy", "placeholder", "tags"} <= found


def test_extra_pattern_laravel():
    import re

    out = cp.compare_strings("k", "Hello :name", "হ্যালো", re.compile(r":[a-z_]+"))
    assert any(":name" in f["message"] for f in out)


def test_cli_exit_codes_and_json():
    ok = run_script(SKILL, SCRIPT, str(F / "en.json"), str(F / "bn_good.json"))
    assert ok.returncode == 0
    bad = run_script(SKILL, SCRIPT, str(F / "en.json"), str(F / "bn_bad.json"), "--json")
    assert bad.returncode == 1
    data = json.loads(bad.stdout)
    assert data["counts"]["error"] >= 5
    warn_only = run_script(SKILL, SCRIPT, str(F / "app.pot"), str(F / "bn_BD.po"), "--fail-on", "warning")
    assert warn_only.returncode == 0
    usage = run_script(SKILL, SCRIPT, str(F / "en.json"))
    assert usage.returncode == 2
    missing = run_script(SKILL, SCRIPT, str(F / "nope.json"), str(F / "en.json"))
    assert missing.returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
