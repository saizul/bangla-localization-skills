#!/usr/bin/env python3
"""Detect and fix broken Bangla Unicode text: mojibake, legacy Bijoy text, bad sequences.

  check  report problems (default; read-only). Exit 1 when anything is found.
  fix    print the normalized text to stdout, or rewrite files with --in-place (a .bak copy
         is kept unless --no-backup).

Fixes (each reported with a code):
  mojibake        UTF-8 Bangla decoded as Windows-1252/Latin-1 ("à¦¬à¦¾à¦‚à¦²à¦¾" -> "বাংলা")
  nfc             Unicode NFC (e-kar + aa-kar -> o-kar, e-kar + au length mark -> au-kar;
                  ড় ঢ় য় become two code points; use --nukta precomposed to keep one)
  a-aa            অ + aa-kar typed instead of আ
  prebase-order   i-kar / e-kar / oi-kar typed before the consonant ("েক" -> "কে")
  mark-order      nukta or chandrabindu in the wrong position ("চঁাদ" -> "চাঁদ")
  khanda-ta       ta + hasanta + ZWJ (old encoding) -> ৎ
  zero-width      stray ZWJ/ZWNJ/BOM/soft hyphen/ZWSP; keeps র‍্য (ra + ZWJ + hasanta + ya)
                  and a ZWJ/ZWNJ right after a hasanta
  duplicate-sign  the same vowel sign, hasanta or chandrabindu typed twice
  danda           ASCII '|' used as danda -> '।' ('||' -> '॥'); space before danda removed
  digits          with --digits bn|en, convert all digits
Reported only (not changed): legacy Bijoy/SutonnyMJ text, '?' replacement runs, dotted
circle U+25CC, orphan vowel signs, Assamese letters ৰ ৱ, mixed digit scripts in one number.

Exit codes: 0 = clean, 1 = problems found (check), 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter
from pathlib import Path

HASANTA = "\u09cd"
NUKTA = "\u09bc"
CANDRABINDU = "\u0981"
ZWNJ, ZWJ = "\u200c", "\u200d"
RA = "\u09b0"
BN = "\u0980-\u09ff"
CONS = "\u0995-\u09b9\u09ce\u09dc\u09dd\u09df"  # ka..ha, khanda ta, precomposed rra rha yya
CONS_RE = f"[{CONS}]"
VOWEL_SIGNS = "\u09be-\u09cc\u09d7\u09e2\u09e3"
VS_RE = f"[{VOWEL_SIGNS}]"
PREBASE = "\u09bf\u09c7\u09c8"  # i-kar, e-kar, oi-kar: drawn before the consonant, stored after it
BENGALI_RE = re.compile(f"[{BN}]")
BN_DIGITS = "\u09e6\u09e7\u09e8\u09e9\u09ea\u09eb\u09ec\u09ed\u09ee\u09ef"
NUKTA_PAIRS = {"\u09dc": "\u09a1\u09bc", "\u09dd": "\u09a2\u09bc", "\u09df": "\u09af\u09bc"}
CP1252_EXTRA = (
    "\u0152\u0153\u0160\u0161\u0178\u017d\u017e\u0192\u02c6\u02dc\u2013\u2014\u2018-\u201e"
    "\u2020-\u2022\u2026\u2030\u2039\u203a\u20ac\u2122"
)
# Bengali UTF-8 is E0 A6 xx / E0 A7 xx, which Windows-1252 shows as "à¦x" / "à§x".
MOJIBAKE_RE = re.compile(
    f"(?:\u00e0[\u00a6\u00a7][\u0080-\u00bf{CP1252_EXTRA}]|\u00e2\u20ac[\u0080-\u00bf{CP1252_EXTRA}])+"
)
BIJOY_WORDS = re.compile(
    r"(?<![A-Za-z])(Avwg|Avgvi|Avgiv|evsjv|Ges|Kiv|K\u2021i|Rb\u00a8|n\u2021q|nq|wK|bv|Zvi|mgq|"
    r"Avcwb|Avcbvi|we\u2021kl|cÖ_g|\u2020`k)(?![A-Za-z])"
)
BIJOY_CHARS = set(
    "\u2020\u2021\u00a8\u00a9\u00d6\u00d5\u00d7\u00ae\u00af\u00b0\u00b1\u00b2\u00b3\u00b4\u00b5\u00b6"
    "\u00b7\u00b8\u00b9\u00ba\u00bb\u00bc\u00bd\u00be\u00bf\u02c6\u2030\u0160\u2039\u0152"
)


def _fix_mojibake_run(run: str) -> str | None:
    data = bytearray()
    for ch in run:
        if ord(ch) < 256:
            data.append(ord(ch))
        else:
            try:
                data += ch.encode("cp1252")
            except UnicodeEncodeError:
                return None
    try:
        fixed = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return fixed


def fix_mojibake(text: str, counts: Counter) -> str:
    def repl(m: re.Match) -> str:
        fixed = _fix_mojibake_run(m.group(0))
        if fixed is None:
            return m.group(0)
        counts["mojibake"] += 1
        return fixed

    return MOJIBAKE_RE.sub(repl, text)


def _sub(pattern: str, repl, text: str, code: str, counts: Counter, flags: int = 0) -> str:
    new, n = re.subn(pattern, repl, text, flags=flags)
    if n:
        counts[code] += n
    return new


def clean_joiners(text: str, counts: Counter) -> str:
    """Drop ZWJ/ZWNJ except where they carry meaning.

    Kept: ZWJ in ra + ZWJ + hasanta (র‍্য, ra + ya-phala as in র‍্যাব), a ZWJ/ZWNJ right
    after a hasanta (half form / visible hasanta), and a ZWNJ right before a hasanta.
    """
    out: list[str] = []
    for i, ch in enumerate(text):
        if ch in (ZWJ, ZWNJ):
            prev = out[-1] if out else ""
            nxt = text[i + 1] if i + 1 < len(text) else ""
            keep = (
                prev == HASANTA
                or (ch == ZWJ and prev == RA and nxt == HASANTA)
                or (ch == ZWNJ and nxt == HASANTA and bool(prev) and bool(BENGALI_RE.match(prev)))
            )
            if keep and prev not in (ZWJ, ZWNJ):
                out.append(ch)
            else:
                counts["zero-width"] += 1
            continue
        out.append(ch)
    return "".join(out)


def normalize(
    text: str, nukta: str = "decomposed", digits: str | None = None, counts: Counter | None = None
) -> str:
    """Return normalized text; counts receives the number of fixes per code."""
    counts = Counter() if counts is None else counts
    text = fix_mojibake(text, counts)
    text = _sub("\u09a4\u09cd\u200d", "\u09ce", text, "khanda-ta", counts)
    text = _sub("[\ufeff\u00ad\u200b]", "", text, "zero-width", counts)
    text = clean_joiners(text, counts)
    text = _sub("\u0985\u09be", "\u0986", text, "a-aa", counts)
    # pre-base vowel sign typed before its consonant cluster: "েক" -> "কে", "িক্ষ" -> "ক্ষি"
    cluster = f"{CONS_RE}{NUKTA}?(?:{HASANTA}[{ZWNJ}{ZWJ}]?{CONS_RE}{NUKTA}?)*"
    text = _sub(
        f"(?<![{BN}{ZWNJ}{ZWJ}])([{PREBASE}])({cluster})(?!{HASANTA})",
        lambda m: m.group(2) + m.group(1),
        text,
        "prebase-order",
        counts,
    )
    # mark order: nukta right after the consonant, chandrabindu after the vowel sign
    text = _sub(f"({CONS_RE})({VS_RE})({NUKTA})", r"\1\3\2", text, "mark-order", counts)
    text = _sub(
        f"({CONS_RE}{NUKTA}?){CANDRABINDU}({VS_RE})", "\\1\\2" + CANDRABINDU, text, "mark-order", counts
    )
    text = _sub(f"({VS_RE}|{HASANTA}|{CANDRABINDU})\\1+", r"\1", text, "duplicate-sign", counts)
    text = _sub(f"(?<=[{BN}])[ \t]*\\|\\|(?=\\s|$)", "\u0965", text, "danda", counts, re.M)
    text = _sub(f"(?<=[{BN}])[ \t]*\\|(?=\\s|$)", "\u0964", text, "danda", counts, re.M)
    text = _sub(f"(?<=[{BN}])[ \t]+(?=[\u0964\u0965])", "", text, "danda", counts)
    nfc = unicodedata.normalize("NFC", text)
    if nfc != text:
        counts["nfc"] += sum(1 for ch in text if unicodedata.normalize("NFC", ch) != ch) or 1
        counts["nfc"] += len(re.findall("\u09c7[\u09be\u09d7]", text))
        text = nfc
    if nukta == "precomposed":
        for pre, dec in NUKTA_PAIRS.items():
            text = text.replace(dec, pre)
    if digits == "bn":
        text = _sub("[0-9]", lambda m: BN_DIGITS[int(m.group(0))], text, "digits", counts)
    elif digits == "en":
        text = _sub(f"[{BN_DIGITS}]", lambda m: str(BN_DIGITS.index(m.group(0))), text, "digits", counts)
    return text


def detect(text: str) -> list[dict]:
    """Problems that are reported but not fixed automatically."""
    out: list[dict] = []

    def add(code: str, pos: int, message: str) -> None:
        out.append({"code": code, "line": text.count("\n", 0, pos) + 1, "message": message})

    letters = sum(1 for c in text if c.isalpha())
    bn = len(BENGALI_RE.findall(text))
    bijoy_hits = BIJOY_WORDS.findall(text)
    bijoy_chars = sum(1 for c in text if c in BIJOY_CHARS)
    n_words = max(1, len(text.split()))
    strong = len(bijoy_hits) >= 3 or (len(bijoy_hits) >= 2 and bijoy_chars >= 1)
    if strong and len(bijoy_hits) / n_words >= 0.15 and bn < letters * 0.2:
        add(
            "bijoy",
            0,
            f"looks like legacy Bijoy/SutonnyMJ (ANSI) text ({len(bijoy_hits)} typical words); "
            "convert it with a Bijoy-to-Unicode converter (see references/bijoy-legacy.md)",
        )
    for m in re.finditer("\\?{2,}|\ufffd+", text):
        add("replacement", m.start(), f"'{m.group(0)}' looks like characters lost in a bad conversion")
    for m in re.finditer("\u25cc", text):
        add("dotted-circle", m.start(), "dotted circle U+25CC: a mark was copied without its base letter")
    for m in re.finditer(f"(?:^|(?<=[\\s\u0964,.!?\"'(]))({VS_RE}|{HASANTA}|{NUKTA})", text, re.M):
        add("orphan-sign", m.start(), f"vowel sign/hasanta U+{ord(m.group(1)):04X} without a base consonant")
    for m in re.finditer("[\u09f0\u09f1]", text):
        add(
            "assamese",
            m.start(),
            f"Assamese letter U+{ord(m.group(0)):04X} in Bangla text; use ra/ba (U+09B0/U+09AC)",
        )
    for m in re.finditer(f"[0-9{BN_DIGITS}]+", text):
        if re.search("[0-9]", m.group(0)) and re.search(f"[{BN_DIGITS}]", m.group(0)):
            add("mixed-digits", m.start(), f"'{m.group(0)}' mixes Latin and Bangla digits")
    return out


def process(
    text: str, nukta: str = "decomposed", digits: str | None = None
) -> tuple[str, Counter, list[dict]]:
    counts: Counter = Counter()
    fixed = normalize(text, nukta, digits, counts)
    return fixed, counts, detect(fixed)


def read(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    return Path(path).read_text(encoding="utf-8-sig")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Detect and fix broken Bangla Unicode text (mojibake, bad sequences, stray ZWJ/ZWNJ).",
        epilog="Examples: bn_normalize.py check content/*.md | bn_normalize.py fix post.txt > fixed.txt | "
        "bn_normalize.py fix locales/bn.json --in-place | bn_normalize.py fix - < broken.txt",
    )
    p.add_argument("mode", choices=["check", "fix"], help="check = report only, fix = output normalized text")
    p.add_argument("paths", nargs="+", help="files, or - for stdin")
    p.add_argument(
        "--nukta",
        choices=["decomposed", "precomposed"],
        default="decomposed",
        help="store ড় ঢ় য় as NFC two-code-point sequences (default) or as one precomposed code point",
    )
    p.add_argument("--digits", choices=["bn", "en"], help="convert all digits to Bangla or Latin")
    p.add_argument("--in-place", action="store_true", help="fix: rewrite the files")
    p.add_argument("--no-backup", action="store_true", help="fix --in-place: do not keep FILE.bak")
    p.add_argument("--json", action="store_true", help="print a JSON report")
    args = p.parse_args(argv)
    if args.in_place and (args.mode != "fix" or "-" in args.paths):
        p.error("--in-place needs 'fix' and real files")
    report = []
    found = False
    for path in args.paths:
        try:
            text = read(path)
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            return 2
        fixed, counts, notes = process(text, args.nukta, args.digits)
        changed = fixed != text
        found = found or changed or bool(notes)
        report.append({"file": path, "changed": changed, "fixes": dict(counts), "notes": notes})
        if args.mode == "fix":
            if args.in_place:
                if changed:
                    if not args.no_backup:
                        shutil.copyfile(path, path + ".bak")
                    Path(path).write_text(fixed, encoding="utf-8")
            elif not args.json:
                sys.stdout.write(fixed)
    if args.json:
        print(json.dumps({"files": report}, ensure_ascii=False, indent=2))
    elif args.mode == "check" or args.in_place:
        for r in report:
            fixes = ", ".join(f"{k}={v}" for k, v in sorted(r["fixes"].items())) or "none"
            if args.mode == "check":
                status = "would change" if r["changed"] else "ok"
            else:
                status = "rewritten" if r["changed"] else "unchanged"
            print(f"{r['file']}: {status}; fixes: {fixes}")
            for n in r["notes"]:
                print(f"  line {n['line']}: [{n['code']}] {n['message']}")
    if args.mode == "fix":
        return 0
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
