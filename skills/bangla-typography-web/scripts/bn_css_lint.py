#!/usr/bin/env python3
"""Lint CSS and HTML for Bangla (Bengali script) typography problems. Read-only.

Checks:
  * font-family stacks on text selectors without any Bengali-capable font
  * @font-face for Bengali fonts without font-display (invisible text on slow networks)
  * Bengali @font-face without unicode-range (cannot split Latin and Bengali files)
  * Google Fonts links/imports without display=swap
  * line-height below 1.5 on body text (clips vowel signs above/below the letters and reph)
  * letter-spacing on text (breaks the matra/headstroke and conjunct shaping)
  * word-break: break-all, text-align: justify, small body font-size
  * font-style: italic for Bangla (no true italics; browsers fake a slant)
  * faux bold: bold weights used with a Bengali family declared in only one weight
  * HTML: missing lang="bn", missing meta charset

Exit codes: 0 = no findings at or above --fail-on, 1 = findings, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BENGALI_FONTS = {
    "noto sans bengali",
    "noto serif bengali",
    "noto sans bengali ui",
    "hind siliguri",
    "baloo da 2",
    "baloo da",
    "tiro bangla",
    "anek bangla",
    "galada",
    "atma",
    "mina",
    "solaimanlipi",
    "kalpurush",
    "siyam rupali",
    "nikosh",
    "nikoshban",
    "bangla mn",
    "bangla sangam mn",
    "kohinoor bangla",
    "vrinda",
    "shonar bangla",
    "nirmala ui",
    "lohit bengali",
    "mukti",
    "mukti narrow",
    "li ador noirrit",
    "adorsho lipi",
    "ekushey lohit",
    "akaash",
    "bensen",
    "noto sans bangla",
    "shurjo",
    "mitra",
    "bornomala",
    "hind siliguri light",
    "anek bangla condensed",
    "sutonnymj",
}
LEGACY_FONTS = {"sutonnymj", "sutonnyomj", "sutonny", "bijoy"}
TEXT_SELECTOR_RE = re.compile(
    r"(^|[\s,>+~])(html|body|:root|p|li|h[1-6]|article|main|section|blockquote|td|th|label|button|input"
    r"|textarea|\.content|\.entry-content|\.prose|:lang\(bn[^)]*\)|\[lang\^?=['\"]?bn)",
    re.I,
)
BODY_SELECTOR_RE = re.compile(
    r"(^|[\s,])(html|body|:root|p|:lang\(bn[^)]*\)|\.entry-content|\.prose)\b", re.I
)
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}


def finding(sev, file, line, check, message, fix):
    return {"severity": sev, "file": str(file), "line": line, "check": check, "message": message, "fix": fix}


def strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), css, flags=re.S)


def parse_css(css: str, base_line: int = 1) -> list[dict]:
    """Return a flat list of rules: {selector, decls: [(prop, value, line)], line, at}."""
    css = strip_comments(css)
    rules: list[dict] = []
    stack: list[str] = []
    buf_start = 0
    i = 0
    n = len(css)
    while i < n:
        c = css[i]
        if c == "{":
            prelude = css[buf_start:i].strip()
            line = base_line + css.count(
                "\n", 0, buf_start + (len(css[buf_start:i]) - len(css[buf_start:i].lstrip()))
            )
            # find matching close or nested open
            j = i + 1
            depth = 1
            nested = False
            while j < n and depth:
                if css[j] == "{":
                    depth += 1
                    nested = True
                elif css[j] == "}":
                    depth -= 1
                j += 1
            if nested and not prelude.lower().startswith("@font-face"):
                stack.append(prelude)
                i += 1
                buf_start = i
                continue
            body = css[i + 1 : j - 1]
            decls = []
            offset = i + 1
            for m in re.finditer(r"([A-Za-z-]+)\s*:\s*([^;]+)", body):
                decls.append(
                    (
                        m.group(1).lower(),
                        m.group(2).strip(),
                        base_line + css.count("\n", 0, offset + m.start()),
                    )
                )
            rules.append({"selector": prelude, "decls": decls, "line": line, "at": list(stack)})
            i = j
            buf_start = i
            continue
        if c == "}":
            if stack:
                stack.pop()
            buf_start = i + 1
        elif c == ";":
            # top-level statements such as @import
            stmt = css[buf_start:i].strip()
            if stmt.startswith("@import"):
                rules.append(
                    {
                        "selector": "@import",
                        "decls": [("import", stmt, base_line + css.count("\n", 0, i))],
                        "line": base_line + css.count("\n", 0, i),
                        "at": list(stack),
                    }
                )
            buf_start = i + 1
        i += 1
    return rules


def families(value: str) -> list[str]:
    return [f.strip().strip("'\"").lower() for f in value.split(",") if f.strip()]


def is_bengali_family(name: str, declared_bn: set[str]) -> bool:
    return name in BENGALI_FONTS or name in declared_bn or "bengali" in name or "bangla" in name


def lint_rules(rules: list[dict], file: Path) -> list[dict]:
    out: list[dict] = []
    declared_bn: set[str] = set()
    face_weights: dict[str, set[str]] = {}
    # pass 1: @font-face
    for r in rules:
        if not r["selector"].lower().startswith("@font-face"):
            continue
        d = {p: (v, ln) for p, v, ln in r["decls"]}
        fam = families(d.get("font-family", ("", 0))[0])
        fam = fam[0] if fam else ""
        urange = d.get("unicode-range", ("", 0))[0].upper()
        is_bn = is_bengali_family(fam, set()) or bool(re.search(r"U\+0?98|U\+09[0-9A-F]", urange))
        if not is_bn:
            continue
        declared_bn.add(fam)
        face_weights.setdefault(fam, set()).add(d.get("font-weight", ("400", 0))[0])
        if fam in LEGACY_FONTS or "mj" in fam.split()[-1:]:
            out.append(
                finding(
                    "error",
                    file,
                    r["line"],
                    "legacy-font",
                    f"@font-face '{fam}' looks like a Bijoy/ANSI font; it does not render Unicode Bangla",
                    "use a Unicode font (Noto Sans Bengali, Hind Siliguri, SolaimanLipi); convert the text",
                )
            )
        if "font-display" not in d:
            out.append(
                finding(
                    "warning",
                    file,
                    r["line"],
                    "font-display",
                    f"@font-face '{fam}' has no font-display; Bangla text is invisible until the font loads",
                    "add font-display: swap; (or optional for body text on slow networks)",
                )
            )
        elif d["font-display"][0].lower() == "block":
            out.append(
                finding(
                    "info",
                    file,
                    r["line"],
                    "font-display",
                    f"@font-face '{fam}' uses font-display: block",
                    "prefer swap or optional",
                )
            )
        if not urange:
            out.append(
                finding(
                    "info",
                    file,
                    r["line"],
                    "unicode-range",
                    f"@font-face '{fam}' has no unicode-range",
                    "add unicode-range: U+0980-09FE, U+200C-200D, U+25CC, U+0964-0965; so Latin text "
                    "does not download the Bengali file",
                )
            )
    # pass 2: rules
    bold_used: list[tuple[str, int]] = []
    for r in rules:
        sel = r["selector"]
        if sel.lower().startswith("@font-face"):
            continue
        if sel == "@import":
            value = r["decls"][0][1]
            if "fonts.googleapis.com" in value and "display=" not in value:
                out.append(
                    finding(
                        "warning",
                        file,
                        r["line"],
                        "google-fonts",
                        "Google Fonts @import without display=swap",
                        "append &display=swap, and prefer <link rel=preconnect> + <link> over @import",
                    )
                )
            continue
        is_text = bool(TEXT_SELECTOR_RE.search(sel))
        is_body = bool(BODY_SELECTOR_RE.search(sel))
        lang_en = ":lang(en" in sel.lower()
        props = {p: (v, ln) for p, v, ln in r["decls"]}
        if "font" in props and "font-family" not in props:
            m = re.search(r"(?:\d[\w.%]*\s*(?:/\s*[\w.%]+)?\s+)(.+)$", props["font"][0])
            if m:
                props["font-family"] = (m.group(1), props["font"][1])
            lh = re.search(r"/\s*([\d.]+%?)", props["font"][0])
            if lh and "line-height" not in props:
                props["line-height"] = (lh.group(1), props["font"][1])
        if "font-family" in props and is_text and not lang_en:
            fams = families(props["font-family"][0])
            if (
                fams
                and not any(f.startswith("var(") for f in fams)
                and not any(is_bengali_family(f, declared_bn) for f in fams)
            ):
                out.append(
                    finding(
                        "warning",
                        file,
                        props["font-family"][1],
                        "font-stack",
                        f"'{sel}' font-family has no Bengali font: {props['font-family'][0]}",
                        "add a Bengali family before the generic fallback, e.g. "
                        "'Inter', 'Hind Siliguri', 'Noto Sans Bengali', sans-serif",
                    )
                )
        if "font-family" in props and any(f in LEGACY_FONTS for f in families(props["font-family"][0])):
            out.append(
                finding(
                    "error",
                    file,
                    props["font-family"][1],
                    "legacy-font",
                    f"'{sel}' uses a Bijoy/ANSI font ({props['font-family'][0]})",
                    "use a Unicode Bengali font and convert legacy text to Unicode",
                )
            )
        if "line-height" in props and is_body and not lang_en:
            v, ln = props["line-height"]
            num = None
            m = re.fullmatch(r"([\d.]+)(%?)", v.strip())
            if m:
                num = float(m.group(1)) / (100 if m.group(2) else 1)
            if num is not None and num < 1.5:
                out.append(
                    finding(
                        "warning",
                        file,
                        ln,
                        "line-height",
                        f"'{sel}' line-height {v} is tight for Bangla",
                        "use 1.6-1.8 for Bangla body text (vowel signs and reph need vertical room)",
                    )
                )
        if "letter-spacing" in props and is_text and not lang_en:
            v, ln = props["letter-spacing"]
            if v.strip().lower() not in ("0", "normal", "0px", "0em", "0rem", "inherit", "initial", "unset"):
                out.append(
                    finding(
                        "warning",
                        file,
                        ln,
                        "letter-spacing",
                        f"'{sel}' letter-spacing: {v} breaks the Bangla headstroke and conjuncts",
                        "reset it for Bangla: :lang(bn) "
                        + sel.split(",")[0].strip()
                        + " { letter-spacing: normal; }",
                    )
                )
        if props.get("word-break", ("", 0))[0].lower() == "break-all":
            out.append(
                finding(
                    "warning",
                    file,
                    props["word-break"][1],
                    "word-break",
                    f"'{sel}' word-break: break-all splits Bangla words mid-word",
                    "use overflow-wrap: anywhere; for long URLs instead",
                )
            )
        if props.get("text-align", ("", 0))[0].lower() == "justify" and is_text:
            out.append(
                finding(
                    "info",
                    file,
                    props["text-align"][1],
                    "justify",
                    f"'{sel}' text-align: justify creates uneven gaps in Bangla (no hyphenation)",
                    "prefer text-align: start for Bangla body text",
                )
            )
        if "font-size" in props and re.search(r"(^|[\s,])(html|body)\b", sel, re.I):
            m = re.fullmatch(r"([\d.]+)px", props["font-size"][0].strip())
            if m and float(m.group(1)) < 15:
                out.append(
                    finding(
                        "info",
                        file,
                        props["font-size"][1],
                        "font-size",
                        f"'{sel}' font-size {props['font-size'][0]} is small for Bangla",
                        "Bangla glyphs look smaller than Latin at the same size; use 16px+ (or size-adjust)",
                    )
                )
        if props.get("font-style", ("", 0))[0].lower() in ("italic", "oblique") and ":lang(bn" in sel.lower():
            out.append(
                finding(
                    "info",
                    file,
                    props["font-style"][1],
                    "italic",
                    f"'{sel}' italicises Bangla; Bengali fonts have no italics, so browsers fake a slant",
                    ":lang(bn) em { font-style: normal; font-weight: 600; }",
                )
            )
        w = props.get("font-weight", ("", 0))[0].lower()
        if w in ("bold", "bolder", "600", "700", "800", "900"):
            bold_used.append((sel, props["font-weight"][1]))
    for fam, weights in face_weights.items():
        if bold_used and weights <= {"400", "normal"}:
            sel, ln = bold_used[0]
            out.append(
                finding(
                    "info",
                    file,
                    ln,
                    "faux-bold",
                    f"bold text is used but '{fam}' is declared only in weight 400",
                    f"load a bold face of '{fam}' (e.g. 600/700) to avoid synthesized bold",
                )
            )
    return out


def lint_html(text: str, file: Path) -> list[dict]:
    out: list[dict] = []
    m = re.search(r"<html\b([^>]*)>", text, re.I)
    has_bn_text = bool(re.search(r"[\u0980-\u09ff]", text))
    if m:
        lang = re.search(r"\blang\s*=\s*['\"]?([A-Za-z-]+)", m.group(1))
        line = text.count("\n", 0, m.start()) + 1
        if not lang:
            out.append(
                finding(
                    "warning",
                    file,
                    line,
                    "lang",
                    "<html> has no lang attribute",
                    'use <html lang="bn"> (or lang="bn-BD") for Bangla pages',
                )
            )
        elif has_bn_text and not lang.group(1).lower().startswith("bn"):
            if not re.search(r"\blang\s*=\s*['\"]?bn", text, re.I):
                out.append(
                    finding(
                        "warning",
                        file,
                        line,
                        "lang",
                        f'page contains Bangla text but lang="{lang.group(1)}" and no element has lang="bn"',
                        'mark Bangla passages with lang="bn" for fonts, :lang(bn) rules and screen readers',
                    )
                )
    if not re.search(r"<meta[^>]+charset\s*=\s*['\"]?utf-8", text, re.I) and re.search(
        r"<head\b", text, re.I
    ):
        out.append(
            finding(
                "warning",
                file,
                1,
                "charset",
                'no <meta charset="utf-8">',
                'add <meta charset="utf-8"> as the first element in <head>',
            )
        )
    for lm in re.finditer(
        r"<link\b[^>]*href\s*=\s*['\"]([^'\"]*fonts\.googleapis\.com[^'\"]*)['\"][^>]*>", text, re.I
    ):
        if "display=" not in lm.group(1):
            out.append(
                finding(
                    "warning",
                    file,
                    text.count("\n", 0, lm.start()) + 1,
                    "google-fonts",
                    "Google Fonts link without display=swap",
                    "append &display=swap to the URL",
                )
            )
    for sm in re.finditer(r"<style\b[^>]*>(.*?)</style>", text, re.I | re.S):
        out += lint_rules(parse_css(sm.group(1), text.count("\n", 0, sm.start(1)) + 1), file)
    return out


def lint_path(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".html", ".htm", ".php", ".vue", ".svelte"):
        return lint_html(text, path)
    return lint_rules(parse_css(text), path)


def iter_files(paths: list[Path]):
    exts = {".css", ".scss", ".html", ".htm", ".php", ".vue", ".svelte"}
    for p in paths:
        if p.is_dir():
            for f in sorted(p.rglob("*")):
                if (
                    f.suffix.lower() in exts
                    and not any(part in ("node_modules", "vendor", ".git", "dist") for part in f.parts)
                    and not f.name.endswith(".min.css")
                ):
                    yield f
        else:
            yield p


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Lint CSS/HTML for Bangla typography problems (fonts, line-height, spacing, loading).",
        epilog="Examples: bn_css_lint.py assets/css/ | bn_css_lint.py index.html style.css --json",
    )
    p.add_argument("paths", nargs="+", type=Path, help="CSS/SCSS/HTML/PHP/Vue files or directories")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument("--fail-on", choices=["info", "warning", "error"], default="warning")
    args = p.parse_args(argv)
    findings: list[dict] = []
    for f in iter_files(args.paths):
        try:
            findings += lint_path(f)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: {f}: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            print(
                f"{f['file']}:{f['line']} {f['severity'].upper()} {f['check']}: {f['message']}\n"
                f"    fix: {f['fix']}"
            )
        print(f"\n{len(findings)} finding(s)")
    floor = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[f["severity"]] >= floor for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
