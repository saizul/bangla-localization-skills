# Contributing to bangla-localization-skills

Thank you for helping! New rules, glossary terms, skills, fixes, real-world test cases and
clearer docs are all welcome. Native Bangla speakers reviewing the language content are
especially valuable.

- [Ways to contribute](#ways-to-contribute)
- [Good first issues](#good-first-issues)
- [Development setup](#development-setup)
- [Repository layout](#repository-layout)
- [Write a new skill](#write-a-new-skill)
- [Quality bar](#quality-bar)
- [Pull request process](#pull-request-process)

## Ways to contribute

| Size | Idea |
| --- | --- |
| 10 minutes | Fix a typo, add a glossary term, add a FAQ entry |
| 30 minutes | Add a spelling rule with a test, or a fixture that shows a false positive |
| 1-2 hours | Add a check or option to an existing script |
| Half a day | Write a new skill from the template |

Comment on an issue before you start so nobody else picks the same one.

## Good first issues

Each of these is self-contained and touches one script and its test file.

1. **bangla-spellcheck-style: more Academy rules.** Add 10 unambiguous corrections to
   `SPELLING` (with the reason), each with a test for the wrong and the right form.
2. **bangla-spellcheck-style: কি/কী hint.** Report `info` when `কি` is followed by a verb
   pattern typical of "what" questions (e.g. `কি করবেন`), with a low false-positive rate.
3. **bangla-ui-translation: Android `strings.xml`.** Load `<string>` and `<plurals>` from
   `values/strings.xml` and `values-bn/strings.xml` and reuse the parity checks.
4. **bangla-ui-translation: XLIFF 1.2/2.0.** Read `<source>`/`<target>` pairs.
5. **i18n-key-extraction: Svelte and Astro.** Add markup-text rules for `.astro` and test
   Svelte `{#if}` blocks.
6. **i18n-key-extraction: `--write-keys`.** Print a unified diff that wraps high-confidence
   JSX text in `t("key")` (diff only, never edit files).
7. **bangla-number-date-format: `--ordinal` numbers.** Add ১ম, ২য়, ৩য়, ৪র্থ, ৫ম ... ordinals
   (`ordinal` subcommand) with tests.
8. **bangla-number-date-format: number words for decimals.** `words 12.5` -> `বারো দশমিক পাঁচ`.
9. **bangla-text-normalization: HTML entities.** Decode `&#2476;` style entities in `fix`
   behind a `--html-entities` flag.
10. **bangla-typography-web: `size-adjust` hint.** Report `info` when a Bengali `@font-face`
    in a mixed-script stack has no `size-adjust`.
11. **bangla-seo-content: hreflang checker.** A script that reads several HTML files and
    reports non-reciprocal `hreflang` links and invalid codes (`BD`, `bn_BD`).
12. **wordpress-bangla-site: JS translations.** Report plugins with `block.json`/JS files but
    no `<domain>-bn_BD-*.json` translation files.
13. **New skill: `bangla-android-ios-strings`** (see the roadmap in the README).

## Development setup

```bash
git clone https://github.com/saizul/bangla-localization-skills.git
cd bangla-localization-skills
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

python tools/validate_skills.py   # SKILL.md frontmatter, sections, links, marketplace listing
ruff check . && ruff format --check .
pytest
```

To try your changes in Claude Code, either copy a skill to `~/.claude/skills/` or add your
checkout as a local marketplace:

```bash
claude plugin marketplace add ./bangla-localization-skills
claude plugin install bangla-localization-skills@bangla-localization-skills
```

For Codex, copy the skill folder to `~/.agents/skills/`.

## Repository layout

```
.claude-plugin/
  marketplace.json      marketplace + plugin entry listing every skill
  plugin.json           plugin manifest (name, version, author)
skills/<name>/
  SKILL.md              frontmatter + workflow (the part agents read)
  scripts/*.py          standalone helpers, Python 3.8+ stdlib only
  references/*.md       glossaries, rule tables, checklists loaded on demand
templates/skill/        copy this to start a new skill
tests/
  test_<skill>.py       one test module per skill
  fixtures/<skill>/     inputs for those tests (real Bangla text)
tools/validate_skills.py
```

## Write a new skill

1. Open a "New skill proposal" issue first so we can agree on scope.
2. Copy the template:
   ```bash
   cp -r templates/skill skills/my-new-skill
   mv skills/my-new-skill/scripts/your_script.py skills/my-new-skill/scripts/my_check.py
   ```
3. Edit `SKILL.md`:
   - `name` equals the folder name: lowercase letters, digits, single hyphens, max 64 chars.
   - `description` (max 1024 chars) says **what** it does with concrete keywords and **when**
     to use it, with a sentence starting "Use when ...". This text decides whether the agent
     picks the skill, so list the phrases users actually type (in English and Bangla terms).
   - Required sections: `## When to use`, `## When not to use`, `## Workflow`, `## Output`.
   - Workflow steps are imperative and numbered, with exact commands and decision points.
   - Keep it under 400 lines; move glossaries and rule tables to `references/`.
4. Write the script: `argparse` with a useful `--help`, `--json` output, exit codes
   0 (ok) / 1 (findings) / 2 (error), read-only by default, no network.
5. Add `tests/test_my_new_skill.py` and fixtures in `tests/fixtures/my-new-skill/`. Cover
   a "bad" input, a "good" input that produces no findings, edge cases and the CLI exit codes.
6. Add the skill to `.claude-plugin/marketplace.json` (`plugins[0].skills`), the README
   skills table, the table in `AGENTS.md` and `CHANGELOG.md` under "Unreleased".
7. Run the validator, ruff and pytest.

## Quality bar

- **Correct Bangla.** Follow Bangla Academy standard spelling unless the skill says
  otherwise; cite a source (dictionary, CLDR, official style guide) for new rules in the PR.
- **Low false positives.** A rule that flags correct words is worse than no rule. If a rule
  is often wrong, make it `info` or drop it. Add the counter-examples you checked as tests.
- **Deterministic where it matters.** If a step is "check this file for X" or "compute Y",
  write a script and test it rather than relying on the model.
- **Unicode hygiene.** In code, write ZWJ, ZWNJ, BOM and lone combining marks as `\uXXXX`
  escapes. Fixture files may contain them raw (they are test data); generate tricky ones
  from escapes so the bytes are exact.
- **Safe by default.** Scripts never rewrite files unless the user passes an explicit flag,
  and then they keep a backup.

## Pull request process

1. Fork, create a branch, make focused commits.
2. Make sure CI passes locally (validator, ruff, pytest).
3. Fill in the pull request template.
4. A maintainer reviews within a few days. Small, focused pull requests are merged fastest.

By contributing you agree that your contributions are licensed under the MIT License.
