#!/usr/bin/env python3
"""Find hard-coded user-facing strings in JS/TS/JSX/TSX/Vue/Svelte, PHP and Python source.

Read-only: scans files and prints findings with a suggested translation key. With
--emit-catalog FILE it also writes a JSON catalog skeleton {key: English text} (it refuses
to overwrite an existing file unless --force is given).

Heuristics (not a parser for JS/PHP; Python uses the ast module):
  * JSX/HTML text nodes and user-facing attributes (placeholder, title, alt, aria-label, label)
  * alert()/confirm()/toast()/echo/print with literal text
  * string literals that read like prose (several words, or a capitalised word)
  * any hard-coded Bangla text (Bengali script) outside translation files
  * strings already inside t(), $t(), i18n.t(), __(), _e(), esc_html__(), gettext(), _() ... are skipped
  * --text-domain checks WordPress __()/_e()/esc_html__() calls for a missing or wrong text domain

Exit codes: 0 = nothing at or above --min-confidence, 1 = findings, 2 = error.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte"}
PHP_EXT = {".php"}
PY_EXT = {".py"}
SKIP_DIRS = {
    "node_modules",
    "vendor",
    ".git",
    "dist",
    "build",
    ".next",
    ".nuxt",
    "out",
    "coverage",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".tox",
    "locales",
    "locale",
    "lang",
    "languages",
    "i18n",
    "migrations",
    "storybook-static",
}
CONFIDENCE = {"low": 0, "medium": 1, "high": 2}
BENGALI_RE = re.compile(r"[\u0980-\u09ff]")
WORD_RE = re.compile(r"[A-Za-z]{2,}")
JS_TRANSLATE_BEFORE = re.compile(
    r"(?:\bt|\$t|\bi18n\.t|\bi18next\.t|\btc|\$tc|\bformatMessage|\bintl\.formatMessage|\b__|\b_x|\b_n"
    r"|\bsprintf\(\s*__|\btranslate|\bgettext|\bngettext|\bpgettext|\bmsg|\bdefineMessage|\buseTranslations\(\)?)"
    r"\s*\(\s*(?:\{[^}]*)?$"
)
PHP_TRANSLATE_BEFORE = re.compile(
    r"(?:\b__|\b_e|\b_x|\b_ex|\b_n|\b_nx|\b_n_noop|\besc_html__|\besc_html_e|\besc_attr__|\besc_attr_e"
    r"|\besc_html_x|\besc_attr_x|\btranslate|\bgettext|\bngettext|\btrans|\btrans_choice|\b@lang|\bLang::get"
    r"|\b__t)\s*\(\s*(?:[^()]*,\s*)?$"
)
PHP_DOMAIN_CALL = re.compile(
    r"\b(__|_e|esc_html__|esc_html_e|esc_attr__|esc_attr_e)\s*\(\s*(['\"])((?:\\.|(?!\2).)*)\2"
    r"\s*(?:,\s*(['\"])((?:\\.|(?!\4).)*)\4)?\s*\)"
)
NON_UI_BEFORE = re.compile(
    r"(?:console\.\w+|require|import|from|logger\.\w+|log\.\w+|debug|className|class|data-[\w-]+|key|type"
    r"|href|src|id|name|rel|target|method|role|htmlFor|style|testid|data-testid|addEventListener"
    r"|querySelector(?:All)?|getElementById|getAttribute|setAttribute|fetch|axios\.\w+|define"
    r"|add_action|add_filter|do_action|apply_filters|wp_enqueue_\w+|wp_register_\w+|get_option|update_option"
    r"|register_\w+|header|setcookie|error_log|preg_\w+|str_replace|in_array|array_key_exists|isset"
    r"|sanitize_\w+|wp_verify_nonce|wp_nonce_field|current_user_can)\s*(?:=\s*\{?|\(|:)\s*$"
)
UI_CALL_BEFORE = re.compile(
    r"(?:\balert|\bconfirm|\bprompt|\btoast(?:\.\w+)?|\bmessage\.\w+|\bnotify|\bnotification\.\w+"
    r"|\bsetError|\bsetMessage|\bthrow new \w*Error)\s*\(\s*$"
)
UI_ATTR_RE = re.compile(
    r"\b(placeholder|title|alt|aria-label|aria-description|label|helperText|tooltip|description"
    r"|emptyText|confirmText|cancelText|okText)\s*=\s*(['\"])([^'\"{}]+)\2"
)
STRING_RE = re.compile(r"(['\"`])((?:\\.|(?!\1).)*)\1")
JSX_TEXT_RE = re.compile(r">([^<>{}]*[A-Za-z\u0980-\u09ff][^<>{}]*)<")
PHP_ECHO_RE = re.compile(r"\b(?:echo|print)\s+(['\"])((?:\\.|(?!\1).)+)\1")
URLISH = re.compile(
    r"^(?:[a-z]+:|//|www\.|/|\./|\.\./|#|@|\$|\{\{|<)|\.(?:js|ts|css|png|jpe?g|svg|webp|php|json|html?)$"
)
CODEISH = re.compile(r"^[a-z0-9_.:/\-\[\]\s*#>~+=,()%]+$")
SQL = re.compile(r"^\s*(select|insert|update|delete|create|alter|drop|with)\b", re.I)


def looks_user_facing(text: str) -> str | None:
    """Return a confidence level if text reads like UI copy, else None."""
    s = re.sub(r"\$\{[^}]*\}|\{\{[^}]*\}\}|\{[A-Za-z0-9_]+\}|%\d*\$?[sd]", " ", text).strip()
    if len(s) < 2:
        return None
    if BENGALI_RE.search(s):
        return "high"
    if not WORD_RE.search(s) or URLISH.search(s) or SQL.match(s) or "@" in s and " " not in s:
        return None
    if CODEISH.match(s) and not re.search(r"[a-z]{2,} [a-z]{2,} [a-z]{2,}", s):
        return None  # css classes, ids, paths, mime types, short lowercase tokens
    if re.fullmatch(r"[A-Z0-9_\-]+", s):
        return None  # CONSTANTS, HTTP verbs
    words = [w for w in re.split(r"\s+", s) if WORD_RE.search(w)]
    if len(words) >= 2:
        return "medium"
    if re.fullmatch(r"[A-Z][a-z]+[.!?:]?", s):
        return "low"
    return None


def suggest_key(text: str, namespace: str, line: int) -> str:
    words = re.findall(r"[A-Za-z0-9]+", re.sub(r"\$\{[^}]*\}|\{[^}]*\}", " ", text).lower())[:5]
    slug = "_".join(words) or f"text_{line}"
    return f"{namespace}.{slug}" if namespace else slug


def namespace_for(path: Path) -> str:
    stem = path.stem.split(".")[0]
    if stem.lower() in ("index", "page", "layout", "__init__", "functions", "main", "app"):
        stem = path.parent.name or stem
    return re.sub(r"[^a-z0-9]+", "_", re.sub(r"(?<!^)(?=[A-Z])", "_", stem).lower()).strip("_")


def blank_comments(src: str, php: bool = False) -> str:
    """Replace block and line comments with spaces, keeping line numbers."""

    def keep_lines(m: re.Match) -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    src = re.sub(r"/\*.*?\*/", keep_lines, src, flags=re.S)
    src = re.sub(r"<!--.*?-->", keep_lines, src, flags=re.S)
    pattern = r"(^|[ \t;])(//|#(?!\[))[^\n]*" if php else r"(^|[ \t;])//[^\n]*"
    return re.sub(pattern, lambda m: m.group(1) + " " * (len(m.group(0)) - len(m.group(1))), src, flags=re.M)


def line_col(src: str, offset: int) -> tuple[int, int]:
    line = src.count("\n", 0, offset) + 1
    return line, offset - (src.rfind("\n", 0, offset) + 1) + 1


def add(findings, path, line, col, conf, kind, text, ns):
    text = " ".join(text.split())
    findings.append(
        {
            "file": str(path),
            "line": line,
            "col": col,
            "confidence": conf,
            "kind": kind,
            "text": text,
            "key": suggest_key(text, ns, line),
        }
    )


def scan_markup_text(src: str, path: Path, ns: str, findings: list, seen: set) -> None:
    for m in JSX_TEXT_RE.finditer(src):
        text = m.group(1)
        if re.search(r";|&&|\|\||=>|==|\breturn\b|\bconst\b|\bif\s*\(", text) or text.strip()[:1] in ")]},.":
            continue
        conf = looks_user_facing(text) or ("low" if re.search(r"[A-Za-z]{3,}", text.strip()) else None)
        if not conf:
            continue
        line, col = line_col(src, m.start(1) + (len(text) - len(text.lstrip())))
        if (line, col) not in seen:
            seen.add((line, col))
            add(findings, path, line, col, "high" if conf != "low" else "medium", "markup-text", text, ns)
    for m in UI_ATTR_RE.finditer(src):
        if looks_user_facing(m.group(3)) or re.fullmatch(r"[A-Z][a-z]+", m.group(3)):
            line, col = line_col(src, m.start(3))
            seen.add((line, col))
            add(findings, path, line, col, "high", f"attribute:{m.group(1)}", m.group(3), ns)


def scan_literals(src: str, path: Path, ns: str, findings: list, seen: set, php: bool) -> None:
    translate_before = PHP_TRANSLATE_BEFORE if php else JS_TRANSLATE_BEFORE
    for m in STRING_RE.finditer(src):
        text = m.group(2)
        line, col = line_col(src, m.start(2))
        if (line, col) in seen or "\n" in text and m.group(1) != "`":
            continue
        line_start = src.rfind("\n", 0, m.start()) + 1
        before = src[line_start : m.start()]
        before_wide = src[max(0, m.start() - 200) : m.start()]
        if translate_before.search(before_wide) or NON_UI_BEFORE.search(before):
            continue
        if re.search(r"(?:defaultMessage|\bid|\bi18nKey|\bmessageId)\s*[:=]\s*\{?\s*$", before):
            continue
        if re.search(r"^\s*(import|export\s+\*|use|namespace|require|include)\b", src[line_start : m.end()]):
            continue
        if (
            re.search(r"\[\s*$", before)
            or re.match(r"\s*(=>|\]|:(?!:))", src[m.end() : m.end() + 3])
            and not php
        ):
            continue  # object keys / index access
        if php and re.match(r"\s*=>", src[m.end() : m.end() + 4]):
            continue  # array keys
        conf = looks_user_facing(text)
        if not conf:
            continue
        kind = "literal"
        if UI_CALL_BEFORE.search(before):
            conf, kind = "high", "ui-call"
        elif php and re.search(r"\b(echo|print)\s*$", before):
            conf, kind = "high", "echo"
        seen.add((line, col))
        add(findings, path, line, col, conf, kind, text, ns)


def scan_js(src: str, path: Path) -> list[dict]:
    findings: list[dict] = []
    seen: set = set()
    ns = namespace_for(path)
    code = blank_comments(src)
    if path.suffix in (".jsx", ".tsx", ".vue", ".svelte") or re.search(r"return\s*\(\s*<|</[A-Za-z]", code):
        scan_markup_text(code, path, ns, findings, seen)
    scan_literals(code, path, ns, findings, seen, php=False)
    return findings


def scan_php(src: str, path: Path, text_domain: str | None) -> list[dict]:
    findings: list[dict] = []
    seen: set = set()
    ns = namespace_for(path)
    # HTML portions: blank out PHP blocks, then scan text nodes and attributes.
    html = re.sub(r"<\?(?:php|=)?.*?(?:\?>|\Z)", lambda m: re.sub(r"[^\n]", " ", m.group(0)), src, flags=re.S)
    scan_markup_text(blank_comments(html), path, ns, findings, seen)
    # PHP portions: blank out HTML, then scan literals.
    parts = []
    pos = 0
    for m in re.finditer(r"<\?(?:php|=)?(.*?)(?:\?>|\Z)", src, flags=re.S):
        parts.append(re.sub(r"[^\n]", " ", src[pos : m.start(1)]))
        parts.append(m.group(1))
        pos = m.end(1)
    parts.append(re.sub(r"[^\n]", " ", src[pos:]))
    php = blank_comments("".join(parts), php=True)
    scan_literals(php, path, ns, findings, seen, php=True)
    if text_domain:
        for m in PHP_DOMAIN_CALL.finditer(php):
            domain = m.group(5)
            if domain != text_domain:
                line, col = line_col(php, m.start())
                msg = "no text domain" if domain is None else f"text domain '{domain}'"
                findings.append(
                    {
                        "file": str(path),
                        "line": line,
                        "col": col,
                        "confidence": "high",
                        "kind": "text-domain",
                        "text": m.group(3),
                        "key": "",
                        "message": f"{m.group(1)}() has {msg}; expected '{text_domain}'",
                    }
                )
    return findings


PY_TRANSLATE = {
    "_",
    "gettext",
    "ngettext",
    "pgettext",
    "npgettext",
    "gettext_lazy",
    "ngettext_lazy",
    "pgettext_lazy",
    "lazy_gettext",
    "lazy_ngettext",
    "_l",
    "N_",
    "ugettext",
    "ugettext_lazy",
}
PY_SKIP_CALLS = {
    "debug",
    "info",
    "warning",
    "warn",
    "error",
    "exception",
    "critical",
    "log",
    "getLogger",
    "getenv",
    "get",
    "setdefault",
    "startswith",
    "endswith",
    "split",
    "join",
    "replace",
    "strftime",
    "strptime",
    "compile",
    "match",
    "search",
    "sub",
    "fullmatch",
    "findall",
    "open",
    "execute",
    "executemany",
    "format_map",
    "encode",
    "decode",
    "Path",
    "import_module",
    "getattr",
    "setattr",
    "hasattr",
    "isinstance",
    "add_argument_group",
    "route",
    "path",
    "re_path",
    "url",
    "environ",
}


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def scan_python(src: str, path: Path, include_logs: bool = False) -> list[dict]:
    findings: list[dict] = []
    ns = namespace_for(path)
    tree = ast.parse(src, filename=str(path))
    parents: dict[ast.AST, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                docstrings.add(first.value)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str)) or node in docstrings:
            continue
        parent = parents.get(node)
        if isinstance(parent, ast.JoinedStr):
            continue  # handled at the f-string level below
        if (
            isinstance(parent, (ast.Compare, ast.Subscript))
            or isinstance(parent, ast.Dict)
            and node in parent.keys
        ):
            continue
        if isinstance(parent, ast.keyword) and parent.arg in (
            "dest",
            "metavar",
            "encoding",
            "name",
            "key",
            "id",
        ):
            continue
        p = parent
        while p is not None and not isinstance(p, ast.Call):
            if isinstance(p, (ast.stmt,)):
                p = None
                break
            p = parents.get(p)
        call = p
        if call is not None:
            name = _call_name(call.func)
            if name in PY_TRANSLATE:
                continue
            if name in PY_SKIP_CALLS and not (include_logs and name in ("info", "warning", "error")):
                continue
        conf = looks_user_facing(node.value)
        if not conf:
            continue
        kind = "literal"
        if call is not None and _call_name(call.func) in (
            "print",
            "flash",
            "messagebox",
            "showinfo",
            "showerror",
        ):
            conf, kind = "high", "ui-call"
        if call is not None and _call_name(call.func).endswith("Error") and conf == "medium":
            kind = "exception"
        add(findings, path, node.lineno, node.col_offset + 1, conf, kind, node.value, ns)
    for node in ast.walk(tree):
        if isinstance(node, ast.JoinedStr):
            parent = parents.get(node)
            if isinstance(parent, ast.Call) and _call_name(parent.func) in PY_SKIP_CALLS | PY_TRANSLATE:
                continue
            text = "".join(v.value if isinstance(v, ast.Constant) else "{x}" for v in node.values)
            conf = looks_user_facing(text)
            if conf:
                add(findings, path, node.lineno, node.col_offset + 1, conf, "f-string", text, ns)
    return findings


def is_test_file(path: Path) -> bool:
    name = path.name
    return bool(re.search(r"(\.test\.|\.spec\.|\.stories\.|^test_|_test\.py$)", name)) or any(
        part in ("tests", "test", "__tests__", "e2e", "cypress") for part in path.parts
    )


def iter_files(paths: list[Path], include_tests: bool):
    for root in paths:
        if root.is_file():
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
            for fn in sorted(filenames):
                p = Path(dirpath) / fn
                if p.suffix not in JS_EXT | PHP_EXT | PY_EXT or fn.endswith((".min.js", ".d.ts")):
                    continue
                if not include_tests and is_test_file(p.relative_to(root)):
                    continue
                yield p


def scan(paths: list[Path], include_tests=False, include_logs=False, text_domain=None) -> tuple[list, list]:
    findings: list[dict] = []
    errors: list[str] = []
    for path in iter_files(paths, include_tests):
        try:
            src = path.read_text(encoding="utf-8")
            if path.suffix in JS_EXT:
                findings += scan_js(src, path)
            elif path.suffix in PHP_EXT:
                findings += scan_php(src, path, text_domain)
            elif path.suffix in PY_EXT:
                findings += scan_python(src, path, include_logs)
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError) as exc:
            errors.append(f"{path}: {exc}")
    findings.sort(key=lambda f: (f["file"], f["line"], f["col"]))
    return findings, errors


def unique_keys(findings: list[dict]) -> dict[str, str]:
    catalog: dict[str, str] = {}
    for f in findings:
        if not f["key"]:
            continue
        key, n = f["key"], 2
        while key in catalog and catalog[key] != f["text"]:
            key, n = f"{f['key']}_{n}", n + 1
        f["key"] = key
        catalog[key] = f["text"]
    return catalog


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Find hard-coded user-facing strings in JS/TS/JSX/Vue/Svelte, PHP and Python.",
        epilog="Examples: find_hardcoded.py src/ | find_hardcoded.py wp-content/themes/mytheme "
        "--text-domain mytheme | find_hardcoded.py app/ --min-confidence high --json",
    )
    p.add_argument("paths", nargs="+", type=Path, help="files or directories to scan")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument(
        "--min-confidence",
        choices=list(CONFIDENCE),
        default="medium",
        help="lowest confidence to report (default: medium)",
    )
    p.add_argument("--include-tests", action="store_true", help="also scan test/spec/story files")
    p.add_argument(
        "--include-logs", action="store_true", help="Python: also report logger.info/warning/error text"
    )
    p.add_argument("--text-domain", help="WordPress: report __()/_e()/esc_html__() without this text domain")
    p.add_argument(
        "--emit-catalog",
        type=Path,
        metavar="FILE",
        help="write a JSON catalog skeleton {key: text} for the findings",
    )
    p.add_argument("--force", action="store_true", help="allow --emit-catalog to overwrite FILE")
    args = p.parse_args(argv)
    for path in args.paths:
        if not path.exists():
            print(f"error: {path} does not exist", file=sys.stderr)
            return 2
    findings, errors = scan(args.paths, args.include_tests, args.include_logs, args.text_domain)
    floor = CONFIDENCE[args.min_confidence]
    findings = [f for f in findings if CONFIDENCE[f["confidence"]] >= floor]
    catalog = unique_keys(findings)
    if args.emit_catalog:
        if args.emit_catalog.exists() and not args.force:
            print(f"error: {args.emit_catalog} exists; pass --force to overwrite", file=sys.stderr)
            return 2
        args.emit_catalog.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    if args.json:
        print(
            json.dumps(
                {"findings": findings, "errors": errors, "count": len(findings)}, ensure_ascii=False, indent=2
            )
        )
    else:
        for f in findings:
            extra = f" ({f['message']})" if f.get("message") else f"  -> {f['key']}"
            print(f"{f['file']}:{f['line']}:{f['col']} [{f['confidence']}] {f['kind']}: {f['text']!r}{extra}")
        for e in errors:
            print(f"skipped {e}", file=sys.stderr)
        print(f"\n{len(findings)} hard-coded string(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
