#!/usr/bin/env python3
"""Format numbers, BDT amounts and dates for Bangla (bn-BD), deterministically.

Subcommands:
  digits    convert digits between Latin (0-9) and Bangla (০-৯)
  parse     turn Bangla/Latin input like "১২,৩৪,৫৬৭.৫০" into a machine number "1234567.50"
  number    lakh/crore grouping (১২,৩৪,৫৬৭) or international grouping, optional compact (১.২৫ কোটি)
  currency  BDT amounts: ৳ ১,২৩,৪৫৬.০০ | ১,২৩,৪৫৬.০০ টাকা | BDT 1,23,456.00
  words     number or amount in Bangla words ("এক লক্ষ তেইশ হাজার ... টাকা মাত্র")
  date      Gregorian date in Bangla (রবিবার, ২২ নভেম্বর ২০২৬; ordinal ২২শে নভেম্বর)
  bangabda  Bangla calendar date (revised Bangladesh civil calendar, 2019): ৭ অগ্রহায়ণ ১৪৩৩
  time      12-hour Bangla time with part of day (বিকাল ৩টা ৪৫ মিনিট / বিকাল ৩:৪৫)
  phone     validate and normalise Bangladeshi mobile numbers (০১৭১১-২২৩৩৪৪ -> +8801711223344)

Standard library only. Exit codes: 0 = ok, 2 = invalid input.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

BN_DIGITS = "০১২৩৪৫৬৭৮৯"
TO_BN = str.maketrans("0123456789", BN_DIGITS)
TO_EN = str.maketrans(BN_DIGITS, "0123456789")

GREGORIAN_MONTHS = [
    "জানুয়ারি",
    "ফেব্রুয়ারি",
    "মার্চ",
    "এপ্রিল",
    "মে",
    "জুন",
    "জুলাই",
    "আগস্ট",
    "সেপ্টেম্বর",
    "অক্টোবর",
    "নভেম্বর",
    "ডিসেম্বর",
]
WEEKDAYS = ["সোমবার", "মঙ্গলবার", "বুধবার", "বৃহস্পতিবার", "শুক্রবার", "শনিবার", "রবিবার"]  # Monday first
BANGLA_MONTHS = [
    "বৈশাখ",
    "জ্যৈষ্ঠ",
    "আষাঢ়",
    "শ্রাবণ",
    "ভাদ্র",
    "আশ্বিন",
    "কার্তিক",
    "অগ্রহায়ণ",
    "পৌষ",
    "মাঘ",
    "ফাল্গুন",
    "চৈত্র",
]
SEASONS = ["গ্রীষ্ম", "বর্ষা", "শরৎ", "হেমন্ত", "শীত", "বসন্ত"]  # two months each, from Boishakh

# 0-99: Bangla number words are irregular, so every value is listed.
ONES = [
    "শূন্য",
    "এক",
    "দুই",
    "তিন",
    "চার",
    "পাঁচ",
    "ছয়",
    "সাত",
    "আট",
    "নয়",
    "দশ",
    "এগারো",
    "বারো",
    "তেরো",
    "চৌদ্দ",
    "পনেরো",
    "ষোলো",
    "সতেরো",
    "আঠারো",
    "উনিশ",
    "বিশ",
    "একুশ",
    "বাইশ",
    "তেইশ",
    "চব্বিশ",
    "পঁচিশ",
    "ছাব্বিশ",
    "সাতাশ",
    "আটাশ",
    "ঊনত্রিশ",
    "ত্রিশ",
    "একত্রিশ",
    "বত্রিশ",
    "তেত্রিশ",
    "চৌত্রিশ",
    "পঁয়ত্রিশ",
    "ছত্রিশ",
    "সাঁইত্রিশ",
    "আটত্রিশ",
    "ঊনচল্লিশ",
    "চল্লিশ",
    "একচল্লিশ",
    "বিয়াল্লিশ",
    "তেতাল্লিশ",
    "চুয়াল্লিশ",
    "পঁয়তাল্লিশ",
    "ছেচল্লিশ",
    "সাতচল্লিশ",
    "আটচল্লিশ",
    "ঊনপঞ্চাশ",
    "পঞ্চাশ",
    "একান্ন",
    "বাহান্ন",
    "তিপ্পান্ন",
    "চুয়ান্ন",
    "পঞ্চান্ন",
    "ছাপ্পান্ন",
    "সাতান্ন",
    "আটান্ন",
    "ঊনষাট",
    "ষাট",
    "একষট্টি",
    "বাষট্টি",
    "তেষট্টি",
    "চৌষট্টি",
    "পঁয়ষট্টি",
    "ছেষট্টি",
    "সাতষট্টি",
    "আটষট্টি",
    "ঊনসত্তর",
    "সত্তর",
    "একাত্তর",
    "বাহাত্তর",
    "তিয়াত্তর",
    "চুয়াত্তর",
    "পঁচাত্তর",
    "ছিয়াত্তর",
    "সাতাত্তর",
    "আটাত্তর",
    "ঊনআশি",
    "আশি",
    "একাশি",
    "বিরাশি",
    "তিরাশি",
    "চুরাশি",
    "পঁচাশি",
    "ছিয়াশি",
    "সাতাশি",
    "অষ্টাশি",
    "ঊননব্বই",
    "নব্বই",
    "একানব্বই",
    "বিরানব্বই",
    "তিরানব্বই",
    "চুরানব্বই",
    "পঁচানব্বই",
    "ছিয়ানব্বই",
    "সাতানব্বই",
    "আটানব্বই",
    "নিরানব্বই",
]
assert len(ONES) == 100


def to_bn_digits(text: str) -> str:
    return str(text).translate(TO_BN)


def to_en_digits(text: str) -> str:
    return str(text).translate(TO_EN)


def parse_number(text: str) -> Decimal:
    """Parse '১২,৩৪,৫৬৭.৫০', '1,234,567.50', '৳ ১,০০০', '-৫০' into a Decimal."""
    s = to_en_digits(text).strip()
    s = re.sub(r"^(?:৳|Tk\.?|BDT|টাকা)\s*|\s*(?:৳|টাকা|Tk\.?|BDT|/-)$", "", s, flags=re.I).strip()
    s = s.replace("−", "-").replace(" ", "").replace("\u00a0", "")
    if not re.fullmatch(r"[-+]?(\d{1,3}(,\d{2})*(,\d{3})|\d+|\d{1,3}(,\d{3})+)?(\.\d+)?", s) or s in (
        "",
        "-",
        "+",
    ):
        raise ValueError(f"not a number: {text!r}")
    try:
        return Decimal(s.replace(",", ""))
    except InvalidOperation as exc:  # pragma: no cover - guarded by the regex
        raise ValueError(f"not a number: {text!r}") from exc


def group_indian(int_digits: str) -> str:
    """'1234567' -> '12,34,567' (last three digits, then groups of two)."""
    if len(int_digits) <= 3:
        return int_digits
    head, tail = int_digits[:-3], int_digits[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail])


def group_international(int_digits: str) -> str:
    return f"{int(int_digits):,}"


def format_number(value, decimals: int | None = None, digits: str = "bn", grouping: str = "indian") -> str:
    d = value if isinstance(value, Decimal) else parse_number(str(value))
    if decimals is not None:
        d = d.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    sign = "-" if d < 0 else ""
    text = format(abs(d), "f")
    int_part, _, frac = text.partition(".")
    if grouping == "indian":
        int_part = group_indian(int_part)
    elif grouping == "international":
        int_part = group_international(int_part)
    out = sign + int_part + ("." + frac if frac else "")
    return to_bn_digits(out) if digits == "bn" else out


def format_compact(value, digits: str = "bn", lakh_word: str = "লক্ষ", max_decimals: int = 2) -> str:
    d = value if isinstance(value, Decimal) else parse_number(str(value))
    units = [(Decimal(10) ** 7, "কোটি"), (Decimal(10) ** 5, lakh_word), (Decimal(1000), "হাজার")]
    for size, word in units:
        if abs(d) >= size:
            q = (d / size).quantize(Decimal(1).scaleb(-max_decimals), rounding=ROUND_HALF_UP).normalize()
            num = format(q, "f")
            if "." in num:
                num = num.rstrip("0").rstrip(".")
            if q >= 1000 and word == "কোটি":
                num = format_number(q, None, "en", "indian")
            return f"{to_bn_digits(num) if digits == 'bn' else num} {word}"
    return format_number(d, None, digits)


def format_currency(
    value, style: str = "symbol", digits: str = "bn", decimals: int = 2, space: bool = True
) -> str:
    d = parse_number(str(value)) if not isinstance(value, Decimal) else value
    neg = d < 0
    num = format_number(abs(d), decimals, digits, "indian")
    gap = "\u00a0" if space else ""
    if style == "symbol":
        out = f"৳{gap}{num}"
    elif style == "word":
        out = f"{num} টাকা"
    elif style == "code":
        out = f"BDT{gap}{num}"
    else:
        raise ValueError(f"unknown currency style {style!r}")
    return f"-{out}" if neg else out


def words_below_crore(n: int, lakh_word: str) -> list[str]:
    parts: list[str] = []
    for size, word in ((100000, lakh_word), (1000, "হাজার"), (100, "শত")):
        if n >= size:
            q, n = divmod(n, size)
            parts.append(ONES[q] + word if word == "শত" else f"{ONES[q]} {word}")
    if n:
        parts.append(ONES[n])
    return parts


def number_to_words(n: int, lakh_word: str = "লক্ষ") -> str:
    """Integer to Bangla words using the South Asian system (শত, হাজার, লক্ষ, কোটি)."""
    if n == 0:
        return ONES[0]
    if n < 0:
        return "ঋণাত্মক " + number_to_words(-n, lakh_word)
    parts: list[str] = []
    crore, rest = divmod(n, 10**7)
    if crore:
        parts.append(f"{number_to_words(crore, lakh_word)} কোটি")
    parts += words_below_crore(rest, lakh_word)
    return " ".join(parts)


def amount_in_words(value, lakh_word: str = "লক্ষ", suffix: str = "মাত্র") -> str:
    d = (value if isinstance(value, Decimal) else parse_number(str(value))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    if d < 0:
        raise ValueError("amounts in words must not be negative")
    taka = int(d)
    poisa = int((d - taka) * 100)
    out = f"{number_to_words(taka, lakh_word)} টাকা"
    if poisa:
        out += f" {number_to_words(poisa, lakh_word)} পয়সা"
    return f"{out} {suffix}".strip()


def ordinal_suffix(day: int) -> str:
    """Suffix used for dates: ১লা, ২রা, ৩রা, ৪ঠা, ৫ই ... ১৮ই, ১৯শে ... ৩১শে."""
    if day == 1:
        return "লা"
    if day in (2, 3):
        return "রা"
    if day == 4:
        return "ঠা"
    if 5 <= day <= 18:
        return "ই"
    return "শে"


def format_gregorian(date: dt.date, weekday: bool = True, ordinal: bool = False, digits: str = "bn") -> str:
    day = str(date.day) + (ordinal_suffix(date.day) if ordinal else "")
    text = f"{day} {GREGORIAN_MONTHS[date.month - 1]} {date.year}"
    if weekday:
        text = f"{WEEKDAYS[date.weekday()]}, {text}"
    return to_bn_digits(text) if digits == "bn" else text


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def bangabda(date: dt.date) -> dict:
    """Revised Bangladesh calendar (in use since 1426 / 2019).

    Pohela Boishakh is 14 April. Boishakh to Ashwin have 31 days, Kartik to Magh and
    Chaitra have 30, Falgun has 29 (30 when the Gregorian February is a leap month).
    """
    start_year = date.year if date >= dt.date(date.year, 4, 14) else date.year - 1
    year = start_year - 593
    lengths = [31] * 6 + [30, 30, 30, 30, 30 if _is_leap(start_year + 1) else 29, 30]
    offset = (date - dt.date(start_year, 4, 14)).days
    month = 0
    while offset >= lengths[month]:
        offset -= lengths[month]
        month += 1
    return {
        "year": year,
        "month": month + 1,
        "month_name": BANGLA_MONTHS[month],
        "day": offset + 1,
        "season": SEASONS[month // 2],
        "weekday": WEEKDAYS[date.weekday()],
        "month_length": lengths[month],
    }


def format_bangabda(
    date: dt.date, ordinal: bool = False, era: bool = True, weekday: bool = False, digits: str = "bn"
) -> str:
    b = bangabda(date)
    day = str(b["day"]) + (ordinal_suffix(b["day"]) if ordinal else "")
    text = f"{day} {b['month_name']} {b['year']}" + (" বঙ্গাব্দ" if era else "")
    if weekday:
        text = f"{b['weekday']}, {text}"
    return to_bn_digits(text) if digits == "bn" else text


def part_of_day(hour: int) -> str:
    """Conventional Bangla parts of the day (boundaries vary by speaker; these are common)."""
    if 4 <= hour < 6:
        return "ভোর"
    if 6 <= hour < 12:
        return "সকাল"
    if 12 <= hour < 15:
        return "দুপুর"
    if 15 <= hour < 18:
        return "বিকাল"
    if 18 <= hour < 20:
        return "সন্ধ্যা"
    return "রাত"


def format_time(t: dt.time, style: str = "clock", digits: str = "bn") -> str:
    h12 = t.hour % 12 or 12
    if style == "clock":
        text = f"{part_of_day(t.hour)} {h12}:{t.minute:02d}"
    else:
        text = f"{part_of_day(t.hour)} {h12}টা" + (f" {t.minute} মিনিট" if t.minute else "")
    return to_bn_digits(text) if digits == "bn" else text


# Original operator by prefix. Since mobile number portability (2018) a number may have moved.
MOBILE_OPERATORS = {
    "13": "Grameenphone",
    "14": "Banglalink",
    "15": "Teletalk",
    "16": "Robi (Airtel)",
    "17": "Grameenphone",
    "18": "Robi",
    "19": "Banglalink",
}
PHONE_STYLES = ("e164", "local", "bn", "intl")


def normalize_bd_mobile(text: str) -> dict:
    """Validate a Bangladeshi mobile number and return it in every display style.

    Accepts Bangla or Latin digits, spaces, dashes, dots and brackets, and the forms
    01XXXXXXXXX, 1XXXXXXXXX, 8801XXXXXXXXX, +8801XXXXXXXXX, 008801XXXXXXXXX and +880 01XXXXXXXXX.
    """
    raw = to_en_digits(text).strip()
    s = re.sub(r"[\s\-.()\u00a0]", "", raw)
    if s.startswith("+"):
        s = s[1:]
    elif s.startswith("00"):
        s = s[2:]
    if re.fullmatch(r"8801\d{9}", s):
        national = s[3:]
    elif re.fullmatch(r"88001\d{9}", s):  # +880 0171... (trunk zero kept by mistake)
        national = s[4:]
    elif re.fullmatch(r"01\d{9}", s):
        national = s[1:]
    elif re.fullmatch(r"1\d{9}", s):
        national = s
    else:
        raise ValueError(f"not a Bangladeshi mobile number: {text!r}")
    prefix = national[:2]
    if prefix not in MOBILE_OPERATORS:
        raise ValueError(f"unknown mobile prefix 0{prefix} in {text!r} (valid: 013-019)")
    local = f"0{national[:4]}-{national[4:]}"
    return {
        "input": text,
        "e164": f"+880{national}",
        "local": local,
        "bn": to_bn_digits(local),
        "intl": f"+880 {national[:4]}-{national[4:]}",
        "operator": MOBILE_OPERATORS[prefix],
    }


def _date(value: str) -> dt.date:
    if value == "today":
        return dt.date.today()
    try:
        return dt.date.fromisoformat(to_en_digits(value))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD, got {value!r}") from exc


def _time(value: str) -> dt.time:
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", to_en_digits(value))
    if not m or int(m.group(1)) > 23 or int(m.group(2)) > 59:
        raise argparse.ArgumentTypeError(f"expected HH:MM (24-hour), got {value!r}")
    return dt.time(int(m.group(1)), int(m.group(2)))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Format numbers, BDT amounts and dates for Bangla (bn-BD).",
        epilog="Examples: bn_format.py number 1234567.5 | bn_format.py currency 125000 | "
        "bn_format.py words 123456.50 --amount | bn_format.py bangabda 2026-04-14 | "
        "bn_format.py date 2026-02-21 --ordinal",
    )
    p.add_argument("--json", action="store_true", help="print JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("digits", help="convert digits")
    s.add_argument("text", nargs="+")
    s.add_argument("--to", choices=["bn", "en"], default="bn")

    s = sub.add_parser("parse", help="Bangla/Latin formatted number -> machine number")
    s.add_argument("text", nargs="+")

    s = sub.add_parser("number", help="group a number")
    s.add_argument("value")
    s.add_argument("--decimals", type=int)
    s.add_argument("--digits", choices=["bn", "en"], default="bn")
    s.add_argument("--grouping", choices=["indian", "international", "none"], default="indian")
    s.add_argument("--compact", action="store_true", help="use হাজার/লক্ষ/কোটি units")
    s.add_argument("--lakh-word", choices=["লক্ষ", "লাখ"], default="লক্ষ")

    s = sub.add_parser("currency", help="format a BDT amount")
    s.add_argument("value")
    s.add_argument("--style", choices=["symbol", "word", "code"], default="symbol")
    s.add_argument("--digits", choices=["bn", "en"], default="bn")
    s.add_argument("--decimals", type=int, default=2)
    s.add_argument("--no-space", action="store_true", help="no non-breaking space after ৳ / BDT")

    s = sub.add_parser("words", help="number or amount in words")
    s.add_argument("value")
    s.add_argument("--amount", action="store_true", help="taka and poisa, ending with মাত্র")
    s.add_argument("--lakh-word", choices=["লক্ষ", "লাখ"], default="লক্ষ")

    s = sub.add_parser("date", help="Gregorian date in Bangla")
    s.add_argument("date", type=_date, help="YYYY-MM-DD or 'today'")
    s.add_argument("--ordinal", action="store_true", help="২২শে নভেম্বর style")
    s.add_argument("--no-weekday", action="store_true")
    s.add_argument("--digits", choices=["bn", "en"], default="bn")

    s = sub.add_parser("bangabda", help="Bangla calendar date (Bangladesh, revised 2019)")
    s.add_argument("date", type=_date, help="YYYY-MM-DD or 'today'")
    s.add_argument("--ordinal", action="store_true")
    s.add_argument("--weekday", action="store_true")
    s.add_argument("--no-era", action="store_true", help="omit 'বঙ্গাব্দ'")
    s.add_argument("--digits", choices=["bn", "en"], default="bn")

    s = sub.add_parser("time", help="Bangla time with part of day")
    s.add_argument("time", type=_time, help="HH:MM, 24-hour")
    s.add_argument("--style", choices=["clock", "spoken"], default="clock")
    s.add_argument("--digits", choices=["bn", "en"], default="bn")

    s = sub.add_parser("phone", help="validate/normalise Bangladeshi mobile numbers")
    s.add_argument("text", nargs="+", help="numbers in any common form, Bangla or Latin digits")
    s.add_argument("--style", choices=PHONE_STYLES, default="e164", help="output style (default e164)")
    return p


def run(args) -> tuple[str | list[str], dict]:
    if args.cmd == "digits":
        fn = to_bn_digits if args.to == "bn" else to_en_digits
        out = [fn(t) for t in args.text]
        return out, {"results": out}
    if args.cmd == "parse":
        out = [format(parse_number(t), "f") for t in args.text]
        return out, {"results": out}
    if args.cmd == "number":
        if args.compact:
            text = format_compact(args.value, args.digits, args.lakh_word)
        else:
            text = format_number(args.value, args.decimals, args.digits, args.grouping)
        return text, {"result": text}
    if args.cmd == "currency":
        text = format_currency(args.value, args.style, args.digits, args.decimals, not args.no_space)
        return text, {"result": text}
    if args.cmd == "words":
        if args.amount:
            text = amount_in_words(args.value, args.lakh_word)
        else:
            d = parse_number(args.value)
            if d != d.to_integral_value():
                raise ValueError("words without --amount needs a whole number")
            text = number_to_words(int(d), args.lakh_word)
        return text, {"result": text}
    if args.cmd == "date":
        text = format_gregorian(args.date, not args.no_weekday, args.ordinal, args.digits)
        return text, {"result": text, "iso": args.date.isoformat()}
    if args.cmd == "bangabda":
        text = format_bangabda(args.date, args.ordinal, not args.no_era, args.weekday, args.digits)
        return text, {"result": text, "iso": args.date.isoformat(), **bangabda(args.date)}
    if args.cmd == "phone":
        info = [normalize_bd_mobile(t) for t in args.text]
        return [i[args.style] for i in info], {"results": info}
    text = format_time(args.time, args.style, args.digits)
    return text, {"result": text}


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text, data = run(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("\n".join(text) if isinstance(text, list) else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
