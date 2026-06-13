from django import template

from plausible.contrib.wagtail.models import PlausibleSettings
from plausible.templatetags.plausible import render_plausible

register = template.Library()


@register.simple_tag(takes_context=True)
def plausible(context):
    plausible_settings = PlausibleSettings.for_request(context["request"])
    return render_plausible(plausible_settings.script_url)
