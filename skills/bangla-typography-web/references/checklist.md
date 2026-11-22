# Bangla typography checklist

## Text and markup

- [ ] Content is Unicode Bangla (U+0980-U+09FF), not Bijoy/ANSI (check with `bangla-text-normalization`)
- [ ] `<meta charset="utf-8">` first in `<head>`
- [ ] `<html lang="bn">` (or `bn-BD`); English passages marked `lang="en"`
- [ ] No images of text for headlines that need to be searchable or translatable

## Fonts

- [ ] Every text font stack contains a Bengali-capable font before the generic family
- [ ] Self-hosted WOFF2 (or Google Fonts with `&display=swap`)
- [ ] `font-display: swap` (body) or `optional` (if layout shift matters more than the brand font)
- [ ] Bengali `@font-face` has `unicode-range: U+0980-09FE, U+200C-200D, U+25CC, U+0964-0965;`
- [ ] Only 2-3 weights loaded; bold text has a real bold face
- [ ] One body weight preloaded: `<link rel="preload" href="/fonts/x-400.woff2" as="font" type="font/woff2" crossorigin>`
- [ ] `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>` when using Google Fonts
- [ ] Subsets: Google Fonts serves split files by `unicode-range` automatically; when
      self-hosting, keep the whole Bengali block in one file (conjunct shaping needs all glyphs
      and the font's shaping tables; never subset by "characters used on the page" with tools
      that drop GSUB/GPOS)

## Spacing and layout

- [ ] Body `line-height` 1.6-1.8; headings 1.3-1.45 (vowel signs ি ী ু ূ ৃ and reph need room)
- [ ] Body text at least 16px (Bangla looks smaller than Latin at the same size)
- [ ] No `letter-spacing` on Bangla text (it breaks the headstroke and, in some browsers,
      disables ligatures that conjuncts depend on); reset with `:lang(bn) { letter-spacing: normal; }`
- [ ] No `text-transform` reliance for emphasis (Bangla has no case)
- [ ] No faux italic: `:lang(bn) em { font-style: normal; font-weight: 600; }`
- [ ] `text-align: start` rather than `justify` for body text (no Bangla hyphenation in browsers)
- [ ] `word-break: normal` + `overflow-wrap: anywhere` (never `break-all`)
- [ ] Buttons and table headers tested with Bangla strings 20-40% longer than English
- [ ] Underlines: `text-underline-offset: 0.25em` so links do not cut through descending vowel signs

## Test strings

Paste these into the page and compare browsers. Each line exercises a different shaping
feature.

```text
ক্ষ জ্ঞ ঞ্চ ঞ্জ ন্ত্র স্ত্র ক্ত হ্ম ষ্ণ ঙ্ক ন্ধ ত্ত দ্ধ শ্চ          conjuncts
কৃষক হৃদয় রুপি রূপ শু হু গু ত্রু দ্রু                          u/ri vowel-sign variants
কর্ম ধর্ম সূর্য কার্যালয় র্ক র্ত র্ধ                              reph
র‍্যাব র‍্যাংকিং                                                   ra + ya-phala (র + ZWJ + ্ + য)
প্রশ্ন ক্রিকেট গ্রাম ব্যবসা দ্বিতীয় স্বাস্থ্য                     ra-phala, ya-phala, ba-phala
কি কী কু কূ কে কৈ কো কৌ                                   all vowel signs on one consonant
হঠাৎ বিদ্যুৎ সংবাদ দুঃখ চাঁদ                                       khanda ta, anusvara, visarga, chandrabindu
আমার সোনার বাংলা, আমি তোমায় ভালোবাসি।                          sentence with danda
১২,৩৪,৫৬৭.৮৯ ৳ ২১শে ফেব্রুয়ারি ২০২৬                            digits, taka sign, ordinal
English and বাংলা mixed in one line, 2026 and ২০২৬                mixed script baseline
```

What to look for: dotted circles (◌) before vowel signs (broken sequence or missing font),
vowel signs floating away from their consonant, conjuncts shown as letter + visible hasanta
(্) where a stacked form is expected, reph drawn on the wrong letter, clipped tops of ি/ী or
bottoms of ু/ূ/ৃ at small line-heights, and baseline jumps in mixed lines.

## Performance budget

- [ ] Total font bytes on first view under ~250 KB on mobile
- [ ] No render-blocking `@import` of Google Fonts inside CSS
- [ ] CLS from font swap checked (use `size-adjust` / `ascent-override` to match fallback metrics)
