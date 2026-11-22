---
name: bangla-typography-web
description: Make Bangla (Bengali script) text look right on the web - choose and pair fonts (Noto Sans Bengali, Noto Serif Bengali, Hind Siliguri, Baloo Da 2, Tiro Bangla, Anek Bangla, SolaimanLipi, Kalpurush), build font stacks that mix Latin and Bangla, set line-height, size and spacing, load fonts fast (font-display, unicode-range subsets, preload, Google Fonts display=swap), keep conjuncts (যুক্তাক্ষর), vowel signs and reph rendering correctly, avoid letter-spacing/italic/justify traps, and set lang="bn". Includes a CSS/HTML linter and a test-string checklist. Use when Bangla text renders as boxes (tofu), broken or detached vowel signs and conjuncts, clipped lines, ugly fallback fonts, slow font loading, or when designing or reviewing CSS for a Bangla or bilingual site.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/bn_css_lint.py. Visual checks need a browser.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla web typography

Bangla script is an abugida with a headstroke (মাত্রা), stacked conjuncts, vowel signs above,
below and before the consonant, and reph. Most rendering problems come from the wrong font,
cramped line-height, letter-spacing, or text that is not real Unicode.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- New Bangla or bilingual (Bangla + English) site or app: fonts, sizes, CSS
- "Bangla shows as squares", "vowel signs are separated", "conjuncts look broken"
- Lighthouse/CLS complaints about Bangla web fonts, slow first paint on mobile data
- Reviewing a theme or design system for Bangla readiness

## When not to use

- Text that is legacy Bijoy/ANSI or contains bad Unicode sequences: fix the text first with
  `bangla-text-normalization` (no font can render Bijoy text as Unicode Bangla)
- Print/PDF typesetting (InDesign, LaTeX): font advice applies, CSS checks do not
- Native mobile apps: use the platform's font APIs (the font choices still apply)

## Workflow

1. **Confirm the text is Unicode.** If you see Latin gibberish like `Avwg evsjvq` or text that
   only renders with SutonnyMJ, stop and use `bangla-text-normalization`.
2. **Lint the CSS/HTML (read-only):**
   ```bash
   python3 scripts/bn_css_lint.py static/css/ templates/
   python3 scripts/bn_css_lint.py index.html style.css --json
   python3 scripts/bn_css_lint.py src/styles --fail-on info
   ```
   It reports font stacks without a Bangla font, `@font-face` without `font-display` or
   `unicode-range`, Google Fonts without `display=swap`, line-height below 1.5, letter-spacing,
   `word-break: break-all`, justify, small body size, faked italic and faux bold, legacy
   Bijoy fonts, and missing `lang`/charset in HTML. Exit 1 when findings reach `--fail-on`
   (default `warning`).
3. **Pick fonts** with [references/fonts.md](references/fonts.md). Default recommendation:
   - UI and body: **Noto Sans Bengali** or **Hind Siliguri** (both OFL, many weights).
   - Editorial/news: **Noto Serif Bengali** or **Tiro Bangla**.
   - Headlines with character: **Baloo Da 2**, **Anek Bangla**, **Galada** (display only).
4. **Apply the CSS baseline** (adapt names and sizes):
   ```css
   :root { --font-sans: "Inter", "Hind Siliguri", "Noto Sans Bengali", sans-serif; }
   body { font-family: var(--font-sans); font-size: 1.0625rem; line-height: 1.7; }
   :lang(bn) { letter-spacing: normal; word-break: normal; overflow-wrap: anywhere; }
   :lang(bn) h1, :lang(bn) h2 { line-height: 1.35; }
   :lang(bn) em, :lang(bn) i { font-style: normal; font-weight: 600; }
   ```
   Latin font first, Bangla font second: Latin glyphs come from the first font, Bangla glyphs
   fall through to the Bangla font. If the Latin font is a variable font that also covers
   Bengali, test it; otherwise put the Bangla font first for Bangla-only pages.
5. **Load fonts efficiently** (details in [references/checklist.md](references/checklist.md)):
   self-host WOFF2, `font-display: swap`, a Bengali `unicode-range`, preload only the one
   body weight used above the fold, at most 2-3 weights.
6. **Set language metadata:** `<html lang="bn">` (or `lang="bn-BD"`), and `lang="en"` on
   English passages in a Bangla page (and vice versa). This drives `:lang()` rules, font
   selection, hyphenation and screen readers.
7. **Render test strings** from [references/checklist.md](references/checklist.md) in Chrome,
   Firefox, Safari (iOS) and Android Chrome; compare conjuncts, reph and vowel signs.
8. **Re-run the linter** until it exits 0, and report what changed.

## Output

- Linter findings grouped by file, each with the fix applied or proposed.
- The final font stack(s), `@font-face` blocks and loading tags.
- Screenshot notes for the test strings (which browser, what looked wrong, fixed or not).
