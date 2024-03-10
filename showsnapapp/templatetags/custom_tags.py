from django import template

register = template.Library()

@register.simple_tag
def break_loop():
    raise StopIteration