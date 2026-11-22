# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | yes |

## What counts as a vulnerability

These skills are run by AI agents on real codebases and content, so unsafe behaviour is
treated like a code vulnerability:

- A script that writes, renames or deletes files without an explicit opt-in flag
  (`--in-place`, `--emit-catalog`), or writes outside the path the user gave
- A script that makes network connections or runs external commands
- Crafted input files (JSON, PO, CSS, HTML, PHP, Python, text) that make a script execute
  code, hang (catastrophic regex backtracking) or exhaust memory
- A `SKILL.md` workflow that tells the agent to run commands against a live site or rewrite
  user files without asking first
- Guidance that would leak user content to third parties

A wrong finding or a missed error is a normal bug: please open an issue.

## Reporting

Please **do not** open a public issue. Use
[GitHub private vulnerability reporting](https://github.com/saizul/bangla-localization-skills/security/advisories/new)
with the affected skill, version, impact and steps to reproduce. Remove personal data from
examples.

You will get an answer within 5 working days. Fixes are released as soon as possible and
credited in the changelog unless you prefer otherwise.
