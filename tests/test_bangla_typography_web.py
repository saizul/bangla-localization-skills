import json

from conftest import FIXTURES, load_script, run_script

SKILL = "bangla-typography-web"
SCRIPT = "bn_css_lint.py"
lint = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL


def checks(findings):
    return {f["check"] for f in findings}


def test_bad_css():
    found = checks(lint.lint_path(F / "bad.css"))
    assert {
        "font-display",
        "unicode-range",
        "google-fonts",
        "font-stack",
        "line-height",
        "font-size",
        "letter-spacing",
        "word-break",
        "justify",
        "italic",
        "faux-bold",
        "legacy-font",
    } <= found


def test_bad_css_lines_and_media_queries():
    findings = lint.lint_path(F / "bad.css")
    lh = [f for f in findings if f["check"] == "line-height"]
    assert {f["line"] for f in lh} == {12, 26}  # body and p inside @media


def test_good_css_and_html_clean():
    assert lint.lint_path(F / "good.css") == []
    assert lint.lint_path(F / "good.html") == []


def test_bad_html():
    found = checks(lint.lint_path(F / "bad.html"))
    assert {"lang", "charset", "google-fonts", "font-stack", "line-height"} <= found


def test_font_shorthand_and_variables():
    css = "body { font: 16px/1.2 Arial, sans-serif; }\n.x { font-family: var(--font); }"
    found = lint.lint_rules(lint.parse_css(css), lint.Path("x.css"))
    assert {"font-stack", "line-height"} <= checks(found)
    assert all(f["line"] == 1 for f in found)


def test_lang_en_and_letter_spacing_normal_are_allowed():
    css = ":lang(en) h1 { letter-spacing: .1em; font-family: Inter, sans-serif; }\np { letter-spacing: normal; }"
    assert lint.lint_rules(lint.parse_css(css), lint.Path("x.css")) == []


def test_bengali_detection():
    assert lint.is_bengali_family("noto sans bengali", set())
    assert lint.is_bengali_family("my bangla font", set())
    assert lint.is_bengali_family("brand", {"brand"})
    assert not lint.is_bengali_family("roboto", set())


def test_unicode_range_marks_custom_font_as_bengali():
    css = (
        '@font-face { font-family: "Brand"; src: url(b.woff2); unicode-range: U+0980-09FE; }\n'
        'body { font-family: "Brand", sans-serif; line-height: 1.7; }'
    )
    found = lint.lint_rules(lint.parse_css(css), lint.Path("x.css"))
    assert checks(found) == {"font-display"}


def test_cli(tmp_path):
    bad = run_script(SKILL, SCRIPT, str(F / "bad.css"), "--json")
    assert bad.returncode == 1 and json.loads(bad.stdout)["count"] >= 12
    good = run_script(SKILL, SCRIPT, str(F / "good.css"), str(F / "good.html"), "--fail-on", "info")
    assert good.returncode == 0
    info_only = tmp_path / "i.css"
    info_only.write_text("p { text-align: justify; font-family: 'Noto Sans Bengali'; line-height: 1.7 }")
    assert run_script(SKILL, SCRIPT, str(info_only)).returncode == 0
    assert run_script(SKILL, SCRIPT, str(info_only), "--fail-on", "info").returncode == 1
    whole_dir = run_script(SKILL, SCRIPT, str(F))
    assert whole_dir.returncode == 1 and "bad.html" in whole_dir.stdout
    assert run_script(SKILL, SCRIPT, str(tmp_path / "missing.css")).returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
