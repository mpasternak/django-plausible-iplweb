# Design: New Plausible tracker + configurable URL masking

Date: 2026-06-13
Status: Approved
Target version: 0.6.0 (breaking change — clean break from the 0.5.x `data-domain` API)

## Background

Plausible replaced the old `script.js` + `data-domain` tracker with a per-site
script (e.g. `https://plausible.io/js/pa-XXXXXXXX.js`) plus a JS init API
(`plausible.init({...})`). The site identity now lives in the script URL — there
is no `data-domain` attribute. To redact sensitive path segments before sending
pageviews, Plausible recommends disabling automatic capture
(`autoCapturePageviews: false`) and sending a manually-masked `pageview`.

References:
- https://plausible.io/docs/script-update-guide
- https://plausible.io/docs/script-extensions
- https://plausible.io/docs/custom-locations

## Decisions

1. **Clean break.** Replace the old behavior entirely. Remove
   `PLAUSIBLE_DOMAIN`, `PLAUSIBLE_SCRIPT_NAME`, the `data-domain` markup,
   `plausible/utils.py`, and the Wagtail `validators.py`.
2. **Configurable masking + safe defaults + commented examples.** Masking runs
   client-side; rules come from Django settings; the README ships commented
   app-specific examples (`/i/<code>`, uuid/int ids).
3. **Overridable Django template.** Render via `plausible/plausible.html`
   (shadowable), replacing the Python string-building.

## Settings (Django)

| Setting | Default | Purpose |
|---|---|---|
| `PLAUSIBLE_SCRIPT_URL` | `""` | Full site script URL pasted from the Plausible dashboard. Empty → tag renders nothing (analytics off). |
| `PLAUSIBLE_INIT_OPTIONS` | `{"autoCapturePageviews": False}` | Dict serialized to JSON into `plausible.init(...)`. |
| `PLAUSIBLE_URL_MASKS` | `[]` | Ordered `{"pattern", "replacement", "flags"?}` rules applied to `location.pathname` via `String.replace(new RegExp(...))`. |
| `PLAUSIBLE_KEEP_QUERY_STRING` | `True` | Append `location.search` to the pageview URL (Plausible's default; preserves utm/ref). Set `False` to drop it. |

## Masking semantics

Emitted JS computes `maskedPath` from `location.pathname`, applies each rule in
order, then sends `plausible("pageview", { url: location.origin + maskedPath [+ location.search] })`.
Default masks `[]` = no path redaction. Documented commented example:

```python
PLAUSIBLE_URL_MASKS = [
    {"pattern": r"^/i/[^/]+", "replacement": "/i/__code__"},          # /i/<passphrase>
    {"pattern": r"/[0-9a-f-]{36}", "replacement": "/__id__", "flags": "gi"},  # uuids
    {"pattern": r"/\d+", "replacement": "/__id__"},                   # numeric ids
]
```

Caveat (documented): like Plausible's own example, this may not work in SPAs or
hash-based routing where `location` changes before the snippet runs.

## Rendering

- `plausible/templates/plausible/plausible.html`: script tag + `plausible` queue
  stub + `plausible.init(<INIT_JSON>)` + masking loop + manual pageview.
- `init_options` and `url_masks` injected as JSON, XSS-escaped (`<`→`<`,
  `>`→`>`, `&`→`&`, U+2028/U+2029) — the same escaping Django's
  `json_script` uses.
- Template files added to `[tool.setuptools.package-data]`.

## Template tag

- `{% plausible %}` (Django): reads settings, renders the template. Optional
  `script_url=` arg override. Empty URL → `""`. No `data-domain`, no request
  dependency. A shared `render_plausible(script_url, ...)` helper backs both tags.
- `plausible/utils.py` and Wagtail `validators.py` deleted; `test_utils.py`
  removed.

## Wagtail integration

- `PlausibleSettings`: drop `site_domain`/`plausible_domain`/`script_name`, add
  `script_url = models.URLField(blank=True)`. Drop the Wagtail <3.0 import shim
  (now require Wagtail ≥7.0). New migration `0002`.
- `plausible_wagtail` tag feeds per-site `script_url` into `render_plausible`.
  Masks/init options stay global Django settings.

## Tests

- Rewrite `tests/test_django.py` (script tag, init JSON, masks JSON, empty-url →
  nothing, XSS escaping, init override, keep/drop query, arg override).
- Rewrite `tests/test_wagtail.py` (per-site `script_url`, app_label).
- Delete `tests/test_utils.py`.

## Docs

README usage rewritten: settings table, emitted snippet explained, masking with
the commented `/i/` example, SPA caveat, and a "Migrating from 0.5.x" mapping.
