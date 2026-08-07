# AGENTS.md

Guidance for LLM agents (and humans) working on this repository. This
complements `README.md`, which covers install/usage; this file covers
conventions, gotchas, and *why* things are set up the way they are.

## What this project is

A Python CLI (`xmipp3_installer`) that drives the installation of
[xmipp3](https://github.com/I2PC/xmipp3) — clones sources, runs CMake,
compiles, downloads models, etc. xmipp3's primary branch is `main` (it
used to be `devel` — if you see a stray `devel` reference in help text
or a test fixture, it's stale, not intentional).

## Architecture, in one paragraph

`application/cli/` parses argv into a mode + args (argparse-based, with
custom help formatters in `application/cli/parsers/`).
`installer/installer_service.py` (`InstallationManager`) picks the right
executor via `installer/modes/mode_selector.py` and runs it.
Every mode lives under `installer/modes/` as a `ModeExecutor` subclass
(`installer/modes/mode_executor.py` is the base class) — look at an
existing mode executor before adding a new one, they all follow the same
shape (`_set_executor_config` for mode-specific flags, `run()` for the
actual work). `installer/handlers/` wraps external tools (git, shell,
cmake, conda). `repository/config.py` reads/writes the config file.
`api_client/` sends anonymous installation telemetry (see README).

## Running tests — always use the script

**Never invoke `pytest` directly on this repo.** Use:

```
./scripts/run-tests.sh [unitary|integration|e2e|all]
```

(or `scripts/run-tests.ps1` on Windows). Each stage has its own pytest
config file under `conf/pytest/` (`unitary.ini`, `integration.ini`,
`e2e.ini`), all of which set `addopts = --capture=no`. A bare
`pytest tests/...` picks up none of that — you'll get pytest's default
stdout capture instead, which silently breaks every test that manually
patches `sys.stdout` (several CLI help-message tests do exactly this).
The symptom is confusing: tests fail locally with an *empty* captured
string, look like a real regression, and pass fine in CI — because CI
always goes through the script. If you ever see that pattern, suspect
the invocation before the code.

If you must run a subset directly, pass the matching config explicitly:
`python -m pytest -c conf/pytest/unitary.ini tests/unitary/...`.

**Coverage is a hard gate at 100%** per stage (see `conf/coverage/*.rc`).
`run-tests.sh` fails the run if coverage drops below that. This is
actually useful when trimming tests: if removing a test drops coverage,
it wasn't redundant.

## Ruff

Single `conf/ruff.toml` covering both `src/` and `tests/`. Tests are
looser (no docstring rules, higher argument-count tolerance) via
`[lint.per-file-ignores]` on the `tests/**/*.py` glob rather than a
separate config file — same effective rule set as before, just one
place to look. Pins an explicit `select = ["E4", "E7", "E9", "F"]`
base before `extend-select`. **Don't remove that `select` line.**
Ruff's actual default rule set changes between versions when only
`extend-select` is set (0.16.0 silently went from ~200 enabled rules
to ~430, unrelated categories included, and broke CI on a routine
Renovate version bump) — pinning `select` explicitly keeps the
enforced rule set stable across ruff upgrades. When adding a new rule
category, add it deliberately to `extend-select`, run the full suite,
and fix what it finds rather than assuming it's already covered by
defaults.

Renovate opens ruff/dependency bump PRs with the version pinned in
`pyproject.toml`; since CI always uses that pinned version (never
"latest"), a new ruff release only ever breaks its own bump PR, not
`main`. Fix forward in that PR.

## Naming convention: single underscore, not double

Internal methods/attributes use a single leading underscore
(`_get_source_info`), not a double one. Double-underscore triggers
Python's name mangling, which only exists to avoid attribute collisions
across an inheritance hierarchy — none of these classes need that. Its
practical effect here was just friction: any test reaching into an
internal method had to spell out the mangled form
(`instance._ClassName__method`), which is fragile (breaks if the class
is renamed) and adds noise for no safety benefit.

Two single-underscore uses coexist and both are correct:
- **Extension point for subclasses** — e.g. `ModeExecutor._set_executor_config`,
  overridden by every mode executor. This is a real "protected" method.
- **Internal, not meant to be touched** — everything that used to be
  `__double_underscore`. Same prefix, different intent; Python doesn't
  distinguish the two at the syntax level and neither does this repo.

**Module-level** `__double_underscore` functions/constants (e.g. in
`shell_handler.py`, `cli.py`, `installation_info_assembler.py`, and
pervasively as pytest fixture names like `__mock_something` across the
whole test suite) are a *different, intentional* convention: Python
does not mangle names outside a class body, so there's no mangling
problem to fix there. Leave those alone — don't "fix" them to single
underscore, that's not what this rule is about.

## Test style

- One behavior per test, named `test_<does_x>_when_<condition>`.
- Fixtures are prefixed `__mock_*`; parametrized fixtures use pytest's
  `indirect=[...]` a lot — read a neighboring test file before adding a
  new one, the pattern is very consistent across the suite.
- It's normal — and expected — for a test of an orchestrating method
  (e.g. `run()`) to mock out every internal collaborator it calls. That
  means the internal collaborator's own logic is *only* covered by its
  own direct test, not by the orchestrator's test. Don't assume a
  private-method test is redundant just because a public-method test
  also exists for the same class — check whether the public test
  actually exercises that code path unmocked before removing anything
  (the 100% coverage gate will catch you if you get this wrong, but
  check first anyway).

## Docstrings

`src/` enforces pydocstyle (pep257 convention) via ruff's `D` rules.
Follow the existing markdown-ish style:
```python
def foo(bar: str) -> bool:
  """
  ### One-line summary.

  Optional longer explanation.

  #### Params:
  - bar (str): What it is.

  #### Returns:
  - (bool): What it means.
  """
```
`tests/` does not enforce this — test functions don't need docstrings.

## Line endings

`.gitattributes` forces LF for all text files (`* text=auto eol=lf`).
The repo has been edited from both Windows and Linux over time; don't
let CRLF creep back in. If a diff looks enormous for a small logical
change, check `file <path>` on the files involved before assuming
something's wrong with the edit itself.

## Making changes

- `pip install -e ".[test]"` gets you everything needed to run tests
  and lint locally (see README).
- Small, single-purpose branches/PRs are preferred over bundling
  unrelated changes (e.g. a line-ending normalization and a rename are
  separate PRs even when one motivated the other).
