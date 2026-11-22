# Platform APIs for Bangla formatting

Locale data comes from CLDR. Output can differ slightly between CLDR versions (browser, ICU
and Babel versions), so pin expectations in tests to what your runtime produces and use
`scripts/bn_format.py` to cross-check the conventions (digits, grouping, month names).

## Locale identifiers

| Want | BCP 47 locale |
| --- | --- |
| Bangla, Bangladesh, Bangla digits | `bn-BD` (or `bn`) |
| Bangla text, Latin digits | `bn-BD-u-nu-latn` |
| English text, lakh/crore grouping, Latin digits | `en-IN` |
| Bangla, India | `bn-IN` |

## JavaScript (Intl)

```js
const n = new Intl.NumberFormat("bn-BD");
n.format(1234567.5);                        // Bangla digits, lakh grouping

new Intl.NumberFormat("bn-BD-u-nu-latn").format(1234567.5);   // Latin digits, lakh grouping

// Currency: CLDR's bn pattern places the sign after the number. If the design wants
// "৳ ১,২৩,৪৫৬.০০", format the number and prefix the sign yourself:
const taka = (v) =>
  "৳\u00a0" + new Intl.NumberFormat("bn-BD", { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v);

new Intl.NumberFormat("bn-BD", { notation: "compact" }).format(12500000);  // compact (CLDR wording)

new Intl.DateTimeFormat("bn-BD", { dateStyle: "full" }).format(new Date(2026, 1, 21));
new Intl.DateTimeFormat("bn-BD", { hour: "numeric", minute: "2-digit" }).format(new Date());

new Intl.PluralRules("bn").select(1);   // "one"
new Intl.PluralRules("bn").select(2);   // "other"

// Parse user input that may contain Bangla digits
const toLatin = (s) => s.replace(/[০-৯]/g, (d) => "০১২৩৪৫৬৭৮৯".indexOf(d));
Number(toLatin("১২,৩৪৫").replace(/,/g, ""));   // 12345
```

Compact notation wording (হা, লা, কো abbreviations or full words) depends on the CLDR version;
when the exact wording matters, use your own formatter (see the script's `--compact`).

The Bangla calendar is not an `Intl` calendar; compute it (port `bangabda()` from the script:
it is a dozen lines with no dependencies).

## PHP (intl extension)

```php
$fmt = new NumberFormatter('bn_BD', NumberFormatter::DECIMAL);
echo $fmt->format(1234567.5);

$cur = new NumberFormatter('bn_BD', NumberFormatter::CURRENCY);
echo $cur->formatCurrency(123456, 'BDT');

$latn = new NumberFormatter('bn_BD@numbers=latn', NumberFormatter::DECIMAL);

$date = new IntlDateFormatter('bn_BD', IntlDateFormatter::FULL, IntlDateFormatter::NONE, 'Asia/Dhaka');
echo $date->format(new DateTime('2026-02-21'));

// Digit conversion without intl
$bn = strtr('2026', ['0'=>'০','1'=>'১','2'=>'২','3'=>'৩','4'=>'৪','5'=>'৫','6'=>'৬','7'=>'৭','8'=>'৮','9'=>'৯']);
```

## Python

```python
# Babel (pip install babel)
from babel.numbers import format_decimal, format_currency
from babel.dates import format_date

format_decimal(1234567.5, locale="bn_BD")
format_currency(123456, "BDT", locale="bn_BD")
format_date(date(2026, 2, 21), format="full", locale="bn_BD")

# Standard library only: copy the functions you need from scripts/bn_format.py
# (to_bn_digits, group_indian, format_currency, amount_in_words, bangabda).
```

Django: with `USE_L10N` behaviour (always on since Django 5.0) and `LANGUAGE_CODE = "bn"`,
template number formatting uses Django's own `bn` format files, which may not convert digits.
Convert digits explicitly in a template filter if the design requires Bangla digits.

## WordPress

WordPress's `bn_BD` translation supplies Bangla month and weekday names to `date_i18n()` /
`wp_date()`. Digits stay Latin unless you convert them. A small mu-plugin:

```php
<?php
// wp-content/mu-plugins/bangla-digits.php
function bd_bangla_digits( $text ) {
    return strtr( (string) $text, array(
        '0' => '০', '1' => '১', '2' => '২', '3' => '৩', '4' => '৪',
        '5' => '৫', '6' => '৬', '7' => '৭', '8' => '৮', '9' => '৯',
    ) );
}
if ( 'bn_BD' === get_locale() ) {
    add_filter( 'wp_date', 'bd_bangla_digits' );
    add_filter( 'date_i18n', 'bd_bangla_digits' );
    add_filter( 'number_format_i18n', 'bd_bangla_digits' );
}
```

Do not filter values that end up in URLs, `datetime` attributes, schema.org JSON-LD or
feeds: those must stay ISO 8601 with Latin digits.

WooCommerce: currency BDT has the symbol ৳; set position and separators under
WooCommerce > Settings > General. WooCommerce uses one thousand separator, so lakh
grouping needs a `wc_price`/`formatted_woocommerce_price` filter if you want it.

## Databases, APIs and storage

- Store amounts as integers in paisa or as DECIMAL; never as formatted strings.
- Store dates in ISO 8601 / UTC; format at the edge with time zone `Asia/Dhaka` (UTC+6, no DST).
- Accept Bangla digits on input (forms, OTP, phone numbers) and normalize to Latin before
  validation; many Bangladeshi users type with Bangla keyboards (Avro, Bijoy layouts, phone IMEs).
