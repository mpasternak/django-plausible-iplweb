# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2] - 2026-08-07

### Fixed

- Pageview tracking was broken in the rendered snippet: the inline `window.plausible`
  stub is a plain function with no `.init` property, so the very next line —
  `plausible.init({...})` — threw `plausible.init is not a function` before the real
  tracker script had loaded. The `GET` for `pa-….js` succeeded, but `init()` and the
  pageview `POST` never ran, so no visits were counted. The template now also stubs
  `plausible.init` (storing the options on `plausible.o`, matching Plausible's own
  official snippet) so the call is safe before the script arrives.
  Thanks to [@igor-alperovich-matplus](https://github.com/igor-alperovich-matplus)
  for the fix ([#1](https://github.com/mpasternak/django-plausible-iplweb/pull/1)).

## [0.6.1] - 2026-08-07

### Added

- Support for Django 6.1: added to the CI test matrix (on Python 3.12, 3.13 and 3.14)
  and to the `Framework :: Django :: 6.1` trove classifier.

### Fixed

- The CI version matrix did not actually take effect — every cell ended up testing the
  same Django version. Two causes: `uv run` without `--no-sync` re-synced the
  environment from the lockfile and silently undid the per-cell
  `uv pip install "django~=X.Y.0"` pin, and `uv sync` picked its interpreter from
  `requires-python` instead of `matrix.python-version`. The workflow now passes
  `--python ${{ matrix.python-version }}` to `uv sync` and runs tests with
  `uv run --no-sync`.
- Added a "Show resolved versions" CI step that prints the Python and Django versions
  actually in use, so a silently collapsing matrix cannot go unnoticed again.

## [0.6.0] - 2026-06-13

### Added

- Support for Plausible's new tracker script (`PLAUSIBLE_SCRIPT_URL`).
- Configurable URL masking via `PLAUSIBLE_URL_MASKS`, plus configurable init options
  and query-string handling.

### Changed

- **Breaking:** settings and template-tag arguments were reworked for the new tracker.
  `PLAUSIBLE_DOMAIN` + `PLAUSIBLE_SCRIPT_NAME` are replaced by a single
  `PLAUSIBLE_SCRIPT_URL`; the `site_domain` / `plausible_domain` / `script_name`
  arguments are gone. The Wagtail settings model gains a `script_url` field
  (migration `0002`). See "Migrating from 0.5.x" in the README.
- Packaging converted from `setup.py`/`setup.cfg` to `pyproject.toml` + uv, with the
  version derived from git tags by setuptools-scm.
- Django and Wagtail dependency floors raised to match `requires-python`.
- GitHub Actions workflows modernised to use uv and hardened for a public repo.
- `pre-commit` hooks added (ruff, pyupgrade, django-upgrade); `black` dropped in
  favour of ruff.

## [0.5.0] - 2023-05-12

### Changed

- Upgraded the supported Django and Wagtail versions ([#25](https://github.com/RealOrangeOne/django-plausible/pull/25)).
- Replaced flake8 with ruff; added CI for Python 3.11.

## [0.4.0] - 2022-10-29

### Changed

- Improved validation of the configured script name.

## [0.3.0] - 2022-08-25

### Changed

- Changed the app label (and added a test covering it).
- Updated the supported Python and Django constraints; Django 4.0+ is no longer
  tested on Python 3.7.
- CI now tests against specific, pinned Wagtail versions.

## [0.2.0] - 2021-11-13

### Removed

- Dropped support for Django 2.2 and 3.0.

### Fixed

- Added a missing `__init__.py`.

## [0.1.0] - 2021-09-05

### Added

- Initial release: Django template tag for embedding the Plausible script, with an
  optional Wagtail integration and per-site configuration.

[Unreleased]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.6.2...HEAD
[0.6.2]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.6.1...v0.6.2
[0.6.1]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.6.0...v0.6.1
[0.6.0]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mpasternak/django-plausible-iplweb/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mpasternak/django-plausible-iplweb/releases/tag/v0.1.0
