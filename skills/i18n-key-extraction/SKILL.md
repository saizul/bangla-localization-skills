---
name: i18n-key-extraction
description: Find hard-coded user-facing strings (English or Bangla) in JavaScript, TypeScript, JSX/TSX, Vue, Svelte, PHP/WordPress templates and Python/Django/Flask code, suggest stable translation keys, emit a JSON catalog skeleton, and wrap the strings in the project's i18n calls (react-i18next t(), next-intl, vue-i18n $t(), FormatJS, WordPress __()/esc_html__() with text domain, gettext _()). Also flags WordPress translation calls with a missing or wrong text domain. Use when the user wants to internationalize or localize an app, prepare a codebase for Bangla/bn-BD or any second language, asks "which strings are not translatable", "extract strings", "add i18n", or sees English text left in a translated UI.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/find_hardcoded.py. Heuristic for JS/PHP, ast-based for Python.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# i18n key extraction

Make a codebase translatable: find the strings users see, give them keys, move them into a
catalog and replace them with translation calls, without breaking the code.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- "Add i18n / Bangla support to this React (Next.js, Vue, Laravel, WordPress, Django) app"
- "Find hard-coded strings", "which texts are not translated yet?"
- English (or hard-coded Bangla) text still shows after switching the UI language
- WordPress theme/plugin review: missing text domains, echo of raw strings

## When not to use

- Translating an existing catalog: use `bangla-ui-translation`
- Choosing an i18n library from scratch for a large app (discuss architecture first)
- Generated, vendored or minified code (`node_modules`, `vendor`, `dist` are skipped)

## Workflow

1. **Identify the i18n setup.** Look for `i18next`, `react-intl`, `next-intl`, `vue-i18n`,
   `@lingui`, `gettext`, `django.utils.translation`, `flask_babel`, WordPress `load_*_textdomain`,
   Laravel `lang/`. If none exists, propose one (see
   [references/framework-recipes.md](references/framework-recipes.md)) and get a yes first.
2. **Scan (read-only).**
   ```bash
   python3 scripts/find_hardcoded.py src/
   python3 scripts/find_hardcoded.py src/ --min-confidence high          # JSX text, attributes, alerts, Bangla
   python3 scripts/find_hardcoded.py wp-content/themes/mytheme --text-domain mytheme
   python3 scripts/find_hardcoded.py app/ --json > hardcoded.json
   python3 scripts/find_hardcoded.py src/ --emit-catalog locales/en.extracted.json
   ```
   Confidence: `high` = JSX/HTML text, UI attributes (placeholder, title, alt, aria-label,
   label), alert/confirm/toast, echo/print, any Bangla text; `medium` = prose-like literals;
   `low` = single capitalised words (`Save`). Default shows medium and up. Tests, stories and
   logger calls are skipped unless `--include-tests` / `--include-logs`.
3. **Triage with the user.** Group findings by file. Drop false positives (CSS classes, log
   messages, enum values, analytics event names). Exceptions shown to users count as UI text;
   internal exceptions do not.
4. **Choose keys.** The script suggests `namespace.slug` from the file name and first words
   (`checkout_form.place_order`). Keep the project's existing convention if there is one.
   Keys describe meaning, not position (`cart.empty_title`, not `page2.text3`).
5. **Edit the code** file by file, showing the diff. Rules:
   - Wrap whole sentences, never fragments joined with `+`. Turn concatenation into
     placeholders: `"Hello " + name` -> `t("greeting", { name })` / `"Hello, {name}"`.
   - Use the library's plural support for counts, not `count === 1 ? ... : ...`.
   - JSX with markup inside a sentence: use `<Trans>` (react-i18next) or rich-text formatting
     (FormatJS/next-intl), not split strings.
   - WordPress: `esc_html__( 'Text', 'domain' )` for output, `esc_attr__()` in attributes,
     `_n()` for plurals, `_x()` when context is needed, `sprintf()` with `%1$s` for values.
   - Python: `_()`/`gettext()`; lazy variants (`gettext_lazy`) for module-level strings in Django.
6. **Write the catalog.** Merge the extracted English strings into the source locale file
   (`en.json`, `.pot` via `wp i18n make-pot` / `xgettext` / `pybabel extract`). Then create
   the Bangla file with `bangla-ui-translation`.
7. **Verify.** Re-run the scan: the findings you handled should be gone. Build and run the
   tests. Switch the app to `bn` and look at the changed screens.

## Output

- A findings table: file:line, confidence, text, suggested key (or the JSON report).
- The code changes as diffs, grouped per file.
- The new or updated source catalog (`en.json` / `.pot`) and the list of keys added.
- Remaining items the user must decide on (ambiguous strings, false positives kept on purpose).
