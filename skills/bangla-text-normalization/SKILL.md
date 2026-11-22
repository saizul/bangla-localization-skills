---
name: bangla-text-normalization
description: Detect and repair broken Bangla (Bengali) Unicode text - mojibake (UTF-8 read as Windows-1252, "à¦¬à¦¾à¦‚à¦²à¦¾" -> বাংলা), legacy Bijoy/SutonnyMJ ANSI text, NFC normalization (decomposed ো/ৌ, nukta letters ড় ঢ় য় precomposed vs decomposed), অ+া typed instead of আ, vowel signs typed before the consonant, chandrabindu/nukta order, old khanda-ta encoding, stray ZWJ/ZWNJ/BOM/ZWSP (keeping র‍্য), duplicated signs, '|' used as danda, mixed Bangla/Latin digits, dotted circles and orphan vowel signs. Use when Bangla text shows gibberish, boxes or dotted circles, search/string matching fails for identical-looking words, data was imported from old Word/Excel/Bijoy files or a database with the wrong charset, or before indexing, deduplicating or comparing Bangla text.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/bn_normalize.py.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla text normalization

Identical-looking Bangla words can be different code point sequences, and imported text is
often mis-decoded or not Unicode at all. Normalize before you store, search, compare,
translate or render.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- Text looks like `à¦†à¦®à¦¿` or `Avwg evsjvq Mvb MvB`
- Dotted circles (◌া), vowel signs on the wrong letter, conjuncts broken only in some data
- `"বাড়ি" == "বাড়ি"` is false; search misses words that are clearly there; duplicates in a DB
- Cleaning content before import (CSV, Excel, scraped pages, old CMS, PO/JSON catalogs)

## When not to use

- Rendering problems with valid Unicode (fonts, CSS): use `bangla-typography-web`
- Spelling mistakes (সরকারী vs সরকারি): use `bangla-spellcheck-style`
- Full Bijoy-to-Unicode conversion: this skill detects Bijoy text and explains conversion
  ([references/bijoy-legacy.md](references/bijoy-legacy.md)) but does not convert it

## Workflow

1. **Check first (read-only):**
   ```bash
   python3 scripts/bn_normalize.py check content/*.md locales/bn.json
   python3 scripts/bn_normalize.py check export.csv --json
   ```
   Exit 1 means something would change or needs attention. The report lists fix counts by
   code (`mojibake`, `nfc`, `a-aa`, `prebase-order`, `mark-order`, `khanda-ta`, `zero-width`,
   `duplicate-sign`, `danda`, `digits`) and notes that need a human (`bijoy`, `replacement`,
   `dotted-circle`, `orphan-sign`, `assamese`, `mixed-digits`).
2. **Decide the policy with the user:**
   - Nukta letters: NFC (two code points, default; what most normalizers and search engines
     produce) or `--nukta precomposed` (one code point, if an existing database uses it).
     Whatever you pick, use the same form everywhere you compare strings.
   - Digits: leave as is, or `--digits bn` / `--digits en` for a consistent dataset.
3. **If notes say `bijoy`:** the text is in the legacy ANSI encoding. Follow
   [references/bijoy-legacy.md](references/bijoy-legacy.md) to convert it with a dedicated
   converter, then come back to step 1.
4. **If notes say `replacement` (`???`, `�`):** the characters were destroyed earlier (for
   example a latin1 database column). They cannot be recovered from this text; find the
   original source or re-export with UTF-8 (`utf8mb4` in MySQL).
5. **Fix:**
   ```bash
   python3 scripts/bn_normalize.py fix post.txt > post.fixed.txt      # stdout, safe
   python3 scripts/bn_normalize.py fix locales/bn.json --in-place     # keeps locales/bn.json.bak
   python3 scripts/bn_normalize.py fix data.csv --digits en --nukta precomposed > clean.csv
   ```
   Ask before `--in-place` on files under version control or shared data; show the check
   report first.
6. **Verify:** run `check` on the output (it must exit 0 or only show notes the user
   accepted), and diff a few lines. For catalogs, re-run `bangla-ui-translation`'s
   `check_placeholders.py` to confirm placeholders survived.
7. **Prevent recurrence:** normalize to NFC at input boundaries (forms, imports, APIs), store
   UTF-8 (`utf8mb4`), and compare/search on normalized text. Patterns per language are in
   [references/unicode-notes.md](references/unicode-notes.md).

## Output

- The check report (counts per fix code, notes with line numbers).
- The fixed text or the list of rewritten files (with `.bak` backups).
- Policy decisions (NFC vs precomposed nukta, digit script) and the snippet to normalize
  at the application boundary.
