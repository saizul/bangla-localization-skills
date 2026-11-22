# Bangla Unicode notes

The Bengali block is U+0980-U+09FF. Text is stored in logical (spoken) order; the font
reorders glyphs for display.

## Equivalent sequences

| Looks like | Forms | NFC result |
| --- | --- | --- |
| ড় | U+09DC, or U+09A1 U+09BC | U+09A1 U+09BC (U+09DC is a composition exclusion) |
| ঢ় | U+09DD, or U+09A2 U+09BC | U+09A2 U+09BC |
| য় | U+09DF, or U+09AF U+09BC | U+09AF U+09BC |
| ো (o-kar) | U+09CB, or U+09C7 U+09BE | U+09CB |
| ৌ (au-kar) | U+09CC, or U+09C7 U+09D7 | U+09CC |

So NFC turns precomposed ড় ঢ় য় into two code points, and composes ো and ৌ. NFD and NFKD
decompose all of them. Pick one normalization form for storage and comparison; NFC is the
web default (W3C recommends NFC for web content).

## Sequences that are not equivalent but look alike

| Wrong | Right | Why it happens |
| --- | --- | --- |
| অ + া | আ | some keyboards/fonts let users build আ from parts |
| ে + ক (e-kar first) | ক + ে | visual-order typing (legacy habits, some old converters) |
| ি + ক | ক + ি | same, for i-kar |
| চ + ঁ + া | চ + া + ঁ | chandrabindu typed before the vowel sign |
| ক + া + ় | ক + ় + া | nukta typed after the vowel sign |
| ত + ্ + ZWJ | ৎ (U+09CE) | khanda ta before Unicode 4.1 |
| ‌ ‍ at word boundaries | (nothing) | copy/paste from PDFs and some editors |
| `|` (U+007C) | `।` (U+0964) | no danda key on the keyboard |
| ৰ (U+09F0), ৱ (U+09F1) | র (U+09B0), ব (U+09AC) | Assamese letters picked by mistake |

## ZWJ and ZWNJ in Bangla

| Sequence | Meaning | Keep? |
| --- | --- | --- |
| র + ZWJ + ্ + য | ra + ya-phala (র‍্যাব, র‍্যাংকিং), instead of reph + ya | yes |
| র + ্ + য | reph + ya (কার্য, সূর্য) | (no joiner) |
| consonant + ্ + ZWNJ | visible hasanta, no conjunct (ক্‌) | yes |
| consonant + ্ + ZWJ | half form / non-stacked conjunct (font dependent) | yes |
| ZWJ/ZWNJ anywhere else | no effect, breaks search and matching | remove |

The script keeps exactly the "yes" cases.

## Mojibake signatures

| You see | What happened | Fix |
| --- | --- | --- |
| `à¦¬à¦¾à¦‚à¦²à¦¾` | UTF-8 bytes shown as Windows-1252/Latin-1 | `bn_normalize.py fix` (re-decodes) |
| `Ã Â¦Â¬` | double mis-decoding | run `fix` twice, check each step |
| `???? ????` | text saved through a non-Unicode charset | not recoverable; get the original |
| `�` (U+FFFD) | invalid bytes replaced on decode | not recoverable from this copy |
| `&#2476;&#2494;` | HTML numeric entities | decode entities (`html.unescape`) first |
| `বা` | JSON/JS escapes shown literally | decode as JSON, not as text |

## Normalizing in code

```python
import unicodedata

clean = unicodedata.normalize("NFC", text)
```

```js
const clean = text.normalize("NFC");
```

```php
$clean = Normalizer::normalize($text, Normalizer::FORM_C);   // intl extension
```

```sql
-- MySQL: store as utf8mb4 with a Unicode collation
ALTER TABLE posts CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

`utf8mb4_unicode_ci` and similar collations may treat some Bangla sequences as equal and
others not; normalize before writing so equality does not depend on the collation.

## Search tips

- Normalize both the index and the query (NFC) and strip ZWJ/ZWNJ for matching.
- Optionally fold variants for search only (not for display): ী -> ি, ূ -> ু,
  ণ -> ন, ষ/শ -> স, and precomposed ড় ঢ় য় -> their NFC form. This catches common spelling variants (বাড়ী/বাড়ি).
- Treat Bangla and Latin digits as equal in search.
