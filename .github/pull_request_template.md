## What does this pull request do?

<!-- One or two sentences. Link the issue: "Closes #123". -->

## Type

- [ ] New skill
- [ ] New rule, check or option in an existing script
- [ ] Workflow / reference / glossary improvement
- [ ] Bug fix
- [ ] Repository tooling (validator, CI)

## Checklist

- [ ] `python tools/validate_skills.py` passes
- [ ] `ruff check . && ruff format --check .` passes
- [ ] `pytest` passes; new script behaviour has tests with fixtures in `tests/fixtures/<skill>/`
- [ ] Scripts use only the Python standard library, support `--help`, have a `--json` option
      where output is structured, and exit non-zero on findings
- [ ] Read-only by default; anything that rewrites files is opt-in (`--in-place`, `--emit-catalog`)
- [ ] Bangla examples are correct standard Bangla (Bangla Academy spelling unless noted) and
      invisible characters (ZWJ, ZWNJ, combining marks on their own) are written as `\uXXXX` in code
- [ ] No secrets or personal data in fixtures
- [ ] New skills: listed in `.claude-plugin/marketplace.json`, the README skills table, `AGENTS.md` and `CHANGELOG.md`
