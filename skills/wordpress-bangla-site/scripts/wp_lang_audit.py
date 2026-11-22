#!/usr/bin/env python3
"""Audit a WordPress install (offline, read-only) for Bangla (bn_BD) translation coverage.

Point it at the WordPress root or at wp-content. It reads files only; it never runs PHP,
WP-CLI or database queries. Reports:

  * core translation files for the locale (bn_BD.mo / .l10n.php, admin-bn_BD.*)
  * every plugin and theme (from its header "Text Domain:"), and whether a bn_BD translation
    exists in wp-content/languages/{plugins,themes}/ or the extension's own Domain Path
  * .po completion (translated, fuzzy, untranslated), .mo missing or older than .po,
    no .l10n.php (WordPress 6.5+ loads PHP translation files first)
  * files named for the wrong locale (bn.po, bn-BD.po instead of bn_BD)
  * WPLANG in wp-config.php (ignored since WordPress 4.0; the locale lives in the database)

Exit codes: 0 = complete, 1 = findings at or above --fail-on, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
HEADER_RE = re.compile(r"^[ \t/*#@]*([A-Za-z ]+):\s*(.+)$", re.M)


def finding(sev: str, component: str, check: str, message: str, fix: str = "") -> dict:
    return {"severity": sev, "component": component, "check": check, "message": message, "fix": fix}


def read_header(path: Path) -> dict[str, str]:
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:8192]
    except OSError:
        return {}
    out: dict[str, str] = {}
    for m in HEADER_RE.finditer(head):
        key = m.group(1).strip()
        if key in ("Plugin Name", "Theme Name", "Text Domain", "Domain Path", "Version", "Requires at least"):
            out.setdefault(key, m.group(2).strip().rstrip("*/").strip())
    return out


def po_stats(path: Path) -> dict:
    """Count entries in a .po file: total, translated, fuzzy, untranslated (header excluded)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    total = translated = fuzzy = 0
    plural_forms = ""
    for block in re.split(r"\n\s*\n", text):
        lines = [ln.strip() for ln in block.strip().splitlines()]
        if not lines or all(ln.startswith("#~") or not ln for ln in lines):
            continue
        is_fuzzy = any(ln.startswith("#,") and "fuzzy" in ln for ln in lines)
        msgid, msgstrs, current = [], [], None
        for ln in lines:
            if ln.startswith("#"):
                continue
            m = re.match(r'^(msgid|msgid_plural|msgstr(?:\[\d+\])?|msgctxt)\s+"(.*)"$', ln)
            if m:
                current = m.group(1)
                if current == "msgid":
                    msgid.append(m.group(2))
                elif current.startswith("msgstr"):
                    msgstrs.append(m.group(2))
                continue
            if ln.startswith('"') and current:
                if current == "msgid":
                    msgid.append(ln[1:-1])
                elif current.startswith("msgstr") and msgstrs:
                    msgstrs[-1] += ln[1:-1]
        if not msgid and not msgstrs:
            continue
        if "".join(msgid) == "":
            pf = re.search(r"Plural-Forms:\s*([^\\]+)", "".join(msgstrs))
            plural_forms = pf.group(1).strip() if pf else ""
            continue
        total += 1
        if is_fuzzy:
            fuzzy += 1
        elif msgstrs and all(s != "" for s in msgstrs):
            translated += 1
    pct = round(100 * translated / total, 1) if total else 100.0
    return {
        "total": total,
        "translated": translated,
        "fuzzy": fuzzy,
        "untranslated": total - translated - fuzzy,
        "percent": pct,
        "plural_forms": plural_forms,
    }


def find_wp_content(root: Path) -> Path:
    if (root / "wp-content").is_dir():
        return root / "wp-content"
    if (root / "plugins").is_dir() or (root / "themes").is_dir() or (root / "languages").is_dir():
        return root
    raise ValueError(f"{root}: not a WordPress root or wp-content directory")


def check_files(base: Path, stem: str, component: str, min_percent: float) -> tuple[list[dict], dict | None]:
    """Check stem.po/.mo/.l10n.php in base. Returns (findings, stats)."""
    out: list[dict] = []
    po, mo, php = base / f"{stem}.po", base / f"{stem}.mo", base / f"{stem}.l10n.php"
    stats = None
    if po.exists():
        stats = po_stats(po)
        if stats["percent"] < min_percent:
            out.append(
                finding(
                    "warning",
                    component,
                    "completion",
                    f"{po.name}: {stats['percent']}% translated ({stats['untranslated']} untranslated, "
                    f"{stats['fuzzy']} fuzzy of {stats['total']})",
                    "translate the remaining strings (Loco Translate, Poedit or translate.wordpress.org)",
                )
            )
        elif stats["fuzzy"]:
            out.append(
                finding(
                    "info",
                    component,
                    "fuzzy",
                    f"{po.name}: {stats['fuzzy']} fuzzy entries are not used",
                    "review and clear the fuzzy flag",
                )
            )
        pf = stats["plural_forms"].replace(" ", "")
        if pf and not pf.startswith("nplurals=2"):
            out.append(
                finding(
                    "warning",
                    component,
                    "plural-forms",
                    f"{po.name}: Plural-Forms '{stats['plural_forms']}'",
                    "use: nplurals=2; plural=(n != 1);",
                )
            )
        if not mo.exists():
            out.append(
                finding(
                    "error",
                    component,
                    "mo-missing",
                    f"{po.name} has no compiled {mo.name}",
                    f"wp i18n make-mo {po}",
                )
            )
        elif mo.stat().st_mtime + 1 < po.stat().st_mtime:
            out.append(
                finding(
                    "warning",
                    component,
                    "mo-stale",
                    f"{mo.name} is older than {po.name}",
                    f"wp i18n make-mo {po}  (and wp i18n make-php for WordPress 6.5+)",
                )
            )
    if (mo.exists() or po.exists()) and not php.exists():
        out.append(
            finding(
                "info",
                component,
                "l10n-php",
                f"no {php.name} (WordPress 6.5+ loads it faster than .mo)",
                f"wp i18n make-php {base}",
            )
        )
    return out, stats


def audit(root: Path, locale: str = "bn_BD", min_percent: float = 90.0) -> dict:
    wpc = find_wp_content(root)
    lang = wpc / "languages"
    findings: list[dict] = []
    components: list[dict] = []

    wp_config = None
    for cand in (wpc.parent / "wp-config.php", wpc.parent.parent / "wp-config.php"):
        if cand.exists():
            wp_config = cand
            break
    if wp_config:
        cfg = wp_config.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"define\(\s*['\"]WPLANG['\"]\s*,\s*['\"]([^'\"]*)['\"]", cfg)
        if m:
            findings.append(
                finding(
                    "info",
                    "wp-config.php",
                    "wplang",
                    f"WPLANG '{m.group(1)}' is ignored since WordPress 4.0",
                    f"remove it; set the language with: wp site switch-language {locale}",
                )
            )

    if not lang.is_dir():
        findings.append(
            finding(
                "error",
                "core",
                "languages-dir",
                "wp-content/languages does not exist",
                f"wp language core install {locale} --activate",
            )
        )
    else:
        if not any((lang / f"{locale}{ext}").exists() for ext in (".mo", ".l10n.php", ".po")):
            findings.append(
                finding(
                    "error",
                    "core",
                    "core-missing",
                    f"no core {locale} translation in languages/",
                    f"wp language core install {locale} --activate",
                )
            )
        else:
            f, stats = check_files(lang, locale, "core", min_percent)
            findings += f
            components.append(
                {
                    "type": "core",
                    "name": "WordPress",
                    "domain": "default",
                    "translation": "languages/",
                    "stats": stats,
                }
            )
        if not any((lang / f"admin-{locale}{ext}").exists() for ext in (".mo", ".l10n.php", ".po")) and any(
            (lang / f"{locale}{ext}").exists() for ext in (".mo", ".l10n.php")
        ):
            findings.append(
                finding(
                    "info",
                    "core",
                    "admin-missing",
                    f"no admin-{locale} files; wp-admin stays English",
                    f"wp language core update  (or reinstall {locale})",
                )
            )
        for wrong in sorted(lang.rglob("*")):
            if (
                wrong.suffix in (".po", ".mo")
                and re.search(r"(^|-)bn(-BD|_bd|-bd)?\.(po|mo)$", wrong.name)
                and locale not in wrong.name
            ):
                findings.append(
                    finding(
                        "warning",
                        str(wrong.relative_to(wpc)),
                        "locale-name",
                        f"{wrong.name} is not named for {locale}; WordPress will not load it",
                        f"rename to ...-{locale}{wrong.suffix}",
                    )
                )

    exts = []
    plugins = wpc / "plugins"
    if plugins.is_dir():
        for d in sorted(p for p in plugins.iterdir() if p.is_dir()):
            for php in sorted(d.glob("*.php")):
                h = read_header(php)
                if "Plugin Name" in h:
                    exts.append(("plugin", d, h))
                    break
    themes = wpc / "themes"
    if themes.is_dir():
        for d in sorted(p for p in themes.iterdir() if p.is_dir()):
            h = read_header(d / "style.css")
            if "Theme Name" in h:
                exts.append(("theme", d, h))

    for kind, d, h in exts:
        name = h.get("Plugin Name") or h.get("Theme Name") or d.name
        domain = h.get("Text Domain") or d.name
        comp = f"{kind}:{d.name}"
        info: dict = {"type": kind, "name": name, "domain": domain, "translation": None, "stats": None}
        locations = []
        if lang.is_dir():
            locations.append((lang / f"{kind}s", f"{domain}-{locale}"))
        dp = h.get("Domain Path", "/languages").strip("/") or "languages"
        if kind == "theme":
            locations.append((d / dp, locale))
            locations.append((d / dp, f"{domain}-{locale}"))
        else:
            locations.append((d / dp, f"{domain}-{locale}"))
        found = False
        for base, stem in locations:
            if any((base / f"{stem}{ext}").exists() for ext in (".mo", ".po", ".l10n.php")):
                f, stats = check_files(base, stem, comp, min_percent)
                findings += f
                info["translation"] = str((base / stem).relative_to(wpc))
                info["stats"] = stats
                found = True
                break
        if not found:
            sev = "warning" if kind == "theme" or "Text Domain" in h else "info"
            findings.append(
                finding(
                    sev,
                    comp,
                    "missing",
                    f"{name} ({domain}) has no {locale} translation",
                    f"wp language {kind} install {d.name} {locale}  (if translate.wordpress.org has one), "
                    f"or create one: wp i18n make-pot {d} {domain}.pot",
                )
            )
        if "Text Domain" not in h:
            findings.append(
                finding(
                    "info",
                    comp,
                    "text-domain",
                    f"{name} has no 'Text Domain:' header",
                    "add the header so WordPress can load its translations",
                )
            )
        components.append(info)
    return {"wp_content": str(wpc), "locale": locale, "components": components, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Offline, read-only audit of a WordPress install's Bangla (bn_BD) translation files.",
        epilog="Examples: wp_lang_audit.py /var/www/html | wp_lang_audit.py ./wp-content --json | "
        "wp_lang_audit.py . --min-percent 100 --fail-on info",
    )
    p.add_argument("path", type=Path, help="WordPress root or wp-content directory")
    p.add_argument("--locale", default="bn_BD", help="WordPress locale (default bn_BD)")
    p.add_argument("--min-percent", type=float, default=90.0, help="warn below this completion (default 90)")
    p.add_argument("--fail-on", choices=list(SEVERITY_ORDER), default="warning")
    p.add_argument("--json", action="store_true", help="print JSON")
    args = p.parse_args(argv)
    try:
        result = audit(args.path, args.locale, args.min_percent)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['wp_content']} (locale {result['locale']})\n")
        for c in result["components"]:
            s = c["stats"]
            pct = (
                f"{s['percent']}% of {s['total']}" if s else ("compiled only" if c["translation"] else "none")
            )
            print(f"  {c['type']:6} {c['name'][:34]:34} {c['domain'][:20]:20} {pct}")
        print()
        for f in result["findings"]:
            print(f"{f['severity'].upper():7} {f['component']}: {f['message']}")
            if f["fix"]:
                print(f"        fix: {f['fix']}")
        print(f"\n{len(result['findings'])} finding(s)")
    floor = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[f["severity"]] >= floor for f in result["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
