#!/usr/bin/env python3
"""Generate Banglish (romanized Bangla) spelling variants of Bangla keywords for SEO research.

People in Bangladesh often search in Latin script ("bhalobasar golpo", "valobasar golpo",
"mobile er dam koto"). This script romanizes each Bangla keyword the way people type it
(not ISO 15919), then produces the most likely spelling variants:

  ভ bh/v   শ ষ sh/s   স s/sh   long i ee/i   long u oo/u   জ য j/z   ফ f/ph   ছ ch/chh   ড় r/d
  inherent vowel o/a/dropped (simple Bangla schwa-deletion rules)

The output is a candidate list to check in a keyword tool or Search Console, not a
dictionary. English loanwords (মোবাইল -> "mobile") must be added by hand.

Input: keywords as arguments, or one per line from --file / stdin.
Exit codes: 0 = ok, 2 = error (for example no Bangla text in the input).
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys

HASANTA = "\u09cd"
NUKTA = "\u09bc"
CONSONANTS = {
    "ক": ["k"],
    "খ": ["kh"],
    "গ": ["g"],
    "ঘ": ["gh"],
    "ঙ": ["ng"],
    "চ": ["ch", "c"],
    "ছ": ["ch", "chh"],
    "জ": ["j", "z"],
    "ঝ": ["jh"],
    "ঞ": ["n"],
    "ট": ["t"],
    "ঠ": ["th"],
    "ড": ["d"],
    "ঢ": ["dh"],
    "ণ": ["n"],
    "ত": ["t"],
    "থ": ["th"],
    "দ": ["d"],
    "ধ": ["dh"],
    "ন": ["n"],
    "প": ["p"],
    "ফ": ["f", "ph"],
    "ব": ["b"],
    "ভ": ["bh", "v"],
    "ম": ["m"],
    "য": ["j", "z"],
    "র": ["r"],
    "ল": ["l"],
    "শ": ["sh", "s"],
    "ষ": ["sh", "s"],
    "স": ["s", "sh"],
    "হ": ["h"],
    "\u09dc": ["r", "d"],
    "\u09dd": ["rh", "r"],
    "\u09df": ["y", ""],  # ড় ঢ় য়
}
INDEPENDENT_VOWELS = {
    "অ": ["o", "a"],
    "আ": ["a"],
    "ই": ["i"],
    "ঈ": ["i", "ee"],
    "উ": ["u"],
    "ঊ": ["u", "oo"],
    "ঋ": ["ri"],
    "এ": ["e"],
    "ঐ": ["oi"],
    "ও": ["o"],
    "ঔ": ["ou", "ow"],
}
VOWEL_SIGNS = {
    "\u09be": ["a"],
    "\u09bf": ["i"],
    "\u09c0": ["i", "ee"],
    "\u09c1": ["u"],
    "\u09c2": ["u", "oo"],
    "\u09c3": ["ri"],
    "\u09c7": ["e"],
    "\u09c8": ["oi"],
    "\u09cb": ["o"],
    "\u09cc": ["ou", "ow"],
}
SIGNS = {"\u0982": ["ng"], "\u0983": ["h", ""], "\u0981": ["", "n"], "ৎ": ["t"]}
DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def normalize(word: str) -> str:
    for decomposed, composed in (
        ("\u09a1\u09bc", "\u09dc"),
        ("\u09a2\u09bc", "\u09dd"),
        ("\u09af\u09bc", "\u09df"),
    ):
        word = word.replace(decomposed, composed)
    return word.replace("\u200c", "").replace("\u200d", "")


def syllables(word: str) -> list[dict]:
    """Split a word into consonant/vowel units with their following marks."""
    units: list[dict] = []
    for ch in normalize(word):
        if ch in CONSONANTS:
            conjunct = bool(units) and units[-1]["type"] == "C" and units[-1].get("hasanta")
            units.append({"type": "C", "char": ch, "sign": None, "hasanta": False, "after_hasanta": conjunct})
        elif ch == HASANTA and units and units[-1]["type"] == "C":
            units[-1]["hasanta"] = True
        elif ch in VOWEL_SIGNS and units and units[-1]["type"] == "C":
            units[-1]["sign"] = ch
        elif ch in INDEPENDENT_VOWELS:
            units.append({"type": "V", "char": ch})
        elif ch in SIGNS:
            units.append({"type": "S", "char": ch})
        elif ch.isdigit() or ch in "০১২৩৪৫৬৭৮৯":
            units.append({"type": "D", "char": ch.translate(DIGITS)})
        # other marks (nukta, danda) are ignored
    return units


def inherent_options(units: list[dict], i: int) -> list[str]:
    """Return preferred-first options for the inherent vowel of consonant units[i]."""
    u = units[i]
    nxt = next((x for x in units[i + 1 :] if x["type"] in "CV"), None)
    rest_has_letter = any(x["type"] in "CV" for x in units[i + 1 :])
    if not rest_has_letter:
        # word-final: usually silent ("dam", "kolom"); a final conjunct keeps it ("bishwo" style)
        return ["o", ""] if u["after_hasanta"] else ["", "o"]
    if i == 0 or all(x["type"] != "C" and x["type"] != "V" for x in units[:i]):
        return ["o", "a"]
    if u["after_hasanta"]:
        return ["o", "", "a"]
    if nxt is not None and nxt["type"] == "C" and nxt["sign"] is not None and not nxt["hasanta"]:
        return ["", "o"]  # সরকারি -> sorkari, আমরা -> amra
    if nxt is not None and nxt["type"] == "C" and nxt["hasanta"]:
        return ["", "o"]
    return ["o", "", "a"]


# How freely a slot varies: lower = its alternatives rank higher. "v" for ভ is as common
# as "bh"; changing an inherent vowel is less likely than changing a consonant spelling.
WEIGHTS = {"ভ": 0.5, "শ": 0.8, "ষ": 0.8, "স": 1.2, "জ": 1.2, "য": 1.2}
INHERENT_WEIGHT = 1.5


def slots(word: str) -> list[tuple[list[str], float]]:
    units = syllables(word)
    out: list[tuple[list[str], float]] = []
    for i, u in enumerate(units):
        if u["type"] == "C":
            base = CONSONANTS[u["char"]]
            if u["after_hasanta"] and u["char"] == "য":
                base = ["y", ""]  # ya-phala: ব্যবসা byabsa / babsa
            elif u["after_hasanta"] and u["char"] == "ব":
                base = ["", "w", "b"]  # ba-phala: বিশ্ব bishwo / bissho
            elif u["after_hasanta"] and u["char"] == "র":
                base = ["r"]
            out.append((base, WEIGHTS.get(u["char"], 1.0)))
            if u["sign"]:
                out.append((VOWEL_SIGNS[u["sign"]], 1.0))
            elif not u["hasanta"]:
                out.append((inherent_options(units, i), INHERENT_WEIGHT))
        elif u["type"] == "V":
            out.append((INDEPENDENT_VOWELS[u["char"]], 1.0))
        elif u["type"] == "S":
            out.append((SIGNS[u["char"]], 1.0))
        else:
            out.append(([u["char"]], 1.0))
    return out


def word_variants(word: str, limit: int) -> list[str]:
    choice_sets = slots(word)
    if not choice_sets:
        return [word] if word else []
    ranked = []
    for combo in itertools.product(*(range(len(c)) for c, _ in choice_sets)):
        cost = sum(j * choice_sets[k][1] for k, j in enumerate(combo))
        if cost > 4:
            continue
        ranked.append((cost, "".join(choice_sets[k][0][j] for k, j in enumerate(combo))))
        if len(ranked) > 5000:
            break
    seen: list[str] = []
    for _, text in sorted(ranked):
        text = re.sub(r"(.)\1{2,}", r"\1\1", text)
        if text and text not in seen:
            seen.append(text)
        if len(seen) >= limit:
            break
    return seen


def keyword_variants(keyword: str, limit: int = 8) -> list[str]:
    words = keyword.split()
    per_word = [word_variants(w, limit) if re.search(r"[\u0980-\u09ff]", w) else [w.lower()] for w in words]
    per_word = [w for w in per_word if w]
    if not per_word:
        return []
    results: list[tuple[int, str]] = []
    for combo in itertools.product(*(range(len(w)) for w in per_word)):
        if sum(combo) > 3:
            continue
        results.append((sum(combo), " ".join(per_word[k][j] for k, j in enumerate(combo))))
    out: list[str] = []
    for _, text in sorted(results):
        if text not in out:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Generate Banglish (romanized Bangla) spelling variants of Bangla keywords.",
        epilog="Examples: banglish_variants.py 'ভালোবাসার গল্প' 'মোবাইলের দাম' | "
        "banglish_variants.py --file keywords.txt --json | banglish_variants.py --max 4 'শাড়ি'",
    )
    p.add_argument("keywords", nargs="*", help="Bangla keywords (quote multi-word keywords)")
    p.add_argument("--file", help="read keywords, one per line ('-' for stdin)")
    p.add_argument("--max", type=int, default=8, help="variants per keyword (default 8)")
    p.add_argument("--json", action="store_true", help="print JSON")
    p.add_argument("--csv", action="store_true", help="print keyword,variant rows")
    args = p.parse_args(argv)
    keywords = list(args.keywords)
    if args.file:
        try:
            fh = sys.stdin if args.file == "-" else open(args.file, encoding="utf-8")  # noqa: SIM115
            with fh:
                keywords += [line.strip() for line in fh if line.strip() and not line.startswith("#")]
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    if not keywords:
        p.error("give keywords as arguments or with --file")
    if not any(re.search(r"[\u0980-\u09ff]", k) for k in keywords):
        print("error: no Bangla (Bengali script) text in the input", file=sys.stderr)
        return 2
    result = {k: keyword_variants(k, args.max) for k in keywords}
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.csv:
        print("keyword,variant")
        for k, vs in result.items():
            for v in vs:
                print(f'"{k}","{v}"')
    else:
        for k, vs in result.items():
            print(f"{k}: {', '.join(vs)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
