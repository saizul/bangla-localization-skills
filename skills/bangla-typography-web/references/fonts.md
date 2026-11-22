# Bangla fonts for the web

Always check the license file shipped with the font before self-hosting or bundling it.
Google Fonts families are under the SIL Open Font License (OFL) at the time of writing.

## Web fonts (Google Fonts, OFL)

| Family | Style | Weights | Good for | Notes |
| --- | --- | --- | --- | --- |
| Noto Sans Bengali | sans, neutral | variable 100-900 | UI, body text, apps | Broadest conjunct coverage; matches Noto Sans Latin; default on Android |
| Noto Serif Bengali | serif | variable 100-900 | news, long reading | Pairs with Noto Serif / Source Serif |
| Hind Siliguri | sans, compact | 300-700 | UI, dashboards, e-commerce | Includes Latin glyphs; very popular on Bangladeshi sites |
| Baloo Da 2 | rounded display | 400-800 | headings, kids, food, playful brands | Includes Latin |
| Anek Bangla | sans, variable width | variable | headings, editorial | Condensed and expanded widths |
| Tiro Bangla | traditional serif | 400 (+ italic Latin) | literature, poetry, headlines | Book-like letterforms |
| Galada | brush display | 400 | logos, posters | Display only, not body text |
| Atma | handwritten display | 300-700 | informal headings | Display only |
| Mina | geometric | 400, 700 | headings | |

## Popular non-Google fonts

| Family | Notes |
| --- | --- |
| SolaimanLipi | Widely used free Unicode font in Bangladesh; check the distribution license before bundling |
| Kalpurush | Free Unicode font, common in Bangladeshi publishing and government sites |
| Nikosh | Unicode font used in Bangladesh government templates |
| Siyam Rupali | Older free Unicode font; good coverage |
| Li Ador Noirrit, Bornomala, etc. | Many newer Bangladeshi releases; verify license and conjunct coverage |

**Not Unicode:** SutonnyMJ, SutonnyOMJ and other "MJ" fonts belong to the Bijoy (ANSI) era.
They display Bangla only for text typed in the Bijoy encoding, which search engines,
screen readers and copy/paste see as Latin gibberish. Never use them on the web.

## System fonts (fallbacks)

| Platform | Bengali fonts |
| --- | --- |
| Windows 10/11 | Nirmala UI, Vrinda, Shonar Bangla |
| macOS / iOS | Kohinoor Bangla, Bangla Sangam MN, Bangla MN |
| Android / ChromeOS | Noto Sans Bengali |
| Linux | Noto Sans Bengali, Lohit Bengali, Mukti (distribution dependent) |

System fallbacks look very different from each other (Vrinda is much smaller than Kohinoor
Bangla), so a web font is worth it for brand-consistent pages.

## Pairing Latin and Bangla

- Match x-height to the Bangla headstroke height visually; Bangla usually needs to be set
  5-10% larger to look equal. Use `size-adjust` in the Bangla `@font-face` to scale only the
  Bangla glyphs:
  ```css
  @font-face {
    font-family: "Hind Siliguri";
    src: url("/fonts/hind-siliguri-400.woff2") format("woff2");
    font-weight: 400;
    font-display: swap;
    unicode-range: U+0980-09FE, U+200C-200D, U+25CC, U+0964-0965;
    size-adjust: 108%;
  }
  ```
- Safe pairs: Noto Sans + Noto Sans Bengali; Inter + Hind Siliguri; Source Serif + Noto
  Serif Bengali; Poppins + Baloo Da 2 (headings).
- Digits: decide whether Bangla digits (০-৯) come from the Bangla font and Latin digits from
  the Latin font; mixed digit styles in tables look messy. Use `font-variant-numeric:
  tabular-nums` where the font supports it.

## Weights

Load at most two or three weights (for example 400 and 600). Bangla fonts are large
(Noto Sans Bengali static weights are typically 100-200 KB WOFF2 each; variable fonts more).
Without a real bold face browsers synthesize bold, which smears the headstroke.
