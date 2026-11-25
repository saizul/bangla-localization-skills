---
name: bangla-number-date-format
description: Format numbers, money and dates for Bangla (bn-BD) correctly - Bangla digits (০-৯) and back, lakh/crore grouping (১২,৩৪,৫৬৭), compact হাজার/লক্ষ/কোটি, BDT/taka amounts (৳ ১,২৩,৪৫৬.০০, টাকা), amounts in words for invoices and cheques (এক লক্ষ ... টাকা মাত্র), Gregorian dates with Bangla month and weekday names, ordinal dates (২১শে ফেব্রুয়ারি), the Bangla calendar (Bangabda, revised Bangladesh calendar: ১লা বৈশাখ ১৪৩৩) 12-hour time with সকাল/দুপুর/বিকাল/রাত, and Bangladeshi mobile numbers (+880 E.164). Includes a deterministic CLI, reference tables and Intl/ICU/PHP/Python/WordPress code patterns. Use when the user needs Bangla number, currency, taka, date, calendar, Pohela Boishakh or time formatting, converts between Bangla and English digits, parses Bangla numeric input, or asks why Intl output differs.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/bn_format.py.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla numbers, currency and dates

Produce exact, conventional Bangla formatting, and wire the same rules into the user's code.
Never format by hand in the answer: run the script, or the platform API, and show the result.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- Display prices in taka, invoices, receipts, cheque amounts in words
- Bangla digits in UI, or converting user input typed with Bangla digits
- Dates on Bangla pages: Gregorian with Bangla names, or the Bangla calendar (বঙ্গাব্দ)
- "Why does `Intl.NumberFormat('bn')` give ১২,৩৪,৫৬৭ and not 1,234,567?"

## When not to use

- Translating UI text: use `bangla-ui-translation`
- West Bengal (India) Bangla calendar dates: the script implements the revised Bangladesh
  civil calendar only; the Indian calendar is based on astronomical rules and can differ by a day
- Hijri dates (Islamic calendar): use an Islamic-calendar library (`Intl` with `-u-ca-islamic`)

## Workflow

1. **Decide the conventions with the user** (defaults in brackets):
   - Digits: Bangla `০-৯` or Latin `0-9` [Bangla for Bangla UI, Latin for codes, IDs, phone
     numbers and anything users copy into other systems].
   - Grouping: lakh/crore `12,34,567` [default in Bangladesh] or international `1,234,567`.
   - Currency: `৳ ১,২৩,৪৫৬.০০` symbol first [common on Bangladeshi sites], `১,২৩,৪৫৬ টাকা` in
     prose, `BDT 1,23,456.00` for invoices and banking.
   - Dates: Gregorian with Bangla month names [default], Bangla calendar where culturally
     expected (Pohela Boishakh, newspapers, government notices: often both).
2. **Format with the script** (deterministic; `--json` for machine-readable output):
   ```bash
   python3 scripts/bn_format.py number 1234567.5 --decimals 2      # ১২,৩৪,৫৬৭.৫০
   python3 scripts/bn_format.py number 125000000 --compact         # ১২.৫ কোটি
   python3 scripts/bn_format.py currency 123456                     # ৳ ১,২৩,৪৫৬.০০
   python3 scripts/bn_format.py currency 1500 --style word --decimals 0   # ১,৫০০ টাকা
   python3 scripts/bn_format.py words 123456.50 --amount            # এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন টাকা পঞ্চাশ পয়সা মাত্র
   python3 scripts/bn_format.py date 2026-02-21 --ordinal --no-weekday    # ২১শে ফেব্রুয়ারি ২০২৬
   python3 scripts/bn_format.py bangabda 2026-04-14 --ordinal       # ১লা বৈশাখ ১৪৩৩ বঙ্গাব্দ
   python3 scripts/bn_format.py time 15:45                          # বিকাল ৩:৪৫
   python3 scripts/bn_format.py parse "১২,৩৪,৫৬৭.৫০"                # 1234567.50
   python3 scripts/bn_format.py digits --to en "০১৭১১-২২৩৩৪৪"        # 01711-223344
   python3 scripts/bn_format.py phone "০১৭১১-২২৩৩৪৪" "+880 1911 223344"   # +8801711223344, +8801911223344
   python3 scripts/bn_format.py phone 01711223344 --style bn       # ০১৭১১-২২৩৩৪৪ (also: local, intl)
   ```
   Exit 2 means invalid input (for example a malformed number); report it, do not guess.
   Store phone numbers as E.164 (`+8801XXXXXXXXX`) and format them only for display. The
   `operator` field in `--json` output is the prefix's original operator; ported numbers may differ.
3. **Implement in code** with the platform's locale data where possible, using the patterns in
   [references/platform-apis.md](references/platform-apis.md) (JavaScript `Intl`, PHP `intl`,
   Python Babel, Django, WordPress filters). Use the script's output as the expected value in
   unit tests.
4. **Watch the traps** (details in [references/tables.md](references/tables.md)):
   - Store and compute with Latin digits and `Decimal`/integers in paisa; convert only for display.
   - Accept both digit scripts in inputs (phone, OTP, amount): normalize with `parse`/`digits --to en`.
   - CLDR's `bn` locale already uses Bangla digits and lakh grouping; add `-u-nu-latn` for Latin digits.
   - Do not translate digits inside URLs, code, version numbers, phone links (`tel:`), or IDs.
   - Bangla calendar: Pohela Boishakh is 14 April in Bangladesh; Falgun has 30 days in
     Gregorian leap years.
5. **Verify** a sample against the script, including edge cases: 0, negative, 99,99,999,
   1,00,00,000 (one crore), 29 February, 13/14 April, midnight.

## Output

- The formatted values (from the script), and the code that produces them in the user's stack.
- A short convention note the team can reuse, e.g.:
  `Prices: ৳ + NBSP + Bangla digits, lakh grouping, 2 decimals in cart, 0 decimals in listings.`
- Test cases (input -> expected string) produced by `scripts/bn_format.py`.
