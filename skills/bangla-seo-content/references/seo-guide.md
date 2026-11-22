# Bangla SEO guide

## How Bangladeshi users search

| Pattern | Example | Notes |
| --- | --- | --- |
| Bangla script | মোবাইলের দাম, সরকারি চাকরির খবর | Growing fast with Bangla keyboards (Gboard, Ridmik, Avro) and voice search |
| Banglish (romanized) | mobile er dam, sorkari chakrir khobor | Very common on phones; spellings vary wildly |
| English with local modifier | samsung price in bd, bkash cash out charge | Typical for products, finance, tech |
| Mixed | iphone 15 er dam koto, ঢাকা to cox's bazar bus | Treat as the same intent as the Bangla form |
| Voice | ঢাকায় আজকের আবহাওয়া কেমন | Full questions, Bangla script |

### Banglish spelling variation

The same word is typed many ways. The main axes (the script generates combinations of these):

| Sound | Variants | Example |
| --- | --- | --- |
| ভ | bh, v | bhalo / valo |
| শ, ষ, স | sh, s | shari / sari, desh / des |
| inherent vowel | o, a, dropped | kolom / kalom; sorkari / sarkari |
| ী, ূ | i/ee, u/oo | eid / id, doodh / dudh |
| জ, য | j, z | namaj / namaz |
| ফ | f, ph | fon / phone |
| ছ | ch, chh | chobi / chhobi |
| ড়, ঢ় | r, d, rh | bari / badi, porashona / podashona |
| possessive এর | er, ar, separate or joined | mobile er / mobiler |

Google often treats close variants as the same query, but not reliably for low-volume
Banglish. Target the main variants in titles/FAQs only when real data shows demand.

### Keyword modifiers that matter in Bangladesh

- Price: দাম, মূল্য, price in bd, dam koto
- Location: ঢাকা, চট্টগ্রাম, সিলেট, near me, এলাকার নাম (মিরপুর, উত্তরা, ধানমন্ডি)
- Quality: সেরা, ভালো, best, top 10
- How-to: কীভাবে, কিভাবে (both spellings are searched), নিয়ম, পদ্ধতি
- Time: ২০২৬, আজকের, সর্বশেষ, update
- Jobs/education: নিয়োগ বিজ্ঞপ্তি, সার্কুলার, রেজাল্ট, ভর্তি
- Payments: বিকাশ, নগদ, রকেট (brand names written in Bangla by users)

### Where to find demand data

Google Search Console (queries already reaching the site, including Banglish), Google
autocomplete and People also ask with a Bangladesh location, Google Trends (country:
Bangladesh, compare Bangla vs Banglish forms), the user's keyword tool. Third-party tools
often under-report Bangla-script volumes; treat their zeros with suspicion.

## Writing

- Use standard চলিত Bangla with Bangla Academy spelling (run `bangla-spellcheck-style`).
- Answer first, then explain. Short paragraphs (2-4 sentences); Bangla text in long blocks
  is tiring on mobile.
- Headings as questions users ask ("বিকাশে ক্যাশ আউট চার্জ কত?").
- Keep English technical terms people actually use (ইউএসবি, ওয়াই-ফাই, অ্যাপ) and add the
  English in parentheses on first use if users search both ways: স্মার্টফোন (smartphone).
- Digits: be consistent within a page. Prices, phone numbers and model numbers are often
  searched with Latin digits; Bangla digits in body text are fine.
- Machine-translated pages rank poorly and hurt trust; always have a fluent reviewer.

## Titles and meta descriptions

Google truncates by pixel width (~600 px for titles on desktop). Bangla glyphs with matras
and conjuncts are wider than Latin, so aim for:

| Element | Bangla target | Example |
| --- | --- | --- |
| Title | 45-60 characters | `স্যামসাং গ্যালাক্সি এ৫৫ এর দাম ও রিভিউ ২০২৬ \| ব্র্যান্ড` |
| Meta description | 110-140 characters | One sentence of value + one call to action |
| H1 | Close to the title, may be longer | |

Character counts are approximate; preview in a SERP tool that measures pixels.

## URLs and slugs

| Option | Example | Pros | Cons |
| --- | --- | --- | --- |
| English slug | `/bn/samsung-a55-price` | Short, shareable, safe everywhere | No Bangla keyword in URL |
| Romanized Bangla | `/bn/mobile-er-dam` | Matches Banglish queries | Spelling choice is arbitrary |
| Bangla slug | `/bn/মোবাইলের-দাম` | Keyword in URL, readable in browsers | Percent-encoded when shared (`%E0%A6%AE...`), long |

Google handles all three. Pick one rule per site, keep slugs short, use hyphens, and never
change existing URLs without 301 redirects. WordPress creates Bangla slugs from Bangla
titles by default; set the slug explicitly if the site uses English slugs.

## hreflang and canonical

For a page available in Bangla and English:

```html
<link rel="canonical" href="https://example.com/bn/pricing/">
<link rel="alternate" hreflang="bn-BD" href="https://example.com/bn/pricing/">
<link rel="alternate" hreflang="en" href="https://example.com/en/pricing/">
<link rel="alternate" hreflang="x-default" href="https://example.com/en/pricing/">
```

- Every language version lists all versions including itself, and the links must be
  reciprocal; one-sided hreflang is ignored.
- Use `bn` for Bangla for everyone, `bn-BD` for Bangladesh-specific content (prices in BDT),
  `bn-IN` only if there is a separate West Bengal version. A region-only value like `BD`
  is invalid; the language comes first.
- Canonical points to the same-language URL, never across languages.
- Sitemaps can carry hreflang instead of `<head>` tags (`xhtml:link`), useful for large sites.
- `<html lang="bn">` helps browsers and screen readers; Google mostly detects language from
  content, so the text itself must be Bangla (not an image, not Bijoy-encoded).

## Structured data

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "ঢাকায় বাসা ভাড়ার নিয়ম",
  "inLanguage": "bn",
  "datePublished": "2026-11-22",
  "author": { "@type": "Person", "name": "Author Name" }
}
```

Dates in JSON-LD stay ISO 8601 with Latin digits; only visible text uses Bangla digits.

## Local SEO (Bangladesh)

- Google Business Profile with the Bangla and English name, Bangla address lines,
  phone in +880 format.
- NAP (name, address, phone) consistent in both scripts across directories.
- Area names users actually use (মিরপুর ১০, উত্তরা সেক্টর ৭) on location pages.

## Audit checklist for a Bangla page that does not rank

- [ ] Text is Unicode Bangla (not Bijoy, not images); `bangla-text-normalization check` passes
- [ ] Indexed? `site:` search and Search Console URL inspection
- [ ] One primary intent; no other page on the site targets the same query
- [ ] Title/H1 contain the main Bangla form; FAQs cover Banglish/English phrasing where data shows demand
- [ ] hreflang reciprocal, canonical self-referencing, `lang="bn"`
- [ ] Content depth vs top 3 results; original information (prices, local details, photos)
- [ ] Fast on 4G mobile; fonts not blocking render (`bangla-typography-web`)
- [ ] Internal links from relevant Bangla pages with descriptive Bangla anchor text
