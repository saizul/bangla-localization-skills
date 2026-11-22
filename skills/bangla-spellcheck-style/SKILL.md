---
name: bangla-spellcheck-style
description: Proofread and edit Bangla (Bengali) text for standard spelling and consistent style - Bangla Academy standard spellings (সরকারি not সরকারী, দুর্নীতি not দূর্নীতি, স্টেশন not ষ্টেশন, ব্যবহার not ব্যাবহার, অ্যাপ not এ্যাপ), mixed সাধু/চলিত register (গুরুচণ্ডালী), formal আপনি vs informal তুমি tone for UI and marketing, কি/কী and other usage rules, danda and punctuation spacing, and digit consistency. Includes a rule-based checker with line numbers and a safe auto-fix, plus a tone and style guide. Use when the user asks to proofread, spellcheck or copy-edit Bangla, review a Bangla translation, choose formal or informal tone, write a Bangla style guide, or make Bangla UI text and articles consistent.
license: MIT
compatibility: Python 3.8+ (standard library only) for scripts/bn_style_check.py. Rule-based; not a full dictionary spellchecker.
metadata:
  author: Saizul Amin
  version: "0.1.0"
---

# Bangla spelling and style

Make Bangla text correct by the standard most Bangladeshi publishers and institutions use
(Bangla Academy প্রমিত বানান) and consistent in register and tone.

Paths below are relative to this skill's folder (in Claude Code: `${CLAUDE_SKILL_DIR}`).

## When to use

- "Proofread this Bangla article / translation / UI file"
- Choosing আপনি or তুমি for an app, campaign or chatbot
- Mixed সাধু and চলিত forms, inconsistent spellings across pages
- Writing a Bangla style guide for a team

## When not to use

- Broken characters, dotted circles, mojibake, Bijoy text: `bangla-text-normalization` first
- Placeholder/ICU checks for translation files: `bangla-ui-translation`
- West Bengal house styles that follow different spelling conventions: confirm the target
  standard with the user before "correcting"

## Workflow

1. **Agree on the standard** (defaults in brackets): Bangla Academy প্রমিত বানান [yes];
   register চলিত [yes for web and UI]; tone আপনি (formal) [apps, banking, government,
   e-commerce] or তুমি (friendly) [youth brands, games, only if the brand says so]; digits
   Bangla or Latin.
2. **Run the checker (read-only):**
   ```bash
   python3 scripts/bn_style_check.py article.md
   python3 scripts/bn_style_check.py locales/bn.json --tone formal
   python3 scripts/bn_style_check.py chapter.txt --digits bn --json
   python3 scripts/bn_style_check.py draft.txt --fail-on info
   ```
   Rules: `spelling` (65+ high-confidence Academy corrections, including inflected
   forms like সরকারীভাবে), `style` (এ্যা -> অ্যা), `register` (sadhu and cholito forms in the
   same text), `tone` (তুমি/তুই forms and informal imperatives in formal text, or the reverse),
   `punctuation` (`.`/`|` as sentence end, space before `।?!,`, missing space after `।`),
   `digits`. Exit 1 when findings reach `--fail-on` (default `warning`).
3. **Read the text yourself** after the script: it only knows listed patterns. Use
   [references/spelling-rules.md](references/spelling-rules.md) for the rules behind each
   correction (ই/ঈ, উ/ঊ, ণত্ব-ষত্ব in foreign words, ্য-ফলা, hasanta, compound words) and
   [references/tone-guide.md](references/tone-guide.md) for tone, register and usage
   (কি/কী, কোনো/কোন, হলো/হল, numbers in prose).
4. **Apply safe fixes** when the user agrees:
   ```bash
   python3 scripts/bn_style_check.py draft.txt --fix > draft.fixed.txt
   ```
   `--fix` changes only listed misspellings and `|` used as danda. Register, tone and
   punctuation changes need judgement: rewrite those sentences yourself and show them.
5. **Re-run** the checker on the edited text and summarize what changed.

## Output

- A findings list (`file:line:col rule: found -> suggestion (reason)`), grouped by rule.
- The corrected text (or a diff), with register and tone rewrites explained in one line each.
- Style decisions to add to the team's guide (e.g. "Use অ্যাকাউন্ট, never একাউন্ট").
