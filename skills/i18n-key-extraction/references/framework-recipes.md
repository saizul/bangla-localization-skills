# Framework recipes: wrapping strings and adding a Bangla locale

Use the project's existing library. These are minimal, current patterns; check the library's
own documentation for the version the project uses.

## React with react-i18next

```tsx
import { useTranslation, Trans } from "react-i18next";

function CartTitle({ count }: { count: number }) {
  const { t } = useTranslation();
  return (
    <>
      <h2>{t("cart.title")}</h2>
      <p>{t("cart.items", { count })}</p>
      <Trans i18nKey="cart.terms" components={{ link: <a href="/terms" /> }} />
    </>
  );
}
```

```json
{
  "cart": {
    "title": "Your cart",
    "items_one": "{{count}} item",
    "items_other": "{{count}} items",
    "terms": "By ordering you accept our <link>terms</link>."
  }
}
```

i18next uses suffix keys (`_one`, `_other`) for plurals. For Bangla the `bn.json` needs
`items_one` and `items_other` (Bangla has only these two categories), usually with the same text.

## Next.js with next-intl

```tsx
import { useTranslations } from "next-intl";

export default function Hero() {
  const t = useTranslations("hero");
  return <h1>{t("title", { name: "Rahim" })}</h1>;
}
```

Messages use ICU syntax: `"title": "Welcome, {name}"`. Add `bn` to the locales list in the
routing config and create `messages/bn.json`.

## FormatJS / react-intl

```tsx
<FormattedMessage id="profile.title" defaultMessage="Your profile" />
intl.formatMessage({ id: "cart.items" }, { count })
```

`defaultMessage` literals are skipped by the scanner. Extract with `formatjs extract`.

## Vue with vue-i18n

```vue
<template>
  <button :title="$t('nav.logout_hint')">{{ $t("nav.logout") }}</button>
</template>
```

Plurals: `"apples": "no apples | one apple | {count} apples"` with `$t('apples', count)`
(vue-i18n's pipe syntax), or ICU via a custom message compiler.

## WordPress (PHP)

```php
<h2><?php esc_html_e( 'Latest news', 'bd-news' ); ?></h2>
<input placeholder="<?php echo esc_attr__( 'Search…', 'bd-news' ); ?>">
<?php
printf(
    /* translators: %s: number of comments */
    esc_html( _n( '%s comment', '%s comments', $count, 'bd-news' ) ),
    esc_html( number_format_i18n( $count ) )
);
```

- The text domain must equal the plugin/theme slug and the `Text Domain:` header.
- Add a `/* translators: */` comment above strings with placeholders.
- Generate the template: `wp i18n make-pot . languages/bd-news.pot`.
- JavaScript in blocks: `import { __ } from '@wordpress/i18n';` plus
  `wp_set_script_translations( 'handle', 'bd-news', $path )` and `wp i18n make-json`.

## Laravel

```php
{{ __('Your cart is empty') }}            // JSON catalog: lang/bn.json
{{ __('cart.empty') }}                    // PHP catalog: lang/bn/cart.php
{{ trans_choice('cart.items', $count) }}  // "{1} :count item|[2,*] :count items"
```

Laravel placeholders are `:name`; check them with
`check_placeholders.py en.json bn.json --extra-pattern ':[a-z_]+'`.

## Django

```python
from django.utils.translation import gettext_lazy, ngettext


class Order(models.Model):
    status = models.CharField(gettext_lazy("status"), max_length=20)


def view(request):
    msg = ngettext("%(count)d item", "%(count)d items", count) % {"count": count}
```

Templates: `{% load i18n %}{% translate "Checkout" %}` and `{% blocktranslate %}`.
Create the catalog with `django-admin makemessages -l bn` and compile with `compilemessages`.
`LANGUAGES` needs `("bn", "বাংলা")`.

## Flask (Flask-Babel)

```python
from flask_babel import gettext as _, lazy_gettext as _l

flash(_("Your order has been placed"))
```

`pybabel extract -F babel.cfg -o messages.pot . && pybabel init -i messages.pot -d translations -l bn`.

## Key naming conventions

- `area.element_purpose`: `checkout.place_order`, `cart.empty_title`, `errors.network_offline`.
- One key per meaning, even if the English text repeats ("Post" verb vs "Post" noun: use
  context in gettext with `_x()` / `pgettext()`).
- Never reuse keys for different screens just because the English matches; Bangla may need
  different words.

## Locale codes

| Use | Code |
| --- | --- |
| BCP 47 (HTML `lang`, Intl, i18next, next-intl) | `bn` or `bn-BD` (Bangladesh), `bn-IN` (India) |
| gettext / WordPress / POSIX | `bn_BD`, `bn_IN` |
| Android resources | `values-bn`, `values-bn-rBD` |
| Apple (.lproj) | `bn.lproj` |
