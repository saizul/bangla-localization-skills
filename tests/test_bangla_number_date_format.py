import datetime as dt
import json
from decimal import Decimal

import pytest

from conftest import load_script, run_script

SKILL = "bangla-number-date-format"
SCRIPT = "bn_format.py"
bf = load_script(SKILL, SCRIPT)
NBSP = " "


def test_digits_round_trip():
    assert bf.to_bn_digits("2026-11-22") == "২০২৬-১১-২২"
    assert bf.to_en_digits("০১৭১১-২২৩৩৪৪") == "01711-223344"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("১২,৩৪,৫৬৭.৫০", "1234567.50"),
        ("1,234,567", "1234567"),
        ("৳ ১,০০০/-", "1000"),
        ("১০০০ টাকা", "1000"),
        ("-৫০", "-50"),
        ("BDT 1,23,456.78", "123456.78"),
    ],
)
def test_parse(raw, expected):
    assert format(bf.parse_number(raw), "f") == expected


@pytest.mark.parametrize("raw", ["12,3,4", "abc", "", "১২.৩৪.৫"])
def test_parse_rejects(raw):
    with pytest.raises(ValueError):
        bf.parse_number(raw)


@pytest.mark.parametrize(
    "digits,expected",
    [
        ("1", "1"),
        ("123", "123"),
        ("1234", "1,234"),
        ("123456", "1,23,456"),
        ("1234567", "12,34,567"),
        ("123456789", "12,34,56,789"),
    ],
)
def test_group_indian(digits, expected):
    assert bf.group_indian(digits) == expected


def test_format_number():
    assert bf.format_number("1234567.5") == "১২,৩৪,৫৬৭.৫"
    assert bf.format_number("1234567.5", 2) == "১২,৩৪,৫৬৭.৫০"
    assert bf.format_number("1234567.555", 2, "en") == "12,34,567.56"
    assert bf.format_number("1234567", None, "en", "international") == "1,234,567"
    assert bf.format_number("-1500") == "-১,৫০০"


def test_compact():
    assert bf.format_compact("125000000") == "১২.৫ কোটি"
    assert bf.format_compact("5000000", lakh_word="লাখ") == "৫০ লাখ"
    assert bf.format_compact("150000") == "১.৫ লক্ষ"
    assert bf.format_compact("1500", digits="en") == "1.5 হাজার"
    assert bf.format_compact("999") == "৯৯৯"


def test_currency():
    assert bf.format_currency("123456") == f"৳{NBSP}১,২৩,৪৫৬.০০"
    assert bf.format_currency("1500", "word", decimals=0) == "১,৫০০ টাকা"
    assert bf.format_currency("1234567", "code", "en") == f"BDT{NBSP}12,34,567.00"
    assert bf.format_currency("-99.5", "symbol", space=False) == "-৳৯৯.৫০"


@pytest.mark.parametrize(
    "n,words",
    [
        (0, "শূন্য"),
        (21, "একুশ"),
        (99, "নিরানব্বই"),
        (100, "একশত"),
        (999, "নয়শত নিরানব্বই"),
        (1000, "এক হাজার"),
        (100000, "এক লক্ষ"),
        (123456, "এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন"),
        (10000000, "এক কোটি"),
        (1000000001, "একশত কোটি এক"),
        (-5, "ঋণাত্মক পাঁচ"),
    ],
)
def test_number_to_words(n, words):
    assert bf.number_to_words(n) == words


def test_ones_table_complete_and_unique():
    assert len(bf.ONES) == 100 and len(set(bf.ONES)) == 100


def test_amount_in_words():
    assert bf.amount_in_words("123456.50") == "এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন টাকা পঞ্চাশ পয়সা মাত্র"
    assert bf.amount_in_words("500000", lakh_word="লাখ") == "পাঁচ লাখ টাকা মাত্র"
    assert bf.amount_in_words(Decimal("0.75")) == "শূন্য টাকা পঁচাত্তর পয়সা মাত্র"
    with pytest.raises(ValueError):
        bf.amount_in_words("-1")


@pytest.mark.parametrize(
    "day,suffix",
    [(1, "লা"), (2, "রা"), (3, "রা"), (4, "ঠা"), (5, "ই"), (18, "ই"), (19, "শে"), (21, "শে"), (31, "শে")],
)
def test_ordinal_suffix(day, suffix):
    assert bf.ordinal_suffix(day) == suffix


def test_gregorian():
    assert bf.format_gregorian(dt.date(2026, 11, 22)) == "রবিবার, ২২ নভেম্বর ২০২৬"
    assert bf.format_gregorian(dt.date(2026, 2, 21), weekday=False, ordinal=True) == "২১শে ফেব্রুয়ারি ২০২৬"
    assert bf.format_gregorian(dt.date(2026, 12, 16), weekday=False, digits="en") == "16 ডিসেম্বর 2026"


@pytest.mark.parametrize(
    "iso,expected",
    [
        ("2026-04-14", (1433, "বৈশাখ", 1)),  # Pohela Boishakh
        ("2026-04-13", (1432, "চৈত্র", 30)),
        ("2026-02-21", (1432, "ফাল্গুন", 8)),  # International Mother Language Day
        ("2026-03-26", (1432, "চৈত্র", 12)),  # Independence Day
        ("2026-12-16", (1433, "পৌষ", 1)),  # Victory Day
        ("2026-10-17", (1433, "কার্তিক", 1)),
        ("2026-11-22", (1433, "অগ্রহায়ণ", 7)),
        ("2027-01-15", (1433, "মাঘ", 1)),
        ("2024-03-14", (1430, "ফাল্গুন", 30)),  # leap year: Falgun has 30 days
        ("2024-03-15", (1430, "চৈত্র", 1)),
        ("2025-03-15", (1431, "চৈত্র", 1)),  # non-leap: Falgun has 29 days
    ],
)
def test_bangabda_anchor_dates(iso, expected):
    b = bf.bangabda(dt.date.fromisoformat(iso))
    assert (b["year"], b["month_name"], b["day"]) == expected


def test_bangabda_full_year_is_continuous():
    d = dt.date(2027, 4, 14)
    prev = None
    total = 0
    while d < dt.date(2028, 4, 14):
        b = bf.bangabda(d)
        if prev:
            assert (b["month"], b["day"]) in ((prev["month"], prev["day"] + 1), (prev["month"] + 1, 1))
        prev = b
        d += dt.timedelta(days=1)
        total += 1
    assert total == 366 and prev["month"] == 12 and prev["day"] == 30  # Feb 2028 is a leap month


def test_format_bangabda():
    assert bf.format_bangabda(dt.date(2026, 4, 14), ordinal=True) == "১লা বৈশাখ ১৪৩৩ বঙ্গাব্দ"
    assert bf.format_bangabda(dt.date(2026, 4, 14), era=False, weekday=True) == "মঙ্গলবার, ১ বৈশাখ ১৪৩৩"
    assert bf.bangabda(dt.date(2026, 11, 22))["season"] == "হেমন্ত"


@pytest.mark.parametrize(
    "hm,clock,spoken",
    [
        ("05:10", "ভোর ৫:১০", "ভোর ৫টা ১০ মিনিট"),
        ("09:00", "সকাল ৯:০০", "সকাল ৯টা"),
        ("13:30", "দুপুর ১:৩০", "দুপুর ১টা ৩০ মিনিট"),
        ("15:45", "বিকাল ৩:৪৫", "বিকাল ৩টা ৪৫ মিনিট"),
        ("19:05", "সন্ধ্যা ৭:০৫", "সন্ধ্যা ৭টা ৫ মিনিট"),
        ("00:30", "রাত ১২:৩০", "রাত ১২টা ৩০ মিনিট"),
    ],
)
def test_time(hm, clock, spoken):
    t = dt.time(*map(int, hm.split(":")))
    assert bf.format_time(t) == clock
    assert bf.format_time(t, "spoken") == spoken


def test_cli():
    r = run_script(SKILL, SCRIPT, "currency", "123456")
    assert r.returncode == 0 and r.stdout.strip() == f"৳{NBSP}১,২৩,৪৫৬.০০"
    r = run_script(SKILL, SCRIPT, "--json", "bangabda", "2026-04-14")
    data = json.loads(r.stdout)
    assert data["year"] == 1433 and data["month_name"] == "বৈশাখ"
    r = run_script(SKILL, SCRIPT, "parse", "১২,৩৪,৫৬৭", "1,000")
    assert r.stdout.split() == ["1234567", "1000"]
    r = run_script(SKILL, SCRIPT, "date", "২০২৬-০২-২১", "--ordinal")
    assert r.stdout.strip() == "শনিবার, ২১শে ফেব্রুয়ারি ২০২৬"
    assert run_script(SKILL, SCRIPT, "number", "12,3,4").returncode == 2
    assert run_script(SKILL, SCRIPT, "words", "12.5").returncode == 2
    assert run_script(SKILL, SCRIPT, "time", "25:00").returncode == 2
    assert run_script(SKILL, SCRIPT, "--help").returncode == 0
