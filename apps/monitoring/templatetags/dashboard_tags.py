import datetime

from django import template

register = template.Library()


@register.filter
def add_days(value, days):
    if not value:
        return value
    return value + datetime.timedelta(days=int(days))