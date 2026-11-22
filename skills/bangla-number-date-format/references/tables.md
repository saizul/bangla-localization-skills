# Reference tables

## Digits

| Latin | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bangla | ০ | ১ | ২ | ৩ | ৪ | ৫ | ৬ | ৭ | ৮ | ৯ |
| Code point | U+09E6 | U+09E7 | U+09E8 | U+09E9 | U+09EA | U+09EB | U+09EC | U+09ED | U+09EE | U+09EF |

Decimal separator `.`, group separator `,` in both scripts. Python's `int("১২৩")` and
JavaScript's `Number()` behave differently: Python accepts Unicode digits, JavaScript does
not. Always normalize to Latin digits before parsing.

## Grouping (South Asian system)

| Value | Lakh/crore | Words |
| --- | --- | --- |
| 1,000 | ১,০০০ | এক হাজার |
| 1,00,000 | ১,০০,০০০ | এক লক্ষ (লাখ) |
| 10,00,000 | ১০,০০,০০০ | দশ লক্ষ |
| 1,00,00,000 | ১,০০,০০,০০০ | এক কোটি |
| 1,00,00,00,000 | ১,০০,০০,০০,০০০ | একশত কোটি |

Rule: the last three digits form one group, then groups of two. Above a crore the count of
crores is grouped the same way (১২,৩৪৫ কোটি). লক্ষ is the formal spelling (used on cheques and
in government documents); লাখ is common in speech and news.

## Currency

| Item | Value |
| --- | --- |
| ISO code | BDT |
| Symbol | ৳ (U+09F3 BENGALI RUPEE SIGN, used as the taka sign) |
| Unit | টাকা (taka), 1 taka = 100 পয়সা (poisa) |
| Common display | `৳ ১,২৩,৪৫৬.০০`, `৳১,২৩,৪৫৬`, `১,২৩,৪৫৬ টাকা`, `Tk 1,23,456`, `BDT 1,23,456.00` |
| Cheque / invoice words | `এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন টাকা মাত্র` |
| Legacy suffix | `/-` after whole amounts (`১,৫০০/-`), still seen on invoices |

Use a non-breaking space (U+00A0) between ৳ and the number so they never wrap apart.

## Number words 1-99

Bangla number words are irregular; each of 1-99 has its own form (the script lists all 100).
Some landmarks: ১১ এগারো, ১৯ উনিশ, ২১ একুশ, ২৯ ঊনত্রিশ, ৩৫ পঁয়ত্রিশ, ৪৮ আটচল্লিশ, ৫৫ পঞ্চান্ন,
৬৯ ঊনসত্তর, ৭১ একাত্তর, ৮৮ অষ্টাশি, ৯৯ নিরানব্বই. Hundreds: একশত, দুইশত ... নয়শত (colloquial:
একশো, দুশো). Spelling variants exist (ঊনত্রিশ / উনত্রিশ); the script uses one consistent set.

## Gregorian months

| # | Month | # | Month |
| --- | --- | --- | --- |
| 1 | জানুয়ারি | 7 | জুলাই |
| 2 | ফেব্রুয়ারি | 8 | আগস্ট |
| 3 | মার্চ | 9 | সেপ্টেম্বর |
| 4 | এপ্রিল | 10 | অক্টোবর |
| 5 | মে | 11 | নভেম্বর |
| 6 | জুন | 12 | ডিসেম্বর |

## Weekdays

| English | Bangla |
| --- | --- |
| Sunday | রবিবার |
| Monday | সোমবার |
| Tuesday | মঙ্গলবার |
| Wednesday | বুধবার |
| Thursday | বৃহস্পতিবার |
| Friday | শুক্রবার |
| Saturday | শনিবার |

Bangladesh's weekend is Friday and Saturday; week pickers usually start on Saturday or Sunday.

## Ordinal date suffixes

| Day | Suffix | Example |
| --- | --- | --- |
| 1 | -লা | ১লা বৈশাখ |
| 2, 3 | -রা | ২রা, ৩রা |
| 4 | -ঠা | ৪ঠা |
| 5-18 | -ই | ৫ই, ১৬ই ডিসেম্বর |
| 19-31 | -শে | ২১শে ফেব্রুয়ারি, ২৬শে মার্চ |

Plain digits without suffix (২১ ফেব্রুয়ারি) are also correct and simpler in UI.

## Bangla calendar (Bangabda, revised Bangladesh calendar)

Bangladesh revised the calendar in 1987 and again from 1426 BS (2019) so that national days
fall on fixed Gregorian dates. Year = Gregorian year - 593 from 14 April, otherwise - 594.

| # | Month | Days | Starts (Gregorian) | Season (ঋতু) |
| --- | --- | --- | --- | --- |
| 1 | বৈশাখ | 31 | 14 April | গ্রীষ্ম |
| 2 | জ্যৈষ্ঠ | 31 | 15 May | গ্রীষ্ম |
| 3 | আষাঢ় | 31 | 15 June | বর্ষা |
| 4 | শ্রাবণ | 31 | 16 July | বর্ষা |
| 5 | ভাদ্র | 31 | 16 August | শরৎ |
| 6 | আশ্বিন | 31 | 16 September | শরৎ |
| 7 | কার্তিক | 30 | 17 October | হেমন্ত |
| 8 | অগ্রহায়ণ | 30 | 16 November | হেমন্ত |
| 9 | পৌষ | 30 | 16 December | শীত |
| 10 | মাঘ | 30 | 15 January | শীত |
| 11 | ফাল্গুন | 29 (30 in a Gregorian leap year) | 14 February | বসন্ত |
| 12 | চৈত্র | 30 | 15 March | বসন্ত |

Checks: ২১শে ফেব্রুয়ারি = ৮ ফাল্গুন, ২৬শে মার্চ = ১২ চৈত্র, ১৬ই ডিসেম্বর = ১ পৌষ,
১৪ই এপ্রিল = ১লা বৈশাখ (Pohela Boishakh, পহেলা বৈশাখ).

West Bengal and other Indian states follow the traditional (sidereal) calendar: Pohela
Boishakh is usually 14 or 15 April there and month lengths vary by year.

## Parts of the day

| Hours | Word | Example |
| --- | --- | --- |
| 04-06 | ভোর | ভোর ৫টা |
| 06-12 | সকাল | সকাল ১০:৩০ |
| 12-15 | দুপুর | দুপুর ১টা |
| 15-18 | বিকাল (বিকেল) | বিকাল ৪টা |
| 18-20 | সন্ধ্যা | সন্ধ্যা ৭টা |
| 20-04 | রাত | রাত ১১টা, রাত ১২:৩০ |

Boundaries vary by speaker; these are the common ones. For schedules and tickets, a 24-hour
clock (১৫:৪৫) or "বিকাল ৩:৪৫" both work; never use AM/PM translated literally (পূর্বাহ্ণ/অপরাহ্ণ
is formal and used mostly in official notices).
