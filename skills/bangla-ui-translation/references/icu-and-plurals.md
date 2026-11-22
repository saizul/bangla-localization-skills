# ICU, plurals and placeholders in Bangla

## Plural categories

CLDR defines two cardinal plural categories for Bengali (`bn`):

| Category | Matches | Example values |
| --- | --- | --- |
| `one` | integer part 0, or n = 1 | 0, 1, 0.5 |
| `other` | everything else | 2, 3, 10, 1.5 |

Bangla nouns do not inflect for number after a numeral (১টি বই, ৫টি বই), so both branches
are normally the same. You still need `other`, and you may keep `one` to mirror the source.
Categories such as `zero`, `two`, `few` and `many` never match in Bangla; use exact matches
(`=0`) when the product wants special text for zero.

```text
en: {count, plural, =0 {No messages} one {# message} other {# messages}}
bn: {count, plural, =0 {কোনো বার্তা নেই} one {#টি বার্তা} other {#টি বার্তা}}
```

`#` is replaced by the formatted number. With a `bn` locale the ICU runtime formats it with
Bangla digits (০-৯) by default; use the `-u-nu-latn` locale extension (`bn-BD-u-nu-latn`) if
the product wants Latin digits.

### Ordinals (selectordinal)

Bangla ordinals are words or suffixes (১ম, ২য়, ৩য়, ৪র্থ, ৫ম ... ; প্রথম, দ্বিতীয়). Unless the
product already uses `selectordinal`, prefer separate messages or a lookup table; check the
CLDR ordinal rules for `bn` in your runtime before relying on specific categories.

## gettext

```po
"Plural-Forms: nplurals=2; plural=(n != 1);\n"
```

This is what WordPress and most Bangla PO files use. `msgstr[0]` is used for n = 1 and
`msgstr[1]` for everything else. Both usually contain the same Bangla text:

```po
msgid "%s comment"
msgid_plural "%s comments"
msgstr[0] "%sটি মন্তব্য"
msgstr[1] "%sটি মন্তব্য"
```

Keep the number placeholder in `msgstr[0]` even if the English singular says "One comment":
Bangla readers expect the digit, and gettext passes the number to both forms.

## select (gender and other enums)

তিনি (he/she, formal) and তাঁরা (they, formal) are gender-neutral, and Bangla verbs do not
agree with gender. A gender `select` can collapse to `other`:

```text
en: {gender, select, male {He replied} female {She replied} other {They replied}}
bn: {gender, select, other {তিনি উত্তর দিয়েছেন}}
```

The checker reports dropped options as a warning, not an error, for this reason.

## Word order and positional placeholders

Bangla is subject-object-verb. Sentences with two or more values often need reordering.
Use positional placeholders and reorder them; never reorder by changing the code.

| English | Bangla |
| --- | --- |
| `Uploaded %1$s of %2$s files` | `%2$sটির মধ্যে %1$sটি ফাইল আপলোড হয়েছে` |
| `{user} liked your {item}` | `{user} আপনার {item} পছন্দ করেছেন` |
| `Showing {from}-{to} of {total}` | `{total}টির মধ্যে {from}-{to} দেখানো হচ্ছে` |

If the source uses non-positional `%s %s` and Bangla needs a different order, ask the
developer to switch to `%1$s %2$s` first (in PHP and C both are supported by printf).

## Case endings attached to placeholders

Possessive and locative endings attach to the value: `{name}-এর`, `{city}-তে`. Because the
ending depends on the last sound of the value (`রহিমের` but `ঢাকার`), a hyphenated form
(`{name}-এর`) or a rephrase (`{name} নামের ব্যবহারকারী`) is safer than guessing.

## Formatting values

- Numbers, dates and currency should be formatted by the code (Intl, ICU, Babel), not
  written into the translation. See the `bangla-number-date-format` skill.
- Do not put Bangla digits into translation strings for values that come from code.
