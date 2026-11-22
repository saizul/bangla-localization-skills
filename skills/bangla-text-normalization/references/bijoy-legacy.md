# Bijoy (ANSI) legacy text

## What it is

Before Unicode was widespread, most Bangla in Bangladesh was typed with the Bijoy keyboard
and displayed with ANSI fonts such as SutonnyMJ. The file stores Latin-1/Windows-1252
characters; the font draws Bangla shapes in their place. Without that font the text reads as
gibberish, and to search engines, screen readers, spell checkers and databases it is gibberish.

| Bijoy text (as stored) | Unicode Bangla |
| --- | --- |
| `Avwg evsjvq Mvb MvB` | আমি বাংলায় গান গাই |
| ``Avgvi †`k evsjv‡`k`` | আমার দেশ বাংলাদেশ |
| `Ges` | এবং |
| `Kiv` | করা |

Tell-tale signs: words like `Avwg`, `evsjv`, `Ges`, `Kiv`, `Rb¨`, `nq`; characters `†`, `‡`,
`¨`, `©`, `Ö`, `ˆ` inside words; the document's font is SutonnyMJ or another "MJ" font.
`bn_normalize.py check` reports this as `bijoy`.

## How to convert

1. **Find the original document** (Word, Excel, InDesign). The safest conversion works on
   the original file with its fonts, because some ANSI fonts map characters differently.
2. **Use a dedicated Bijoy-to-Unicode converter.** Several free desktop tools and web
   converters exist. Converters are
   rule-based; results differ for rare conjuncts.
3. **Convert in small batches**, then run:
   ```bash
   python3 scripts/bn_normalize.py check converted.txt
   python3 scripts/bn_normalize.py fix converted.txt > converted.clean.txt
   ```
   Converters often leave visual-order vowel signs, `অ+া`, stray ZWJ/ZWNJ or `|` as danda;
   `fix` repairs those.
4. **Proofread** a sample with a fluent reader, especially conjuncts (ক্ষ, জ্ঞ, ন্ত্র, স্ত্র),
   reph (র্), ya-phala (্য) and ra-phala (্র). Then run `bangla-spellcheck-style`.
5. **Replace the font** in the template with a Unicode Bangla font (see `bangla-typography-web`).

## Mixed documents

Some documents mix Unicode and Bijoy paragraphs (copy/paste from different sources). Convert
only the Bijoy paragraphs: running a converter on Unicode text corrupts it. Split by paragraph
and use `bn_normalize.py check` on each piece if needed.

## Preventing new Bijoy text

- Ask writers to use a Unicode keyboard (Avro Phonetic, Bijoy in Unicode mode, Gboard,
  Ridmik) and a Unicode font.
- Reject or flag uploads where `check` reports `bijoy`.
