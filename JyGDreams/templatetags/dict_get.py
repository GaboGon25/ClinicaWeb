from django import template
register = template.Library()

@register.filter
def dict_get(d, k):
    return d.get(k)