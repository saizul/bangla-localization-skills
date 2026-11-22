---
name: wordpress-bangla-site
description: Set up and audit a WordPress site in Bangla (locale bn_BD) - site and user language, core/plugin/theme translation files (.po, .mo, .l10n.php for WordPress 6.5+, JS .json), WP-CLI language commands, translating themes and plugins (text domains, make-pot, Loco Translate, Poedit), multilingual Bangla + English with Polylang, WPML or TranslatePress, Bangla digits in dates and numbers, WooCommerce BDT, Bangla fonts, slugs and hreflang (no RTL work needed: Bangla is left-to-right). Includes an offline audit script for translation coverage. Use when the user wants a Bangla WordPress or WooCommerce site, switches a site to bn_BD, finds English strings left in a Bangla theme or plugin, has .po/.mo files that do not load, or plans a bilingual Bangla/English WordPress site.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/wp_lang_audit.py (reads files only). WP-CLI commands need shell access to the WordPress host.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# WordPress Bangla site

Get every visible string on a WordPress site into Bangla, keep translations loading after
updates, and add Bangla-specific polish (digits, fonts, currency) without breaking SEO.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- New Bangla WordPress/WooCommerce site, or switching an existing site to `bn_BD`
- English strings still visible on a Bangla site; translations "not loading"
- Translating a custom theme or plugin into Bangla
- Bangla + English site with a multilingual plugin

## When not to use

- The translation text itself (quality, placeholders): `bangla-ui-translation`
- Hard-coded strings in a custom theme/plugin: `i18n-key-extraction` (with `--text-domain`)
- Fonts and CSS details: `bangla-typography-web`; SEO strategy: `bangla-seo-content`

## Workflow

1. **Audit offline first (read-only):**
   ```bash
   python3 scripts/wp_lang_audit.py /var/www/html
   python3 scripts/wp_lang_audit.py ./wp-content --json
   python3 scripts/wp_lang_audit.py . --min-percent 100 --fail-on info
   ```
   It lists core, every plugin and theme with its text domain and Bangla coverage, and flags
   missing translations, uncompiled or stale `.mo`, missing `.l10n.php`, wrongly named files
   (`bn.po` instead of `bn_BD.po`), bad Plural-Forms and the obsolete `WPLANG` constant.
   It never runs PHP or touches the database. With only a backup or a download of
   `wp-content`, it still works.
2. **Plan changes and get confirmation.** Every WP-CLI command below changes the live site;
   show the list first, suggest a staging copy or a backup (`wp db export`), then run them
   only after the user says yes.
3. **Install and activate Bangla** (see [references/checklist.md](references/checklist.md)):
   ```bash
   wp language core install bn_BD --activate
   wp language plugin install --all bn_BD
   wp language theme install --all bn_BD
   wp language core update && wp language plugin update --all && wp language theme update --all
   ```
   Or Settings > General > Site Language > বাংলা. Each user can keep English for wp-admin in
   their profile (Language), which is useful for admins who are not comfortable in Bangla.
4. **Fill the gaps** shown by the audit:
   - Plugin/theme from wordpress.org with < 100%: contribute on translate.wordpress.org or
     add a local override with Loco Translate (store custom translations in the "Custom"
     or "System" location so plugin updates do not overwrite them).
   - Custom theme/plugin: `wp i18n make-pot <dir> <dir>/languages/<domain>.pot`, translate to
     `<domain>-bn_BD.po` (`bangla-ui-translation`), then compile:
     `wp i18n make-mo <dir>/languages` and `wp i18n make-php <dir>/languages`.
   - Block/JS strings: `wp i18n make-json <dir>/languages --no-purge` and make sure the
     plugin calls `wp_set_script_translations()`.
5. **Bangla-specific polish** (snippets in the checklist): Bangla digits for dates/numbers
   via filters (optional), WooCommerce currency BDT (৳), a Bangla web font, `lang="bn"`
   is set automatically by `language_attributes()` once the site language is Bangla.
6. **Bilingual sites:** choose one plugin (Polylang, WPML or TranslatePress), give each
   language its own URL (`/bn/`, `/en/`), let the plugin output hreflang, translate menus,
   widgets, slugs and WooCommerce product data, and keep one default language for `x-default`.
7. **Verify:** re-run the audit (expect no warnings), browse the front page, a post, search,
   404, cart/checkout and account pages in Bangla, and check emails WooCommerce sends.

## Output

- The audit table (component, text domain, coverage) and findings with fixes.
- The exact commands run (or proposed) and their results.
- Remaining untranslated strings by component, and where each override lives.
