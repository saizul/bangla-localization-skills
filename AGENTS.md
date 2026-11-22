# AGENTS.md

Guidance for Codex CLI and other coding agents that use or work on this repository.

## Using the skills

The skills live in `skills/<name>/SKILL.md` and follow the Agent Skills format. Codex
discovers them when they are copied to `~/.agents/skills/` or `.agents/skills/` (see
README "Install"). If you are reading this file inside the repository instead:

1. Pick the skill whose `description` matches the user's request:

   | Request is about | Skill |
   | --- | --- |
   | translating UI strings, `bn.json`, `.po`, placeholder/ICU errors | `bangla-ui-translation` |
   | hard-coded strings, adding i18n, WordPress text domains | `i18n-key-extraction` |
   | Bangla digits, taka/BDT, lakh/crore, dates, Bangla calendar, time | `bangla-number-date-format` |
   | Bangla fonts, CSS, broken conjuncts on screen, font loading | `bangla-typography-web` |
   | Bangla SEO, keywords, Banglish, hreflang, slugs | `bangla-seo-content` |
   | gibberish/mojibake, Bijoy text, dotted circles, ZWJ/ZWNJ, NFC | `bangla-text-normalization` |
   | WordPress or WooCommerce in Bangla, `bn_BD`, .po/.mo loading | `wordpress-bangla-site` |
   | proofreading, spelling, tone (আপনি/তুমি), sadhu/cholito | `bangla-spellcheck-style` |

   Typical chains: `i18n-key-extraction` -> `bangla-ui-translation` -> `bangla-spellcheck-style`;
   `bangla-text-normalization` before any other skill when the text itself is broken.
2. Read that `SKILL.md` completely and follow its Workflow section in order.
3. Paths such as `scripts/x.py` and `references/y.md` are relative to the skill folder.
   `${CLAUDE_SKILL_DIR}` in the text means that folder; Codex does not expand it.
4. Read files in `references/` only when a workflow step points to them.

## Rules (apply to every skill)

- Run the read-only scripts freely. Ask before anything that rewrites the user's files in
  bulk (`--in-place`, overwriting catalogs) or runs WP-CLI against a live site; show the
  report or the command first.
- Never translate placeholders, keys, HTML attributes or code. Validate translation files
  with `bangla-ui-translation/scripts/check_placeholders.py` before handing them back.
- Use scripts for deterministic answers (formatting, calendar dates, checks) instead of
  writing Bangla numbers or dates by hand.
- Mark generated or unverified data (for example Banglish keyword variants) as such; never
  present it as search volume or as a verified translation.
- Do not send user text to third-party services unless the user asks.

## Working on this repository

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python tools/validate_skills.py   # frontmatter, sections, links, marketplace listing
ruff check . && ruff format --check .
pytest
```

- Scripts: Python 3.8+ standard library only, `#!/usr/bin/env python3`, `argparse` with
  `--help`, `--json` where output is structured, exit 0/1/2 (ok / findings / error).
- In Python source, write invisible characters (ZWJ U+200D, ZWNJ U+200C, BOM) and lone
  combining marks (hasanta U+09CD, vowel signs) as `\uXXXX` escapes; keep whole Bangla words
  readable.
- Every script needs tests in `tests/test_<skill_with_underscores>.py` with fixtures in
  `tests/fixtures/<skill>/`. Use real, correct Bangla in fixtures; never commit secrets or
  personal data.
- Keep each `SKILL.md` under 400 lines; move detail to `references/`.
- A new skill must be added to `.claude-plugin/marketplace.json` (`plugins[0].skills`), the
  README table, the table above and `CHANGELOG.md`. The validator enforces the manifest.
