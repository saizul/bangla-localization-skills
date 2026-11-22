# WordPress Bangla checklist

## Locale facts

- WordPress locale: `bn_BD` (Bangla, Bangladesh). HTML `lang` output: `bn-BD`.
- Bangla is left-to-right: no RTL stylesheet, no `is_rtl()` work.
- Plural forms in Bangla PO files: `nplurals=2; plural=(n != 1);`
- `WPLANG` in `wp-config.php` is ignored since WordPress 4.0; the site language is the
  `WPLANG` option in the database (set via Settings > General or WP-CLI).

## Where translation files live

| Component | Location (first match wins) |
| --- | --- |
| Core | `wp-content/languages/bn_BD.{l10n.php,mo}`, `admin-bn_BD.*`, `admin-network-bn_BD.*`, `continents-cities-bn_BD.*` |
| Plugin | `wp-content/languages/plugins/<domain>-bn_BD.{l10n.php,mo}`, then the plugin's Domain Path |
| Theme | `wp-content/languages/themes/<domain>-bn_BD.{l10n.php,mo}`, then `<theme>/languages/bn_BD.mo` |
| JS strings | `wp-content/languages/plugins/<domain>-bn_BD-<md5 of script path>.json` |
| Loco Translate custom | `wp-content/languages/loco/{plugins,themes}/` (survives updates) |

WordPress 6.5+ loads `.l10n.php` files before `.mo` (faster, opcache-friendly). WP-CLI's
`wp i18n make-php` creates them. Language packs from translate.wordpress.org include them.

## Setup commands (WP-CLI)

```bash
wp language core list --status=installed
wp language core install bn_BD --activate        # or: wp site switch-language bn_BD
wp language plugin install --all bn_BD
wp language theme install --all bn_BD
wp language plugin list --all                     # language packs per plugin
wp option get WPLANG                              # current site language
wp user update 1 --locale=en_US                   # keep one admin in English (optional)
```

Language packs are only available for plugins/themes translated on translate.wordpress.org
above the packaging threshold; the rest need local translations.

## Translating a custom theme or plugin

1. Every string uses `__()`, `_e()`, `esc_html__()`, `esc_attr__()`, `_x()`, `_n()` with the
   text domain equal to the slug (check with `i18n-key-extraction --text-domain <slug>`).
2. Theme: `load_theme_textdomain( 'slug', get_template_directory() . '/languages' );` (not
   needed for themes hosted on wordpress.org, but harmless). Plugin: `Text Domain:` and
   `Domain Path:` headers; since WordPress 4.6 plugins on wordpress.org load automatically.
3. Template: `wp i18n make-pot . languages/slug.pot --domain=slug`
4. Translate: Poedit, Loco Translate, or an editor; follow `bangla-ui-translation` and run its
   `check_placeholders.py languages/slug.pot languages/slug-bn_BD.po`.
5. Compile: `wp i18n make-mo languages/ && wp i18n make-php languages/`
6. JavaScript: `wp_set_script_translations( 'handle', 'slug', plugin_dir_path( __FILE__ ) . 'languages' );`
   then `wp i18n make-json languages/ --no-purge`.

## Multilingual (Bangla + English)

| Plugin | Model | Notes |
| --- | --- | --- |
| Polylang | separate post per language | Free core; language in URL (`/bn/`), outputs hreflang |
| WPML | separate post per language | Paid; string translation, WooCommerce Multilingual add-on |
| TranslatePress | translate on the front end | Free core; keeps one post, translations stored separately |

Common to all: translate menus, widgets, slugs, SEO titles and WooCommerce attributes;
decide whether Bangla or English is the default (`x-default`); never auto-redirect by IP.

## Bangla digits (optional)

WordPress keeps Latin digits even with `bn_BD`. To show Bangla digits in dates and formatted
numbers, add a must-use plugin (`wp-content/mu-plugins/bangla-digits.php`):

```php
<?php
/**
 * Plugin Name: Bangla digits
 * Description: Shows Bangla digits in dates and formatted numbers when the locale is bn_BD.
 */
function bd_bangla_digits( $text ) {
    return strtr( (string) $text, array(
        '0' => '০', '1' => '১', '2' => '২', '3' => '৩', '4' => '৪',
        '5' => '৫', '6' => '৬', '7' => '৭', '8' => '৮', '9' => '৯',
    ) );
}
add_action( 'init', function () {
    if ( 'bn_BD' !== determine_locale() || is_admin() || wp_is_json_request() ) {
        return;
    }
    add_filter( 'wp_date', 'bd_bangla_digits' );
    add_filter( 'date_i18n', 'bd_bangla_digits' );
    add_filter( 'number_format_i18n', 'bd_bangla_digits' );
} );
```

Test feeds, sitemaps, schema JSON-LD and `datetime` attributes afterwards: they must keep
ISO dates with Latin digits (most use `mysql2date`/`gmdate`, which the filters above do not touch).

## WooCommerce

- WooCommerce > Settings > General: Currency `Bangladeshi taka (৳)`, currency position
  (left with space is common: `৳ 1,500`), thousand separator `,`, decimals `0` or `2`.
- Lakh grouping (১,২৩,৪৫৬) needs a filter on `formatted_woocommerce_price`; see the
  `bangla-number-date-format` skill for the grouping function.
- Address fields: Bangladesh districts (জেলা) are available as states in WooCommerce;
  check that checkout labels are translated.
- Emails: WooCommerce emails use the site language (or the customer's language with a
  multilingual plugin); send a test order.

## Fonts

Enqueue a Bangla web font in the theme (or child theme):

```php
add_action( 'wp_enqueue_scripts', function () {
    wp_enqueue_style(
        'bangla-font',
        'https://fonts.googleapis.com/css2?family=Hind+Siliguri:wght@400;600&display=swap',
        array(),
        null
    );
} );
```

Self-hosting is better for privacy and speed; run `bangla-typography-web`'s linter on the
theme CSS.

## Slugs and search

- Bangla post titles produce Bangla slugs (`/মোবাইলের-দাম/`); set English or romanized slugs
  by hand if the site's URL rule says so (`bangla-seo-content`).
- Default WordPress search matches exact substrings; normalize content (`bangla-text-normalization`)
  so that visually identical words match.

## Final check

- [ ] `wp_lang_audit.py` shows no warnings
- [ ] Front end: home, single post, page, archive, search results, 404, comments form
- [ ] WooCommerce: product, cart, checkout, my account, order emails
- [ ] Admin (if editors use Bangla): dashboard, editor, media library
- [ ] `<html lang="bn-BD">` in the page source; hreflang correct on bilingual sites
- [ ] Updates do not wipe custom translations (stored in `languages/loco/` or a child theme)
