# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-11-22

### Added

- `bangla-ui-translation`: workflow, 100+ term UI glossary, ICU/plural guide and
  `check_placeholders.py` for en/bn JSON, ARB, PO and POT parity (keys, ICU, i18next,
  printf, tags, Plural-Forms, translated placeholder names, Bangla digits in `%১$s`).
- `i18n-key-extraction`: `find_hardcoded.py` for JS/TS/JSX/TSX/Vue/Svelte, PHP/WordPress
  and Python (ast), key suggestions, JSON catalog skeleton, WordPress text-domain checks;
  framework recipes.
- `bangla-number-date-format`: `bn_format.py` for Bangla digits, lakh/crore grouping,
  compact units, BDT, amounts in words, Gregorian dates in Bangla, ordinal dates, the revised
  Bangladesh calendar (Bangabda) and Bangla time; reference tables and platform API notes.
- `bangla-typography-web`: `bn_css_lint.py` for font stacks, font loading, line-height,
  letter-spacing and other Bangla CSS traps; font guide and checklist with test strings.
- `bangla-seo-content`: `banglish_variants.py` romanized keyword variants and a Bangla SEO
  guide (search behaviour, titles, slugs, hreflang, structured data).
- `bangla-text-normalization`: `bn_normalize.py` check/fix for mojibake, NFC/nukta forms,
  অ+া, vowel-sign order, khanda ta, ZWJ/ZWNJ, danda and digits; Bijoy detection; Unicode notes.
- `wordpress-bangla-site`: offline `wp_lang_audit.py` for `bn_BD` coverage (.po/.mo/.l10n.php,
  plugins, themes, locale names, WPLANG) and a setup checklist.
- `bangla-spellcheck-style`: `bn_style_check.py` with Bangla Academy spelling rules,
  register mixing, tone, punctuation and digit checks; spelling rules and tone guide.
- Claude Code plugin marketplace manifest, `tools/validate_skills.py`, CI and release workflows.

[Unreleased]: https://github.com/saizul/bangla-localization-skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/saizul/bangla-localization-skills/releases/tag/v0.1.0
