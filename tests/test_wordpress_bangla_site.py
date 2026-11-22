import json
import os
import shutil

from conftest import FIXTURES, load_script, run_script

SKILL = "wordpress-bangla-site"
SCRIPT = "wp_lang_audit.py"
wp = load_script(SKILL, SCRIPT)
F = FIXTURES / SKILL


def by_check(result):
    return {(f["component"], f["check"]) for f in result["findings"]}


def test_partial_site():
    result = wp.audit(F / "partial")
    found = by_check(result)
    assert ("wp-config.php", "wplang") in found
    assert ("core", "admin-missing") in found
    assert ("plugin:contact-lite", "missing") in found
    assert ("theme:bd-news", "completion") in found
    assert ("theme:bd-news", "mo-missing") in found
    assert ("theme:bd-news", "l10n-php") in found
    assert any(c == "locale-name" for _, c in found)
    names = {c["name"]: c for c in result["components"]}
    assert names["Shop Helper"]["stats"]["percent"] == 100.0
    assert names["BD News"]["stats"] == {
        "total": 4,
        "translated": 1,
        "fuzzy": 1,
        "untranslated": 2,
        "percent": 25.0,
        "plural_forms": "nplurals=2; plural=(n != 1);",
    }


def test_complete_site_is_clean():
    result = wp.audit(F / "complete" / "wp-content")
    assert result["findings"] == []
    assert {c["type"] for c in result["components"]} == {"core", "plugin", "theme"}


def test_stale_mo_and_wrong_plural_forms(tmp_path):
    site = tmp_path / "site"
    shutil.copytree(F / "complete", site)
    lang = site / "wp-content" / "languages" / "plugins"
    po = lang / "shop-helper-bn_BD.po"
    mo = lang / "shop-helper-bn_BD.mo"
    po.write_text(
        po.read_text(encoding="utf-8").replace("nplurals=2; plural=(n != 1);", "nplurals=1; plural=0;"),
        encoding="utf-8",
    )
    os.utime(mo, (1_700_000_000, 1_700_000_000))
    found = by_check(wp.audit(site))
    assert ("plugin:shop-helper", "mo-stale") in found
    assert ("plugin:shop-helper", "plural-forms") in found


def test_missing_core_and_languages_dir(tmp_path):
    (tmp_path / "wp-content" / "themes").mkdir(parents=True)
    found = by_check(wp.audit(tmp_path))
    assert ("core", "languages-dir") in found
    (tmp_path / "wp-content" / "languages").mkdir()
    assert ("core", "core-missing") in by_check(wp.audit(tmp_path))


def test_po_stats_counts_plurals_and_obsolete(tmp_path):
    po = tmp_path / "x.po"
    po.write_text(
        'msgid ""\nmsgstr ""\n"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n\n'
        'msgid "%s item"\nmsgid_plural "%s items"\nmsgstr[0] "%sটি পণ্য"\nmsgstr[1] ""\n\n'
        'msgid "Hello"\nmsgstr ""\n"হ্যালো"\n\n'
        '#~ msgid "Old"\n#~ msgstr "পুরনো"\n',
        encoding="utf-8",
    )
    stats = wp.po_stats(po)
    assert stats["total"] == 2 and stats["translated"] == 1 and stats["untranslated"] == 1


def test_read_header():
    h = wp.read_header(F / "partial" / "wp-content" / "plugins" / "shop-helper" / "shop-helper.php")
    assert h["Plugin Name"] == "Shop Helper" and h["Text Domain"] == "shop-helper"


def test_cli(tmp_path):
    r = run_script(SKILL, SCRIPT, str(F / "partial"), "--json")
    assert r.returncode == 1
    assert json.loads(r.stdout)["locale"] == "bn_BD"
    r = run_script(SKILL, SCRIPT, str(F / "complete"), "--fail-on", "info")
    assert r.returncode == 0 and "Shop Helper" in r.stdout
    r = run_script(SKILL, SCRIPT, str(F / "partial"), "--fail-on", "error", "--min-percent", "10")
    assert r.returncode == 1  # theme .mo missing is an error
    assert run_script(SKILL, SCRIPT, str(tmp_path)).returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
