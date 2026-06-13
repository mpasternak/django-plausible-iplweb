from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class PlausibleSettings(BaseSiteSetting):
    script_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Full Plausible script URL, e.g. https://plausible.io/js/pa-XXXXXXXX.js",
    )

    class Meta:
        verbose_name = "Plausible Analytics"
