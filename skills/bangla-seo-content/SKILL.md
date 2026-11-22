---
name: bangla-seo-content
description: Plan, write and optimize Bangla (bn-BD) web content for search - Bangla keyword research nuances (Bangla script vs Banglish/romanized queries like "bhalobasar golpo" / "valobasar golpo", English loanwords, mixed-script searches, spelling variants), a generator for Banglish spelling variants, search intent for Bangladesh, titles and meta descriptions that fit, Bangla vs transliterated URL slugs, hreflang (bn-BD, bn, en, x-default), lang attributes, schema.org inLanguage, and bilingual site structure. Use when the user wants Bangla SEO, keyword research for Bangladesh, a Bangla blog or landing page that ranks, Banglish keyword variants, hreflang or URL decisions for a Bangla/English site, or asks why a Bangla page does not rank.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/banglish_variants.py. Keyword volumes need the user's own SEO tools.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla SEO content

People in Bangladesh search in three ways: Bangla script (মোবাইলের দাম), romanized Bangla
(mobile er dam, mobiler dam) and English (mobile price in bd). Good Bangla SEO covers the
intent behind all three, writes natural Bangla, and gets the technical signals right.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- Keyword research or a content plan for a Bangladeshi audience
- Writing or rewriting a Bangla article, category or landing page for search
- Bilingual site decisions: URLs, hreflang, language switcher, duplicate content
- "Our Bangla pages get no traffic" audits

## When not to use

- UI string translation: `bangla-ui-translation`
- Spelling and style proofreading: `bangla-spellcheck-style` (run it on the final draft)
- Broken characters or Bijoy text on the page: `bangla-text-normalization`
- Generic technical SEO unrelated to language (crawl budget, Core Web Vitals)

## Workflow

1. **Brief.** Ask for: topic/product, audience (Dhaka city, nationwide, diaspora, West Bengal),
   page type, business goal, existing rankings or Search Console data, competitor URLs.
2. **Seed keywords in all three forms.** Write the Bangla seeds, then generate Banglish variants:
   ```bash
   python3 scripts/banglish_variants.py "ভালোবাসার গল্প" "সরকারি চাকরির খবর" "শাড়ির দাম"
   python3 scripts/banglish_variants.py --file seeds.txt --csv > banglish.csv
   python3 scripts/banglish_variants.py --max 4 --json "বাড়ি ভাড়া"
   ```
   The output is a candidate list (bhalobasar golpo, valobasar golpo ...). Add English
   loanword forms by hand (mobile, online, price in bd). Check every candidate in the user's
   keyword tool, Google autocomplete/"People also ask" or Search Console; keep only those
   with real demand. Never present the generated variants as search volumes.
3. **Map intent and pick one primary keyword per page** using
   [references/seo-guide.md](references/seo-guide.md): informational (কীভাবে, কী, কেন),
   commercial (দাম, সেরা, রিভিউ, price in bd), local (ঢাকায়, near me, এলাকার নাম),
   navigational (brand). Decide which script the page targets; one page usually ranks for
   Bangla and Banglish variants of the same intent, while English queries often need an
   English page.
4. **Outline and write in natural চলিত Bangla.** Primary keyword in the title, H1, first
   100 words and one H2; variants and synonyms elsewhere. Answer the question early. Use
   Bangla digits or Latin digits consistently (prices: follow the market; most Bangladeshi
   e-commerce shows ৳ with Bangla or Latin digits consistently per site). Do not stuff Banglish
   into Bangla prose; put Banglish only where users would see it naturally (FAQ phrasing,
   product tags), never as hidden text.
5. **On-page signals:**
   - Title: about 45-60 characters of Bangla (Bangla glyphs are wide; Google truncates by
     pixel width), meta description about 110-140 characters, both unique per page.
   - `<html lang="bn">`, `hreflang` and canonical as in the guide; `inLanguage: "bn"` in
     schema.org `Article`/`Product`/`FAQPage`.
   - URL slug: pick a site-wide rule (short English or romanized slug for shareable,
     readable URLs, or Bangla slugs when the audience types and shares Bangla); never mix
     rules for the same section.
   - Images: Bangla `alt` text describing the image; file names in English/romanized.
6. **Bilingual sites:** separate URLs per language (`/bn/...`, `/en/...` or subdomain),
   reciprocal `hreflang`, `x-default`, self-referencing canonical per language, no automatic
   IP-based redirects (Googlebot crawls mostly from the US).
7. **Proofread and validate.** Run `bangla-spellcheck-style` on the draft; spot-check
   rendering with `bangla-typography-web`; validate hreflang pairs (every page must point back).

## Output

- Keyword table: keyword, script (bn / banglish / en), intent, target page, status
  (verified volume or "to check"); generated variants clearly marked as unverified.
- The content outline or draft with title, meta description, H1/H2s, slug and FAQ.
- The technical snippet: `<head>` tags (lang, hreflang, canonical) and JSON-LD.
- A short list of follow-ups (internal links, pages to merge, Search Console checks after 2-4 weeks).
