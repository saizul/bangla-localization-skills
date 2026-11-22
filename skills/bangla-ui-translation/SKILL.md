---
name: bangla-ui-translation
description: Translate software UI strings from English to natural, consistent Bangla (bn / bn-BD) while preserving placeholders ({name}, {{count}}, %s, %1$s, %(name)s), ICU plural/select blocks, HTML/JSX tags and keys, then validate en vs bn JSON, ARB, PO or POT files with a parity checker (missing/stale keys, changed placeholders, translated placeholder names, broken ICU, lost tags, Bangla digits inside %১$s, untranslated strings, wrong Plural-Forms). Use when the user asks to translate an app, website, i18n JSON, locale file, .po/.pot, WordPress or React/Vue/Next.js strings into Bangla/Bengali, review an existing bn translation, or fix broken placeholders after translation.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/check_placeholders.py.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla UI translation

Translate interface text into Bangla that reads like it was written in Bangla, and prove with
a script that nothing the code depends on (keys, placeholders, tags, plural syntax) changed.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- "Translate `locales/en.json` to Bangla", "make a `bn.json`", "fill in `bn_BD.po`"
- Reviewing an existing Bangla translation for quality or broken placeholders
- An app crashes or shows `{name}` / `%s` literally after a Bangla translation was added
- Building a Bangla glossary or style rules for a product

## When not to use

- Finding strings that are still hard-coded in source: use `i18n-key-extraction` first
- Long-form articles, marketing copy and SEO pages: use `bangla-seo-content` and
  `bangla-spellcheck-style` (this skill is for short UI strings)
- Number/date/currency formatting in code: use `bangla-number-date-format`
- Text that renders as boxes or broken conjuncts: use `bangla-text-normalization` and
  `bangla-typography-web`

## Workflow

1. **Collect context before translating.**
   - File format (i18next JSON, react-intl/FormatJS ICU, vue-i18n, next-intl, Flutter ARB, gettext PO).
   - Audience and tone: default to formal আপনি with -উন imperatives (সংরক্ষণ করুন) for apps,
     banking, government and e-commerce. Use তুমি only when the brand voice is explicitly casual.
   - Existing glossary or earlier translations; read them and stay consistent.
   - Ask whether digits should be Bangla (০-৯) or Latin in UI text. Default: Bangla digits in
     prose, but never inside placeholders.
2. **Translate with these rules** (details and a 130-term glossary in
   [references/glossary.md](references/glossary.md)):
   - Keep every key, placeholder, tag and ICU keyword byte-for-byte: `{name}` stays `{name}`,
     never `{নাম}`; `%1$s` never `%১$s`; `{count, plural, ...}` keeps `plural`, `one`, `other`, `#`.
   - Translate the text inside ICU branches and between tags; move placeholders and tags to
     where Bangla word order needs them (`Uploaded %1$s of %2$s` -> `%2$sটির মধ্যে %1$sটি আপলোড হয়েছে`).
   - Plurals: Bangla nouns do not change after numbers, so the `one` and `other` branches are
     usually identical (`#টি পণ্য`). Always keep `other`. Do not add `few`/`many`; Bangla has only
     `one` and `other` ([references/icu-and-plurals.md](references/icu-and-plurals.md)).
   - Attach classifiers directly: `{count}টি`, `%dজন`, `%s টাকা`.
   - Buttons and menu items are verbs in polite imperative: Save -> সংরক্ষণ করুন, Delete ->
     মুছে ফেলুন. Short labels may drop the verb (Settings -> সেটিংস).
   - Use the danda `।` for sentences, never `.` or `|`. Keep `?` and `!`.
   - Prefer words Bangladeshi users actually use: common English loanwords (অ্যাকাউন্ট, পাসওয়ার্ড,
     ডাউনলোড) beat obscure Sanskritised coinages. Keep brand and product names as they are.
   - Gender: তিনি/তাঁরা are gender-neutral; a `select` on gender can map male/female to the same text.
3. **Write the Bangla file** with the same structure and key order as the source.
4. **Validate (mandatory, read-only):**
   ```bash
   python3 scripts/check_placeholders.py locales/en.json locales/bn.json
   python3 scripts/check_placeholders.py languages/bn_BD.po          # msgid vs msgstr
   python3 scripts/check_placeholders.py app.pot languages/bn_BD.po  # also missing/stale entries
   python3 scripts/check_placeholders.py en.json bn.json --json --fail-on warning
   python3 scripts/check_placeholders.py en.json bn.json --extra-pattern ':[a-z_]+'  # Laravel :name
   ```
   Exit 1 means at least one finding at or above `--fail-on` (default `error`).
5. **Fix every error**, then re-run until it exits 0. Treat warnings (missing keys,
   untranslated, fuzzy) as a to-do list for the user, not silent passes.
6. **Polish:** run `bangla-spellcheck-style` on the Bangla file for spelling (সরকারি, not
   সরকারী), register and tone consistency.
7. **Compile if needed:** for gettext, `msgfmt -c -o bn_BD.mo bn_BD.po` (or `wp i18n make-mo`).

## Decision points

- **Error `placeholder`:** restore the exact English placeholder. If the message says the
  name is in Bangla, someone translated the variable name.
- **Error `icu` (no `other`):** add an `other` branch; ICU throws at runtime without it.
- **Warning `icu` (select drops an option):** fine when Bangla uses the same word (তিনি), as
  long as `other` exists.
- **Warning `untranslated`:** acceptable for brand names, codes, `OK`, `URL`; otherwise translate.
- **Info `punctuation`:** replace a final `.` with `।`.

## Output

1. The Bangla file (or a diff), with the same keys and structure as the source.
2. The checker summary, for example:
   ```
   0 error(s), 2 warning(s), 0 info
   WARNING untranslated  brand.name: Bangla value is identical to English   (intended: brand name)
   ```
3. A short list of terminology decisions (e.g. "Checkout -> চেকআউট, kept as loanword") so
   the user can add them to their glossary.
