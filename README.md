# django-plausible-iplweb

[![CI](https://github.com/mpasternak/django-plausible-iplweb/actions/workflows/ci.yml/badge.svg)](https://github.com/mpasternak/django-plausible-iplweb/actions/workflows/ci.yml)
![PyPI](https://img.shields.io/pypi/v/django-plausible-iplweb.svg)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)
![Django](https://img.shields.io/badge/django-5.2%20%7C%206.0-blue)
![PyPI - Status](https://img.shields.io/pypi/status/django-plausible-iplweb.svg)
![PyPI - License](https://img.shields.io/pypi/l/django-plausible-iplweb.svg)


Django module to provide easy [Plausible](https://plausible.io/) integration, with [Wagtail](https://wagtail.io/) support.

## Installation

```
pip install django-plausible-iplweb
```

Then simply add `plausible` to `INSTALLED_APPS`.

## Usage

`django-plausible-iplweb` provides a `plausible` template tag that emits Plausible's
current per-site tracking script. Each Plausible site now has its **own script URL**
(e.g. `https://plausible.io/js/pa-XXXXXXXX.js`) — there is no `data-domain` attribute
any more. Copy the script URL from your Plausible dashboard (**Site Settings → General →
Site Installation**) into `PLAUSIBLE_SCRIPT_URL`, then place the tag in your `<head>`:

```html
{% load plausible %}

{% plausible %}
```

With `PLAUSIBLE_SCRIPT_URL = "https://plausible.io/js/pa-XXXXXXXX.js"`, this renders:

```html
<script defer src="https://plausible.io/js/pa-XXXXXXXX.js"></script>
<script>
  window.plausible = window.plausible || function () { (window.plausible.q = window.plausible.q || []).push(arguments) };
  plausible.init({"autoCapturePageviews": false});
  (function () {
    var path = window.location.pathname;
    var masks = [];
    for (var i = 0; i < masks.length; i++) {
      path = path.replace(new RegExp(masks[i].pattern, masks[i].flags || "g"), masks[i].replacement);
    }
    var url = window.location.origin + path + window.location.search;
    plausible("pageview", { url: url });
  })();
</script>
```

Automatic pageview capture is **disabled** (`autoCapturePageviews: false`) so the package
can send a single, optionally-masked pageview itself (see [URL masking](#url-masking)).

If `PLAUSIBLE_SCRIPT_URL` is empty (the default), the tag renders nothing — a convenient
way to switch analytics off in development.

### Configuration

All configuration lives in `settings.py`:

| Setting | Default | Purpose |
|---|---|---|
| `PLAUSIBLE_SCRIPT_URL` | `""` | Full per-site script URL from your Plausible dashboard. Empty → tag renders nothing. |
| `PLAUSIBLE_INIT_OPTIONS` | `{"autoCapturePageviews": False}` | Dict passed (as JSON) to [`plausible.init(...)`](https://plausible.io/docs/script-extensions). Add any init option here, e.g. `{"autoCapturePageviews": False, "hashBasedRouting": True}`. |
| `PLAUSIBLE_URL_MASKS` | `[]` | Ordered list of client-side path-masking rules (see below). |
| `PLAUSIBLE_KEEP_QUERY_STRING` | `True` | Append `location.search` to the reported URL (keeps `utm_*`/`ref` for acquisition reports). Set `False` to drop the query string entirely. |

You can also pass the script URL at call time, e.g. to use a different site on one page:

```html
{% plausible script_url="https://plausible.io/js/pa-OTHER.js" %}
```

### URL masking

Plausible records the page URL. If your paths contain identifiers (invitation codes,
user IDs, UUIDs, …) those would leak into your analytics. `PLAUSIBLE_URL_MASKS` lets you
redact them **client-side** before the pageview is sent. Each rule is applied to
`location.pathname` in order via JavaScript's
[`String.replace(new RegExp(pattern, flags), replacement)`](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String/replace):

```python
PLAUSIBLE_URL_MASKS = [
    # Mask invitation/passphrase codes:  /i/<passphrase>  ->  /i/__code__
    {"pattern": r"^/i/[^/]+", "replacement": "/i/__code__"},
    # Mask UUIDs anywhere in the path:  /<uuid>  ->  /__id__
    {"pattern": r"/[0-9a-f-]{36}", "replacement": "/__id__", "flags": "gi"},
    # Mask numeric ids:  /123  ->  /__id__
    {"pattern": r"/\d+", "replacement": "/__id__"},
]
```

`pattern` and `flags` are **JavaScript** regular-expression syntax (the rules run in the
browser). `flags` defaults to `"g"`. The patterns above are examples — adapt them to your
own routes; the default (`[]`) applies no masking.

> **Caveat:** like Plausible's own [redaction guidance](https://plausible.io/docs/custom-locations),
> this masking runs once when the page loads. It may not behave as expected in
> single-page applications or with hash-based routing, where `location` changes
> without a full page load.

### Overriding the rendered markup

The snippet is rendered from the `plausible/plausible.html` template. To fully customise
it, shadow that path in your own project's templates directory.

## Usage with Wagtail

`django-plausible-iplweb` also provides an optional [Wagtail](https://wagtail.org)
integration that lets editors set the script URL **per site** through the Wagtail admin.
Add `plausible.contrib.wagtail` to `INSTALLED_APPS` and run `migrate`.

Configuration is done through the "Plausible Analytics"
[setting](https://docs.wagtail.org/en/stable/reference/contrib/settings.html):

- `script_url`: the full per-site Plausible script URL. Blank (the default) → nothing is rendered for that site.

Masking (`PLAUSIBLE_URL_MASKS`), init options, and query-string handling are still
configured globally via the Django settings above.

Load `plausible_wagtail` rather than `plausible`; the tag itself is still `plausible`:

```html
{% load plausible_wagtail %}

{% plausible %}
```

## Migrating from 0.5.x

Version 0.6.0 is a clean break to match Plausible's new tracker. Update your settings:

| Old (0.5.x) | New (0.6.0) |
|---|---|
| `PLAUSIBLE_DOMAIN` + `PLAUSIBLE_SCRIPT_NAME` | `PLAUSIBLE_SCRIPT_URL` (the full script URL from your dashboard) |
| `data-domain` (request host / `site_domain`) | *(gone — the site is identified by the script URL)* |
| `{% plausible site_domain=… plausible_domain=… script_name=… %}` | `{% plausible %}` (optionally `script_url=…`) |
| Wagtail `site_domain` / `plausible_domain` / `script_name` fields | Wagtail `script_url` field (migration `0002` applies the change) |

## License

This project is licensed under the **BSD 3-Clause License**. See the [LICENSE](LICENSE) file for details.

This is a fork of [`django-plausible`](https://github.com/RealOrangeOne/django-plausible) by Jake Howard.
