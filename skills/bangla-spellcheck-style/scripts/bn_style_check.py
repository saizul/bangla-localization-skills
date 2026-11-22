#!/usr/bin/env python3
"""Check Bangla text for common misspellings, mixed sadhu/cholito register, tone and punctuation.

Rules follow the Bangla Academy standard spelling (প্রমিত বাংলা বানান) for the most common,
unambiguous errors; see references/spelling-rules.md for the full list and the reasoning.

  spelling     সরকারী -> সরকারি, দূর্নীতি -> দুর্নীতি, ষ্টেশন -> স্টেশন, ব্যাবহার -> ব্যবহার ...
  register     সাধু (করিয়া, তাহার, হইবে) and চলিত (করে, তার, হবে) forms mixed in one text
  tone         --tone formal flags তুমি/তুই forms and informal imperatives (করো, দাও);
               --tone informal flags আপনি forms
  punctuation  '.' or '|' ending a Bangla sentence (use '।'), space before । ? ! ,
  digits       --digits bn flags Latin digits inside Bangla sentences (and --digits en the reverse)

Works on plain text, Markdown, HTML, JSON and PO files (line by line). --fix prints the text
with spelling and danda fixes applied (stdout only; nothing is written).

Exit codes: 0 = no findings at or above --fail-on, 1 = findings, 2 = error.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

BN = "\u0980-\u09ff"
LETTER = f"[{BN}\u200c\u200d]"
SEVERITY_ORDER = {"info": 0, "warning": 1, "error": 2}

# (wrong, right, note, allow_suffix). allow_suffix=True also matches inflected forms
# (সরকারীভাবে, বাড়ীতে). Keep entries unambiguous: never list a "wrong" form that is a
# correct word with another meaning.
SPELLING: list[tuple[str, str, str, bool]] = [
    ("সরকারী", "সরকারি", "-ই suffix in non-tatsama words takes ই-কার", True),
    ("দরকারী", "দরকারি", "-ই suffix in non-tatsama words takes ই-কার", True),
    ("বেসরকারী", "বেসরকারি", "-ই suffix in non-tatsama words takes ই-কার", True),
    ("জানুয়ারী", "জানুয়ারি", "foreign words take ই-কার", True),
    ("ফেব্রুয়ারী", "ফেব্রুয়ারি", "foreign words take ই-কার", True),
    ("বাড়ী", "বাড়ি", "tadbhava words take ই-কার", True),
    ("গাড়ী", "গাড়ি", "tadbhava words take ই-কার", True),
    ("শাড়ী", "শাড়ি", "tadbhava words take ই-কার", True),
    ("পাখী", "পাখি", "tadbhava words take ই-কার", True),
    ("কোম্পানী", "কোম্পানি", "foreign words take ই-কার", True),
    ("চাকুরী", "চাকরি", "standard form is চাকরি", True),
    ("চাকরী", "চাকরি", "foreign (Persian) word takes ই-কার", True),
    ("তৈরী", "তৈরি", "standard form takes ই-কার", True),
    ("জরুরী", "জরুরি", "foreign (Arabic) word takes ই-কার", True),
    ("ইংরেজী", "ইংরেজি", "language/nationality -ই suffix takes ই-কার", True),
    ("বাংলাদেশী", "বাংলাদেশি", "nationality -ই suffix takes ই-কার", True),
    ("আরবী", "আরবি", "language name takes ই-কার", True),
    ("ফারসী", "ফারসি", "language name takes ই-কার", True),
    ("হিন্দী", "হিন্দি", "language name takes ই-কার", True),
    ("শ্রেণী", "শ্রেণি", "Bangla Academy standard (2012) is শ্রেণি", True),
    ("কাহিনী", "কাহিনি", "Bangla Academy standard is কাহিনি", True),
    ("রাণী", "রানি", "Bangla Academy standard is রানি", True),
    ("কিংবদন্তী", "কিংবদন্তি", "Bangla Academy standard is কিংবদন্তি", True),
    ("দূর্নীতি", "দুর্নীতি", "prefix দুর্ (bad) takes উ-কার; দূর = far", True),
    ("দূর্ঘটনা", "দুর্ঘটনা", "prefix দুর্ (bad) takes উ-কার", True),
    ("দূর্বল", "দুর্বল", "prefix দুর্ (bad) takes উ-কার", True),
    ("দূর্ভাগ্য", "দুর্ভাগ্য", "prefix দুর্ (bad) takes উ-কার", True),
    ("দূর্যোগ", "দুর্যোগ", "prefix দুর্ (bad) takes উ-কার", True),
    ("মুহুর্ত", "মুহূর্ত", "মুহূর্ত has ঊ-কার after হ", True),
    ("পুরষ্কার", "পুরস্কার", "পুরঃ + কার -> পুরস্কার (স, not ষ)", True),
    ("উজ্জল", "উজ্জ্বল", "উৎ + জ্বল -> উজ্জ্বল (ব-ফলা)", True),
    ("শারিরীক", "শারীরিক", "শরীর + ইক -> শারীরিক", True),
    ("প্রতিযোগীতা", "প্রতিযোগিতা", "প্রতিযোগী + তা -> প্রতিযোগিতা (ই-কার)", True),
    ("সহযোগীতা", "সহযোগিতা", "সহযোগী + তা -> সহযোগিতা (ই-কার)", True),
    ("ব্যাবহার", "ব্যবহার", "ব্যবহার has no আ-কার", True),
    ("ব্যাবসা", "ব্যবসা", "ব্যবসা has no আ-কার", True),
    ("ব্যাবস্থা", "ব্যবস্থা", "ব্যবস্থা has no আ-কার", True),
    ("ষ্টেশন", "স্টেশন", "foreign words use স, never ষ", True),
    ("পোষ্ট", "পোস্ট", "foreign words use স, never ষ", True),
    ("মাষ্টার", "মাস্টার", "foreign words use স, never ষ", True),
    ("ষ্টোর", "স্টোর", "foreign words use স, never ষ", True),
    ("ফাষ্ট", "ফাস্ট", "foreign words use স, never ষ", True),
    ("ষ্টাফ", "স্টাফ", "foreign words use স, never ষ", True),
    ("লিষ্ট", "লিস্ট", "foreign words use স, never ষ", True),
    ("রেজিষ্ট্রেশন", "রেজিস্ট্রেশন", "foreign words use স, never ষ", True),
    ("কর্ণার", "কর্নার", "foreign words use ন, never ণ", True),
    ("গভর্ণর", "গভর্নর", "foreign words use ন, never ণ", True),
    ("আকাংখা", "আকাঙ্ক্ষা", "standard form is আকাঙ্ক্ষা", True),
    ("উচিৎ", "উচিত", "Bangla Academy standard is উচিত", False),
    ("সমিচীন", "সমীচীন", "standard form is সমীচীন", True),
    ("নিরিক্ষা", "নিরীক্ষা", "নির্ + ঈক্ষা -> নিরীক্ষা", True),
    ("অপরাহ্ন", "অপরাহ্ণ", "অপর + অহ্ন -> অপরাহ্ণ (ণত্ব after র)", True),
    ("পূর্বাহ্ন", "পূর্বাহ্ণ", "পূর্ব + অহ্ন -> পূর্বাহ্ণ (ণত্ব after র)", True),
    ("দারিদ্রতা", "দারিদ্র্য", "দারিদ্র্য already means poverty; -তা is redundant", True),
    ("সৌজন্যতা", "সৌজন্য", "সৌজন্য is already a noun; -তা is redundant", True),
    ("উৎকর্ষতা", "উৎকর্ষ", "উৎকর্ষ is already a noun; -তা is redundant", True),
    ("বুদ্ধিজীবি", "বুদ্ধিজীবী", "-জীবী takes ঈ-কার", True),
    ("শ্রমজীবি", "শ্রমজীবী", "-জীবী takes ঈ-কার", True),
    ("সত্বেও", "সত্ত্বেও", "standard form is সত্ত্বেও", False),
    ("স্বত্বেও", "সত্ত্বেও", "standard form is সত্ত্বেও", False),
    ("ভৌগলিক", "ভৌগোলিক", "ভূগোল + ইক -> ভৌগোলিক", True),
    ("আর্শীবাদ", "আশীর্বাদ", "আশীঃ + বাদ -> আশীর্বাদ", True),
    ("ইদানিং", "ইদানীং", "standard form is ইদানীং", False),
    ("নীচে", "নিচে", "নিচে (below) takes ই-কার; নীচ means mean/low", False),
    ("পৌছানো", "পৌঁছানো", "needs chandrabindu", True),
    ("পৌছে", "পৌঁছে", "needs chandrabindu", False),
    ("পৌছাতে", "পৌঁছাতে", "needs chandrabindu", False),
]
# Academy style for English "a" (as in app, account): অ্যা, not এ্যা. Reported as info.
STYLE_REGEX: list[tuple[str, str, str]] = [
    (
        f"(?<!{LETTER})\u098f\u09cd\u09af\u09be",
        "\u0985\u09cd\u09af\u09be",
        "write অ্যা (not এ্যা) for English 'a' sounds",
    ),
]
SADHU = [
    "তাহার",
    "তাহাকে",
    "তাহারা",
    "তাহাদের",
    "যাহা",
    "যাহার",
    "যাহারা",
    "তাহা",
    "ইহা",
    "উহা",
    "ইহার",
    "উহার",
    "করিয়া",
    "করিয়াছে",
    "করিয়াছিল",
    "করিতেছে",
    "করিতেছেন",
    "করিতে",
    "করিল",
    "করিলেন",
    "করিব",
    "করিবে",
    "হইয়া",
    "হইয়াছে",
    "হইয়াছিল",
    "হইতেছে",
    "হইবে",
    "হইল",
    "হইলেন",
    "হইতে",
    "গিয়াছে",
    "গিয়াছিল",
    "আসিয়া",
    "আসিল",
    "দেখিয়া",
    "দেখিল",
    "বলিয়া",
    "বলিল",
    "বলিলেন",
    "যাইতে",
    "যাইবে",
    "যাইয়া",
    "থাকিয়া",
    "লইয়া",
    "দিয়াছে",
    "দিয়াছিল",
    "পাইয়া",
    "পাইল",
]
CHOLITO = [
    "তাদের",
    "যারা",
    "যেটা",
    "এটা",
    "ওটা",
    "সেটা",
    "করেছে",
    "করেছিল",
    "করছে",
    "করছেন",
    "করতে",
    "করল",
    "করলেন",
    "করলাম",
    "হয়েছে",
    "হয়েছিল",
    "হচ্ছে",
    "হলো",
    "গেছে",
    "গিয়েছিল",
    "এসে",
    "দেখল",
    "বলল",
    "বললেন",
    "যেতে",
    "নিয়ে",
    "দিয়েছে",
    "দিয়েছিল",
    "পেয়ে",
    "পেল",
]
INFORMAL_2P = ["তুমি", "তোমার", "তোমাকে", "তোমরা", "তোমাদের", "তুই", "তোর", "তোকে", "তোদের"]
INFORMAL_IMPERATIVE = [
    "করো",
    "দেখো",
    "যাও",
    "দাও",
    "চলো",
    "বলো",
    "লেখো",
    "খোলো",
    "রাখো",
    "নাও",
    "এসো",
    "শোনো",
    "পড়ো",
]
FORMAL_2P = ["আপনি", "আপনার", "আপনাকে", "আপনারা", "আপনাদের"]


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def word_pattern(word: str, allow_suffix: bool) -> re.Pattern[str]:
    tail = "" if allow_suffix else f"(?!{LETTER})"
    return re.compile(f"(?<!{LETTER}){re.escape(nfc(word))}{tail}")


SPELLING_RE = [(word_pattern(w, s), nfc(w), nfc(r), note) for w, r, note, s in SPELLING]
STYLE_RE = [(re.compile(p), r, note) for p, r, note in STYLE_REGEX]


def finding(sev, line, col, rule, found, suggest, message):
    return {
        "severity": sev,
        "line": line,
        "col": col,
        "rule": rule,
        "found": found,
        "suggest": suggest,
        "message": message,
    }


def words_in(text: str, words: list[str]) -> list[tuple[str, int]]:
    hits = []
    for w in words:
        for m in word_pattern(w, False).finditer(text):
            hits.append((w, m.start()))
    return sorted(hits, key=lambda h: h[1])


def check_text(text: str, tone: str | None = None, digits: str | None = None) -> list[dict]:
    text = nfc(text)
    out: list[dict] = []
    lines = text.split("\n")

    def pos(offset: int) -> tuple[int, int]:
        line = text.count("\n", 0, offset) + 1
        return line, offset - (text.rfind("\n", 0, offset) + 1) + 1

    for rx, wrong, right, note in SPELLING_RE:
        for m in rx.finditer(text):
            ln, col = pos(m.start())
            out.append(finding("warning", ln, col, "spelling", wrong, right, note))
    for rx, right, note in STYLE_RE:
        for m in rx.finditer(text):
            ln, col = pos(m.start())
            out.append(finding("info", ln, col, "style", m.group(0), right, note))

    sadhu, cholito = words_in(text, SADHU), words_in(text, CHOLITO)
    if sadhu and cholito:
        ln, col = pos(sadhu[0][1])
        out.append(
            finding(
                "warning",
                ln,
                col,
                "register",
                ", ".join(sorted({w for w, _ in sadhu})[:5]),
                "use one register (চলিত for UI and web content)",
                f"sadhu forms ({len(sadhu)}) mixed with cholito forms ({len(cholito)}, e.g. "
                f"{', '.join(sorted({w for w, _ in cholito})[:3])}): গুরুচণ্ডালী দোষ",
            )
        )

    if tone == "formal":
        for w, off in words_in(text, INFORMAL_2P + INFORMAL_IMPERATIVE):
            ln, col = pos(off)
            sug = "আপনি-form (আপনি, আপনার, করুন, দেখুন, দিন)"
            out.append(finding("warning", ln, col, "tone", w, sug, "informal form in formal text"))
    elif tone == "informal":
        for w, off in words_in(text, FORMAL_2P):
            ln, col = pos(off)
            out.append(finding("info", ln, col, "tone", w, "তুমি-form", "formal form in informal text"))

    for i, line in enumerate(lines, 1):
        if not re.search(f"[{BN}]", line):
            continue
        for m in re.finditer(f"(?<=[{BN}])\\.(?=\\s*(?:$|[\"'\u201d<]|\\s[{BN}]))", line):
            if line[m.start() - 1 : m.start() + 2] == "...":
                continue
            out.append(
                finding(
                    "info",
                    i,
                    m.start() + 1,
                    "punctuation",
                    ".",
                    "\u0964",
                    "Bangla sentences end with the danda '\u0964'",
                )
            )
        for m in re.finditer(f"(?<=[{BN}])\\s*\\|(?=\\s|$)", line):
            out.append(
                finding(
                    "warning",
                    i,
                    m.start() + 1,
                    "punctuation",
                    "|",
                    "\u0964",
                    "ASCII '|' is not a danda; use '\u0964' (U+0964)",
                )
            )
        for m in re.finditer(f"(?<=[{BN}])[ \\t]+([\u0964?!,;:])", line):
            out.append(
                finding(
                    "info",
                    i,
                    m.start() + 1,
                    "punctuation",
                    m.group(0),
                    m.group(1),
                    "no space before punctuation",
                )
            )
        for m in re.finditer(f"\u0964(?=[{BN}])", line):
            out.append(
                finding(
                    "info",
                    i,
                    m.start() + 1,
                    "punctuation",
                    "\u0964",
                    "\u0964 ",
                    "add a space after the danda",
                )
            )
        if digits == "bn":
            for m in re.finditer(r"(?<![A-Za-z_%$#{.\-/])\d+(?:[.,]\d+)*(?![A-Za-z_%}])", line):
                out.append(
                    finding(
                        "info",
                        i,
                        m.start() + 1,
                        "digits",
                        m.group(0),
                        m.group(0).translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")),
                        "Latin digits in Bangla text (--digits bn)",
                    )
                )
        elif digits == "en":
            for m in re.finditer("[\u09e6-\u09ef]+", line):
                out.append(
                    finding(
                        "info",
                        i,
                        m.start() + 1,
                        "digits",
                        m.group(0),
                        m.group(0).translate(str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")),
                        "Bangla digits where Latin digits are required (--digits en)",
                    )
                )
    out.sort(key=lambda f: (f["line"], f["col"]))
    return out


def apply_fixes(text: str) -> str:
    text = nfc(text)
    for rx, _wrong, right, _note in SPELLING_RE:
        text = rx.sub(right, text)
    text = re.sub(f"(?<=[{BN}])[ \\t]*\\|(?=\\s|$)", "\u0964", text, flags=re.M)
    return text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Check Bangla text for misspellings, mixed sadhu/cholito register, tone, punctuation.",
        epilog="Examples: bn_style_check.py content/post.md | "
        "bn_style_check.py locales/bn.json --tone formal | bn_style_check.py draft.txt --fix > fixed.txt",
    )
    p.add_argument("paths", nargs="+", help="files, or - for stdin")
    p.add_argument("--tone", choices=["formal", "informal"], help="expected tone of address")
    p.add_argument("--digits", choices=["bn", "en"], help="expected digit script")
    p.add_argument("--fail-on", choices=list(SEVERITY_ORDER), default="warning")
    p.add_argument("--fix", action="store_true", help="print the text with spelling/danda fixes (one input)")
    p.add_argument("--json", action="store_true", help="print JSON")
    args = p.parse_args(argv)
    if args.fix and len(args.paths) != 1:
        p.error("--fix takes exactly one input")
    results = []
    for path in args.paths:
        try:
            text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8-sig")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"error: {path}: {exc}", file=sys.stderr)
            return 2
        if args.fix:
            sys.stdout.write(apply_fixes(text))
            return 0
        results.append({"file": path, "findings": check_text(text, args.tone, args.digits)})
    if args.json:
        print(json.dumps({"files": results}, ensure_ascii=False, indent=2))
    else:
        total = 0
        for r in results:
            for f in r["findings"]:
                total += 1
                print(
                    f"{r['file']}:{f['line']}:{f['col']} {f['severity'].upper()} {f['rule']}: "
                    f"{f['found']} -> {f['suggest']}  ({f['message']})"
                )
        print(f"\n{total} finding(s)")
    floor = SEVERITY_ORDER[args.fail_on]
    return 1 if any(SEVERITY_ORDER[f["severity"]] >= floor for r in results for f in r["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
