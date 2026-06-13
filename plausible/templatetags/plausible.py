import json

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

register = template.Library()

# Default options passed to plausible.init(...). Automatic pageview capture is
# disabled so we can send a single manually-masked pageview instead.
DEFAULT_INIT_OPTIONS = {"autoCapturePageviews": False}

# Escapes that make a JSON literal safe to embed inside a <script> block,
# matching the escaping Django's json_script applies.
_JSON_SCRIPT_ESCAPES = {
    ord("<"): "\\u003c",
    ord(">"): "\\u003e",
    ord("&"): "\\u0026",
    0x2028: "\\u2028",  # line separator
    0x2029: "\\u2029",  # paragraph separator
}


def _safe_json(value) -> SafeString:
    """Serialize ``value`` to JSON that is safe to embed in a <script> block."""
    return mark_safe(json.dumps(value).translate(_JSON_SCRIPT_ESCAPES))


def render_plausible(
    script_url,
    *,
    init_options=None,
    url_masks=None,
    keep_query_string=None,
) -> SafeString:
    """Render the Plausible tracker snippet, or "" when no script URL is set."""
    if not script_url:
        return mark_safe("")

    if init_options is None:
        init_options = getattr(settings, "PLAUSIBLE_INIT_OPTIONS", DEFAULT_INIT_OPTIONS)
    if url_masks is None:
        url_masks = getattr(settings, "PLAUSIBLE_URL_MASKS", [])
    if keep_query_string is None:
        keep_query_string = getattr(settings, "PLAUSIBLE_KEEP_QUERY_STRING", True)

    return mark_safe(
        render_to_string(
            "plausible/plausible.html",
            {
                "plausible_script_url": script_url,
                "plausible_init_options": _safe_json(init_options),
                "plausible_url_masks": _safe_json(url_masks),
                "plausible_keep_query_string": keep_query_string,
            },
        )
    )


@register.simple_tag
def plausible(script_url=None) -> SafeString:
    if script_url is None:
        script_url = getattr(settings, "PLAUSIBLE_SCRIPT_URL", "")
    return render_plausible(script_url)
