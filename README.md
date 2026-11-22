# bangla-localization-skills

[![CI](https://github.com/saizul/bangla-localization-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/saizul/bangla-localization-skills/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/saizul/bangla-localization-skills?sort=semver)](https://github.com/saizul/bangla-localization-skills/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Stars](https://img.shields.io/github/stars/saizul/bangla-localization-skills?style=social)](https://github.com/saizul/bangla-localization-skills/stargazers)

**Agent Skills that help Claude Code and Codex build Bangla (বাংলা) + English software and content correctly: natural translations, no broken placeholders, real Unicode, correct taka and dates.**

Eight skills for the jobs that come up in every Bangla project: translating UI strings,
finding hard-coded text, formatting numbers, BDT and the Bangla calendar, making Bangla
look right on the web, Bangla SEO, fixing broken Unicode, running WordPress in `bn_BD`, and
proofreading. Each skill is a step-by-step workflow plus a tested, standard-library-only
Python script, so the agent checks its own work instead of guessing.

- **Catches the bugs that ship.** `{নাম}` instead of `{name}`, `%১$s`, ICU plurals without
  `other`, lost `<b>` tags, mojibake (`à¦¬à¦¾à¦‚à¦²à¦¾`), Bijoy text, stray ZWJ, `|` as danda.
- **Real Bangla.** Bangla Academy spelling rules, formal/informal tone, lakh/crore grouping,
  the revised Bangladesh calendar (১লা বৈশাখ = 14 April), fonts like Noto Sans Bengali and Hind Siliguri.
- **Tested.** 180+ tests with real Bangla fixtures, run on Python 3.11-3.13 in CI.
- **No dependencies, no network.** Python 3.8+ standard library only. Scripts are read-only
  by default; anything that writes files is opt-in.

## Skills

| Skill | What it does | Try asking |
| --- | --- | --- |
| [bangla-ui-translation](skills/bangla-ui-translation/SKILL.md) | Translates UI strings to natural Bangla (glossary, tone, plurals, word order) and validates en vs bn JSON/ARB/PO/POT: keys, placeholders, ICU, tags, Plural-Forms | "Translate `locales/en.json` to Bangla and check the placeholders" |
| [i18n-key-extraction](skills/i18n-key-extraction/SKILL.md) | Finds hard-coded strings in JS/TS/JSX/Vue/Svelte, PHP/WordPress and Python, suggests keys, emits a catalog, flags missing WordPress text domains | "Which strings in `src/` are not translatable yet?" |
| [bangla-number-date-format](skills/bangla-number-date-format/SKILL.md) | Bangla digits, lakh/crore grouping, ৳/BDT, amounts in words, Bangla month/weekday names, ordinal dates, Bangabda calendar, Bangla time | "Show prices as ৳ ১,২৩,৪৫৬ and dates as ২১শে ফেব্রুয়ারি" |
| [bangla-typography-web](skills/bangla-typography-web/SKILL.md) | Font choice and pairing, stacks, line-height, font loading, conjunct test strings; CSS/HTML linter | "Bangla text on our site looks cramped and broken, fix the CSS" |
| [bangla-seo-content](skills/bangla-seo-content/SKILL.md) | Bangla keyword research (Bangla, Banglish, English), Banglish variant generator, titles, slugs, hreflang `bn-BD` | "Plan keywords for a Bangla recipe blog, including Banglish searches" |
| [bangla-text-normalization](skills/bangla-text-normalization/SKILL.md) | Fixes mojibake, NFC/nukta forms, অ+া, vowel-sign order, khanda ta, stray ZWJ/ZWNJ, danda; detects Bijoy text | "This CSV has gibberish where Bangla should be" |
| [wordpress-bangla-site](skills/wordpress-bangla-site/SKILL.md) | `bn_BD` setup with WP-CLI, translation coverage audit (.po/.mo/.l10n.php), multilingual plugins, Bangla digits, WooCommerce BDT | "Switch my WooCommerce site to Bangla and find what is still English" |
| [bangla-spellcheck-style](skills/bangla-spellcheck-style/SKILL.md) | Bangla Academy spelling checks, sadhu/cholito mixing, আপনি/তুমি tone, punctuation, safe auto-fix; style guide | "Proofread this Bangla article and keep the tone formal" |

## Install

### Claude Code: plugin marketplace (recommended)

```text
/plugin marketplace add saizul/bangla-localization-skills
/plugin install bangla-localization-skills@bangla-localization-skills
```

Or from your shell:

```bash
claude plugin marketplace add saizul/bangla-localization-skills
claude plugin install bangla-localization-skills@bangla-localization-skills
```

Plugin skills are namespaced, e.g. `/bangla-localization-skills:bangla-ui-translation`.
Claude also picks them up automatically when your request matches a skill's description.
Update later with `/plugin marketplace update bangla-localization-skills`.

### Claude Code: copy the skills

```bash
git clone https://github.com/saizul/bangla-localization-skills.git
# all projects (personal skills)
mkdir -p ~/.claude/skills && cp -r bangla-localization-skills/skills/* ~/.claude/skills/
# or just one project
mkdir -p .claude/skills && cp -r bangla-localization-skills/skills/bangla-ui-translation .claude/skills/
```

Each release also has one zip per skill and an all-skills zip under
[Releases](https://github.com/saizul/bangla-localization-skills/releases).

### Codex CLI

Codex reads skills from `~/.agents/skills` (all repositories) and `.agents/skills` in a
repository (from the current directory up to the repository root):

```bash
git clone https://github.com/saizul/bangla-localization-skills.git
mkdir -p ~/.agents/skills && cp -r bangla-localization-skills/skills/* ~/.agents/skills/
```

Codex also ships a `$skill-installer` skill that can install skills from a GitHub
repository; ask it to install from `saizul/bangla-localization-skills`. Skill locations and
the installer are described in the [Codex skills documentation](https://developers.openai.com/codex/skills);
check it if your Codex version behaves differently. [AGENTS.md](AGENTS.md) explains how
Codex and other agents should use these skills.

### Any other agent

The skills follow the open [Agent Skills format](https://agentskills.io/specification):
a folder with `SKILL.md` (YAML frontmatter + instructions), `scripts/` and `references/`.
Point your agent at the folder, or run the scripts yourself; every script has `--help`.

## Usage examples

```text
> Translate locales/en.json into Bangla for our grocery app. Formal tone.
  (Claude asks about digits and existing terms, writes bn.json with the glossary,
   runs check_placeholders.py, fixes the plural block it missed, reports 0 errors.)

> Our Next.js app still shows English on the checkout page in Bangla mode.
  (i18n-key-extraction finds 14 hard-coded strings, wraps them in t(), adds the keys
   to en.json, then bangla-ui-translation fills bn.json.)

> Import these 2,000 product names from the old ERP export; search does not find them.
  (bangla-text-normalization check: mojibake + precomposed য়; fix writes a clean CSV.)
```

Run the scripts directly too:

```bash
python3 skills/bangla-ui-translation/scripts/check_placeholders.py locales/en.json locales/bn.json
python3 skills/i18n-key-extraction/scripts/find_hardcoded.py src/ --min-confidence high
python3 skills/bangla-number-date-format/scripts/bn_format.py words 123456.50 --amount
python3 skills/bangla-number-date-format/scripts/bn_format.py bangabda 2026-04-14 --ordinal
python3 skills/bangla-typography-web/scripts/bn_css_lint.py static/css/
python3 skills/bangla-seo-content/scripts/banglish_variants.py "ভালোবাসার গল্প"
python3 skills/bangla-text-normalization/scripts/bn_normalize.py check content/
python3 skills/wordpress-bangla-site/scripts/wp_lang_audit.py /var/www/html
python3 skills/bangla-spellcheck-style/scripts/bn_style_check.py article.md --tone formal
```

```text
$ python3 skills/bangla-number-date-format/scripts/bn_format.py words 123456.50 --amount
এক লক্ষ তেইশ হাজার চারশত ছাপ্পান্ন টাকা পঞ্চাশ পয়সা মাত্র

$ python3 skills/bangla-seo-content/scripts/banglish_variants.py "ভালোবাসার গল্প" --max 4
ভালোবাসার গল্প: bhalobasar golpo, bhalobasar galpo, valobasar golpo, bhalobasar golp
```

## How skills work

At startup the agent loads only each skill's `name` and `description` (about 100 tokens
each). When your request matches a description, it reads that skill's `SKILL.md`: the
workflow, decision points and output format. Longer material (glossaries, rule tables,
checklists) lives in `references/` and is read only when a step needs it. Scripts run as
normal commands, so their output is exact and repeatable.

```
skills/<skill-name>/
  SKILL.md          frontmatter (name, description) + workflow
  scripts/          standalone Python 3 helpers (stdlib only, --help, --json)
  references/       glossaries, rule tables, checklists, code patterns
```

## FAQ

**Does this replace a human translator or proofreader?**
No. The skills make the agent follow the conventions a good Bangla localizer follows and
catch mechanical errors with scripts. For published content, have a fluent reviewer read it.

**Which spelling standard?**
Bangla Academy standard spelling (প্রমিত বাংলা বানান), as used by most Bangladeshi
textbooks, newspapers and government offices. The checker only flags common, unambiguous
cases; you can extend the rule list.

**Bangladesh or West Bengal?**
Defaults target Bangladesh (`bn-BD`, BDT, the revised Bangladesh calendar). Most rules apply
to all Bangla; the calendar and currency parts note where India differs.

**Does anything leave my machine?**
No. No script makes network calls or sends telemetry.

**Can it convert Bijoy (SutonnyMJ) text to Unicode?**
It detects Bijoy text and explains how to convert it with a dedicated converter, then cleans
up the converter's output. A full Bijoy converter is on the roadmap.

**Why does the checker say `{নাম}` is an error?**
Placeholder names are code. The app passes `name`, not `নাম`, so the string would show
`{নাম}` literally or throw.

## Roadmap

Ideas for new skills and features (great first contributions; see [CONTRIBUTING.md](CONTRIBUTING.md)):

- `bangla-android-ios-strings` - `strings.xml` / `.strings` / `.xcstrings` parity checks and plural rules
- `bijoy-to-unicode` - a tested converter for SutonnyMJ text with a conjunct table
- `bangla-transliteration` - Avro-style phonetic Banglish to Bangla (reverse of the variant generator)
- `bangla-voice-and-tts` - SSML and pronunciation hints for Bangla text-to-speech
- `bangla-email-sms-templates` - SMS length with Unicode (70-char segments), OTP and transactional templates
- `bangla-accessibility` - screen reader checks for `lang`, number reading, abbreviations
- `bangla-legal-gov-forms` - NID, address and date conventions for Bangladeshi forms
- `bangla-sort-collation` - alphabetical order (বর্ণানুক্রম) and ICU collation for Bangla lists

## Contributing

Contributions are welcome: new rules, glossary terms, skills, fixes and better docs. Read
[CONTRIBUTING.md](CONTRIBUTING.md) for the skill template, the quality bar and how to run
the validator and tests:

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt
python tools/validate_skills.py && ruff check . && ruff format --check . && pytest
```

Please follow the [Code of Conduct](CODE_OF_CONDUCT.md) and report security issues
privately as described in [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE) (c) Saizul Amin
