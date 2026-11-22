#!/usr/bin/env python3
"""Check placeholder, ICU, HTML-tag and key parity between English and Bangla translation files.

Supported inputs:
  en.json bn.json      nested or flat JSON (i18next, react-intl, vue-i18n, next-intl, ARB)
  bn.po                one gettext PO file (msgid = English, msgstr = Bangla)
  en.pot bn.po         a template plus its translation (also reports missing/stale entries)

Placeholders understood: ICU/format {name} {0} {count, plural, ...}, i18next {{name}} and
$t(key), printf %s %d %1$s %(name)s %.2f, and HTML/JSX tags <b> </b> <a href=...> <0> <1/>.

Exit codes: 0 = ok, 1 = findings at or above --fail-on, 2 = usage or parse error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

BENGALI_RE = re.compile(r"[\u0980-\u09ff]")
BENGALI_DIGIT_RE = re.compile(r"[০-৯]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")
I18NEXT_RE = re.compile(r"\{\{\s*([^{}]+?)\s*\}\}")
I18NEXT_NEST_RE = re.compile(r"\$t\(([^)]*)\)")
PRINTF_RE = re.compile(
    r"%(?:(\d+)\$|\(([A-Za-z_][A-Za-z0-9_]*)\))?[-+0#]*(?:\d+|\*)?(?:\.\d+)?(?:hh|h|ll|l|L|z|j|t)?"
    r"([sdifuxXoeEgGcpb@])"
)
BROKEN_PRINTF_RE = re.compile(r"%[০-৯]+\$?[sd]?")
TAG_RE = re.compile(r"</?([A-Za-z][A-Za-z0-9-]*|\d+)(?:\s[^<>]*)?/?>")
PLURAL_TYPES = {"plural", "selectordinal"}
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}
# CLDR plural categories for Bengali (cardinal): one (i = 0 or n = 1) and other.
BN_PLURAL_CATEGORIES = {"one", "other"}


# --------------------------------------------------------------------------- ICU parsing
def icu_parse(text: str) -> tuple[set[str], dict[str, set[str]], list[str]]:
    """Return (argument names, {plural/select arg: option keys}, parse errors)."""
    args: set[str] = set()
    options: dict[str, set[str]] = {}
    errors: list[str] = []
    s = I18NEXT_RE.sub("", text)
    n = len(s)

    def skip_ws(i: int) -> int:
        while i < n and s[i].isspace():
            i += 1
        return i

    def read_ident(i: int) -> tuple[str, int]:
        j = i
        while j < n and s[j] not in ",{}" and not s[j].isspace():
            j += 1
        return s[i:j], j

    def parse_message(i: int, depth: int) -> int:
        """Parse until the closing brace of this level (or end at depth 0)."""
        while i < n:
            c = s[i]
            if c == "'":
                if i + 1 < n and s[i + 1] == "'":
                    i += 2
                    continue
                if i + 1 < n and s[i + 1] in "{}#|":
                    end = s.find("'", i + 1)
                    i = n if end == -1 else end + 1
                    continue
                i += 1
            elif c == "{":
                i = parse_argument(i + 1, depth + 1)
            elif c == "}":
                if depth == 0:
                    errors.append("unbalanced '}'")
                    i += 1
                    continue
                return i + 1
            else:
                i += 1
        if depth > 0:
            errors.append("unclosed '{'")
        return i

    def parse_argument(i: int, depth: int) -> int:
        i = skip_ws(i)
        name, i = read_ident(i)
        i = skip_ws(i)
        if not name:
            errors.append("empty placeholder '{}'")
        else:
            args.add(name)
        if i < n and s[i] == "}":
            return i + 1
        if i < n and s[i] == ",":
            i = skip_ws(i + 1)
            kind, i = read_ident(i)
            i = skip_ws(i)
            if i < n and s[i] == "}":
                return i + 1  # {n, number}
            if i < n and s[i] == ",":
                i += 1
                if kind in PLURAL_TYPES or kind == "select":
                    keys = options.setdefault(f"{name}:{kind}", set())
                    while True:
                        i = skip_ws(i)
                        if i >= n:
                            errors.append(f"unclosed {kind} for '{name}'")
                            return i
                        if s[i] == "}":
                            return i + 1
                        key, i = read_ident(i)
                        i = skip_ws(i)
                        if key.startswith("offset:"):
                            continue
                        if i < n and s[i] == "{":
                            keys.add(key)
                            i = parse_message(i + 1, depth)
                        else:
                            errors.append(f"option '{key}' of '{name}' has no {{message}}")
                            return i
                # {d, date, short}: skip to closing brace
                close = s.find("}", i)
                return n if close == -1 else close + 1
        errors.append(f"malformed placeholder near '{s[max(0, i - 10) : i + 10]}'")
        close = s.find("}", i)
        return n if close == -1 else close + 1

    parse_message(0, 0)
    return args, options, errors


# --------------------------------------------------------------------------- extraction
def placeholders(text: str, extra: re.Pattern[str] | None = None) -> dict:
    icu_args, icu_opts, icu_errors = icu_parse(text)
    printf = []
    for m in PRINTF_RE.finditer(text.replace("%%", "")):
        printf.append(
            f"%{m.group(1) + '$' if m.group(1) else ''}"
            f"{'(' + m.group(2) + ')' if m.group(2) else ''}{m.group(3)}"
        )
    return {
        "icu": sorted(icu_args),
        "plural": {k: sorted(v) for k, v in icu_opts.items()},
        "i18next": sorted(Counter(x.split(",")[0].strip() for x in I18NEXT_RE.findall(text)).elements()),
        "nesting": sorted(I18NEXT_NEST_RE.findall(text)),
        "printf": sorted(printf),
        "tags": sorted(
            Counter(
                m.group(0).startswith("</") and "/" + m.group(1) or m.group(1) for m in TAG_RE.finditer(text)
            ).elements()
        ),
        "extra": sorted(extra.findall(text)) if extra else [],
        "errors": icu_errors,
    }


# --------------------------------------------------------------------------- loaders
def flatten_json(data, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(k, str) and k.startswith("@"):
                continue  # ARB metadata
            key = f"{prefix}.{k}" if prefix else str(k)
            out.update(flatten_json(v, key))
    elif isinstance(data, list):
        for i, v in enumerate(data):
            out.update(flatten_json(v, f"{prefix}[{i}]"))
    elif isinstance(data, str):
        out[prefix] = data
    return out


def _po_unescape(s: str) -> str:
    return re.sub(r'\\(["\\ntr])', lambda m: {"n": "\n", "t": "\t", "r": "\r"}.get(m.group(1), m.group(1)), s)


def parse_po(text: str) -> tuple[list[dict], dict[str, str]]:
    """Return (entries, header fields). Entry: key, msgid, msgid_plural, msgstr list, fuzzy, line."""
    entries: list[dict] = []
    cur: dict = {}
    field = None
    lineno = 0

    def flush():
        nonlocal cur
        if "msgid" in cur and not cur.get("obsolete"):
            entries.append(cur)
        cur = {}

    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip()
        if not line:
            flush()
            field = None
            continue
        if line.startswith("#~"):
            cur["obsolete"] = True
            continue
        if line.startswith("#,"):
            if "msgid" in cur:
                flush()
            cur["fuzzy"] = "fuzzy" in line
            continue
        if line.startswith("#"):
            if "msgid" in cur and field and field.startswith("msgstr"):
                flush()
            continue
        m = re.match(r'^(msgctxt|msgid_plural|msgid|msgstr(?:\[(\d+)\])?)\s+"(.*)"$', line)
        if m:
            kw = m.group(1)
            if kw in ("msgctxt", "msgid") and "msgid" in cur and field and field.startswith("msgstr"):
                flush()
            cur.setdefault("line", lineno)
            value = _po_unescape(m.group(3))
            if kw.startswith("msgstr"):
                idx = int(m.group(2)) if m.group(2) else 0
                cur.setdefault("msgstr", {})[idx] = value
                field = f"msgstr[{idx}]"
            else:
                cur[kw] = value
                field = kw
            continue
        if line.startswith('"') and line.endswith('"') and field:
            value = _po_unescape(line[1:-1])
            if field.startswith("msgstr["):
                idx = int(field[7:-1])
                cur["msgstr"][idx] += value
            else:
                cur[field] += value
            continue
        raise ValueError(f"line {lineno}: cannot parse {raw!r}")
    flush()
    header: dict[str, str] = {}
    out = []
    for e in entries:
        e["msgstr"] = [
            e.get("msgstr", {}).get(i, "") for i in range(max(e.get("msgstr", {0: ""}).keys()) + 1)
        ]
        e["key"] = (e["msgctxt"] + "\x04" if "msgctxt" in e else "") + e["msgid"]
        if e["msgid"] == "" and "msgctxt" not in e:
            for hline in e["msgstr"][0].splitlines():
                if ":" in hline:
                    k, v = hline.split(":", 1)
                    header[k.strip()] = v.strip()
            continue
        out.append(e)
    return out, header


def load(path: Path):
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() in (".po", ".pot"):
        return "po", parse_po(text)
    if path.suffix.lower() in (".json", ".arb"):
        return "json", flatten_json(json.loads(text))
    raise ValueError(f"{path}: unsupported file type (use .json, .arb, .po or .pot)")


# --------------------------------------------------------------------------- comparison
def finding(severity: str, key: str, check: str, message: str) -> dict:
    return {"severity": severity, "key": key.replace("\x04", " | "), "check": check, "message": message}


def compare_strings(key: str, en: str, bn: str, extra=None, plural_alt: str | None = None) -> list[dict]:
    """Compare one English source with its Bangla translation.

    plural_alt: for gettext msgstr[0], the msgid_plural; Bangla may drop or add the
    number placeholder relative to the English singular.
    """
    out: list[dict] = []
    if bn.strip() == "":
        return [finding("warning", key, "empty", "Bangla value is empty")]
    pe, pb = placeholders(en, extra), placeholders(bn, extra)
    for err in pb["errors"]:
        out.append(finding("error", key, "syntax", f"Bangla ICU syntax: {err}"))
    for kind in ("icu", "i18next", "nesting", "printf", "extra"):
        a, b = Counter(pe[kind]), Counter(pb[kind])
        if kind in ("icu", "extra"):
            a, b = Counter(set(pe[kind])), Counter(set(pb[kind]))
        missing, added = a - b, b - a
        if plural_alt is not None:
            alt = Counter(placeholders(plural_alt, extra)[kind])
            added = Counter({k: v for k, v in added.items() if k not in alt})
            missing = Counter({k: v for k, v in missing.items() if k not in ("%d", "%s", "%1$d", "%1$s")})
        for ph in sorted(missing.elements()):
            out.append(finding("error", key, "placeholder", f"missing {kind} placeholder {ph!r}"))
        for ph in sorted(added.elements()):
            msg = f"unexpected {kind} placeholder {ph!r}"
            if BENGALI_RE.search(ph):
                msg += " (placeholder names must stay in English, do not translate them)"
            out.append(finding("error", key, "placeholder", msg))
    if BROKEN_PRINTF_RE.search(bn):
        out.append(finding("error", key, "placeholder", "printf placeholder uses Bangla digits (e.g. %১$s)"))
    for arg_kind, keys in pe["plural"].items():
        name, kind = arg_kind.split(":")
        bkeys = set(pb["plural"].get(arg_kind, []))
        if arg_kind not in pb["plural"]:
            out.append(finding("error", key, "icu", f"{kind} block for '{name}' is missing in Bangla"))
        elif "other" not in bkeys:
            out.append(finding("error", key, "icu", f"{kind} '{name}' has no 'other' branch"))
        elif kind == "plural":
            unknown = {k for k in bkeys if not k.startswith("=")} - BN_PLURAL_CATEGORIES
            if unknown:
                out.append(
                    finding(
                        "warning",
                        key,
                        "icu",
                        f"plural categories {sorted(unknown)} never match in Bangla (only one/other)",
                    )
                )
        elif kind == "select":
            lost = set(keys) - bkeys
            if lost:
                out.append(
                    finding(
                        "warning",
                        key,
                        "icu",
                        f"select '{name}' drops {sorted(lost)}; those values fall back to 'other'",
                    )
                )
    if Counter(pe["tags"]) != Counter(pb["tags"]):
        out.append(finding("error", key, "tags", f"HTML/JSX tags differ: en {pe['tags']} vs bn {pb['tags']}"))
    if en.count("\n") != bn.count("\n"):
        out.append(finding("info", key, "newlines", "number of line breaks differs"))
    if bn == en and LATIN_WORD_RE.search(en) and not BENGALI_RE.search(bn):
        out.append(finding("warning", key, "untranslated", "Bangla value is identical to English"))
    if (
        en.rstrip().endswith(".")
        and bn.rstrip().endswith(".")
        and BENGALI_RE.search(bn)
        and not en.endswith("...")
    ):
        out.append(finding("info", key, "punctuation", "Bangla sentence ends with '.'; use the danda '।'"))
    if bn.rstrip().endswith("|"):
        out.append(finding("warning", key, "punctuation", "ASCII '|' used as danda; use '।' (U+0964)"))
    return out


def check_json(en: dict[str, str], bn: dict[str, str], extra=None) -> list[dict]:
    out: list[dict] = []
    for key in en:
        if key not in bn:
            out.append(finding("warning", key, "missing", "key missing in Bangla file"))
    for key in bn:
        if key not in en:
            out.append(finding("warning", key, "stale", "key exists only in Bangla file"))
    for key, en_val in en.items():
        if key in bn:
            out += compare_strings(key, en_val, bn[key], extra)
    return out


def check_po(
    entries: list[dict], header: dict[str, str], template: list[dict] | None, extra=None
) -> list[dict]:
    out: list[dict] = []
    nplurals = None
    pf = header.get("Plural-Forms", "")
    m = re.search(r"nplurals\s*=\s*(\d+)", pf)
    if m:
        nplurals = int(m.group(1))
        if nplurals != 2:
            out.append(
                finding(
                    "warning",
                    "(header)",
                    "plural-forms",
                    f"Plural-Forms has nplurals={nplurals}; Bangla uses 'nplurals=2; plural=(n != 1);'",
                )
            )
    elif any(e.get("msgid_plural") for e in entries):
        out.append(finding("warning", "(header)", "plural-forms", "no Plural-Forms header"))
    lang = header.get("Language", "")
    if lang and not lang.lower().startswith("bn"):
        out.append(
            finding("warning", "(header)", "language", f"Language header is '{lang}', expected bn or bn_BD")
        )
    if template is not None:
        have = {e["key"] for e in entries}
        tkeys = {e["key"] for e in template}
        for k in sorted(tkeys - have):
            out.append(finding("warning", k, "missing", "entry in template but not in Bangla PO"))
        for k in sorted(have - tkeys):
            out.append(finding("info", k, "stale", "entry not in template (run msgmerge)"))
    for e in entries:
        key = e["key"]
        if e.get("fuzzy"):
            out.append(finding("warning", key, "fuzzy", "entry is marked fuzzy and will not be used"))
        strs = e["msgstr"]
        if all(s == "" for s in strs):
            out.append(finding("warning", key, "untranslated", "no translation"))
            continue
        if e.get("msgid_plural"):
            if nplurals and len(strs) != nplurals:
                out.append(
                    finding("error", key, "plural-forms", f"has {len(strs)} msgstr[] but nplurals={nplurals}")
                )
            for i, s in enumerate(strs):
                src = e["msgid"] if i == 0 else e["msgid_plural"]
                alt = e["msgid_plural"] if i == 0 else None
                out += compare_strings(key + f" [msgstr[{i}]]", src, s, extra, plural_alt=alt)
        else:
            out += compare_strings(key, e["msgid"], strs[0], extra)
    return out


def run(paths: list[Path], extra=None) -> list[dict]:
    loaded = [load(p) for p in paths]
    if len(paths) == 1:
        kind, data = loaded[0]
        if kind != "po":
            raise ValueError("a single file must be a .po; for JSON pass en.json bn.json")
        return check_po(*data, None, extra)
    (k1, d1), (k2, d2) = loaded
    if k1 == "json" and k2 == "json":
        return check_json(d1, d2, extra)
    if k1 == "po" and k2 == "po":
        return check_po(d2[0], d2[1], d1[0], extra)
    raise ValueError("compare two JSON files, or a .pot/.po template with a .po translation")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Check placeholder/ICU/tag/key parity between English and Bangla translation files.",
        epilog="Examples: check_placeholders.py locales/en.json locales/bn.json | "
        "check_placeholders.py languages/bn_BD.po | check_placeholders.py app.pot bn_BD.po --json",
    )
    p.add_argument("files", nargs="+", type=Path, help="en.json bn.json | bn.po | template.pot bn.po")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument(
        "--fail-on",
        choices=["error", "warning", "info"],
        default="error",
        help="lowest severity that makes the exit code 1 (default: error)",
    )
    p.add_argument(
        "--extra-pattern",
        metavar="REGEX",
        help=r"extra placeholder syntax to compare, e.g. ':[a-z_]+' for Laravel",
    )
    p.add_argument("--quiet", action="store_true", help="hide info findings in text output")
    args = p.parse_args(argv)
    if len(args.files) > 2:
        p.error("pass one .po file or two files")
    try:
        extra = re.compile(args.extra_pattern) if args.extra_pattern else None
        findings = run(args.files, extra)
    except (OSError, ValueError, re.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    counts = Counter(f["severity"] for f in findings)
    if args.json:
        print(
            json.dumps(
                {"files": [str(f) for f in args.files], "counts": dict(counts), "findings": findings},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for f in findings:
            if args.quiet and f["severity"] == "info":
                continue
            print(f"{f['severity'].upper():7} {f['check']:13} {f['key']}: {f['message']}")
        print(f"\n{counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info")
    threshold = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[f["severity"]] >= threshold for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
