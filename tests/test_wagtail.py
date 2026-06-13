import pytest
from pytest_django.asserts import assertInHTML
from wagtail.models import Site

from plausible.contrib.wagtail.models import PlausibleSettings

SCRIPT_URL = "https://plausible.io/js/pa-WAG999.js"


@pytest.fixture
def plausible_settings():
    return PlausibleSettings.for_site(Site.objects.get())


@pytest.mark.django_db
def test_renders_script_from_site_setting(client, plausible_settings):
    plausible_settings.script_url = SCRIPT_URL
    plausible_settings.save()
    response = client.get("/simple-wagtail")
    assert response.status_code == 200
    assertInHTML(
        f'<script defer src="{SCRIPT_URL}"></script>',
        response.content.decode(),
    )


@pytest.mark.django_db
def test_renders_init_snippet(client, plausible_settings):
    plausible_settings.script_url = SCRIPT_URL
    plausible_settings.save()
    response = client.get("/simple-wagtail")
    assert "plausible.init(" in response.content.decode()


@pytest.mark.django_db
def test_blank_script_url_renders_nothing(client, plausible_settings):
    # script_url defaults to blank -> no tracker emitted
    response = client.get("/simple-wagtail")
    assert response.status_code == 200
    assert "plausible.init(" not in response.content.decode()


@pytest.mark.django_db
def test_global_masks_apply_to_wagtail(client, plausible_settings, settings):
    settings.PLAUSIBLE_URL_MASKS = [
        {"pattern": "^/i/[^/]+", "replacement": "/i/__code__"},
    ]
    plausible_settings.script_url = SCRIPT_URL
    plausible_settings.save()
    response = client.get("/simple-wagtail")
    assert '"replacement": "/i/__code__"' in response.content.decode()


def test_app_label():
    assert PlausibleSettings._meta.app_label == "wagtailplausible"
