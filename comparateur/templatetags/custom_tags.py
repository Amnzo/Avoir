from django import template

register = template.Library()

@register.simple_tag
def set_var(value=None):
    return value

@register.simple_tag(takes_context=True)
def increment(context, var_name):
    context[var_name] += 1
    return ''
