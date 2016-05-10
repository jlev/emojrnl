from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

from emojrnl.emoji import EMOJI


@register.filter
@stringfilter
def emoji(alias):
    return EMOJI.get(alias, '')
