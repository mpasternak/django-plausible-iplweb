from django.template import RequestContext, Template
from pytest_django.asserts import assertInHTML

SCRIPT_URL = "https://plausible.io/js/pa-ABC123.js"


def _render(template, rf, **extra_context):
    request = rf.get("/")
    return Template(template).render(RequestContext(request, extra_context))


def _plausible(rf):
    return _render("{% load plausible %}{% plausible %}", rf)


def test_renders_script_tag_from_setting(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    assertInHTML(f'<script defer src="{SCRIPT_URL}"></script>', _plausible(rf))


def test_renders_init_with_autocapture_disabled(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    rendered = _plausible(rf)
    assert "plausible.init(" in rendered
    assert '"autoCapturePageviews": false' in rendered


def test_renders_manual_pageview(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    rendered = _plausible(rf)
    assert 'plausible("pageview"' in rendered


def test_empty_script_url_renders_nothing(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = ""
    assert _plausible(rf).strip() == ""


def test_missing_script_url_renders_nothing(settings, rf):
    # No PLAUSIBLE_SCRIPT_URL defined at all.
    if hasattr(settings, "PLAUSIBLE_SCRIPT_URL"):
        del settings.PLAUSIBLE_SCRIPT_URL
    assert _plausible(rf).strip() == ""


def test_url_masks_serialized_into_js(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    settings.PLAUSIBLE_URL_MASKS = [
        {"pattern": "^/i/[^/]+", "replacement": "/i/__code__"},
    ]
    rendered = _plausible(rf)
    assert '"pattern": "^/i/[^/]+"' in rendered
    assert '"replacement": "/i/__code__"' in rendered


def test_default_masks_empty_array(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    if hasattr(settings, "PLAUSIBLE_URL_MASKS"):
        del settings.PLAUSIBLE_URL_MASKS
    rendered = _plausible(rf)
    assert "var masks = [];" in rendered


def test_masks_are_xss_escaped(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    settings.PLAUSIBLE_URL_MASKS = [
        {"pattern": "</script><x>", "replacement": "x"},
    ]
    rendered = _plausible(rf)
    # The dangerous value must be unicode-escaped, not emitted literally.
    assert "\\u003c/script\\u003e\\u003cx\\u003e" in rendered


def test_init_options_override(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    settings.PLAUSIBLE_INIT_OPTIONS = {
        "autoCapturePageviews": False,
        "hashBasedRouting": True,
    }
    rendered = _plausible(rf)
    assert '"hashBasedRouting": true' in rendered


def test_keep_query_string_by_default(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    if hasattr(settings, "PLAUSIBLE_KEEP_QUERY_STRING"):
        del settings.PLAUSIBLE_KEEP_QUERY_STRING
    assert "location.search" in _plausible(rf)


def test_drop_query_string_when_disabled(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    settings.PLAUSIBLE_KEEP_QUERY_STRING = False
    assert "location.search" not in _plausible(rf)


def test_script_url_arg_overrides_setting(settings, rf):
    settings.PLAUSIBLE_SCRIPT_URL = ""
    rendered = _render(
        '{% load plausible %}{% plausible script_url="https://x.test/js/pa-1.js" %}',
        rf,
    )
    assertInHTML('<script defer src="https://x.test/js/pa-1.js"></script>', rendered)


def test_simple_template_view(client, settings):
    settings.PLAUSIBLE_SCRIPT_URL = SCRIPT_URL
    response = client.get("/simple", HTTP_HOST="example.com")
    assert response.status_code == 200
    assertInHTML(
        f'<script defer src="{SCRIPT_URL}"></script>',
        response.content.decode(),
    )
