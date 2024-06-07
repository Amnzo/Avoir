from decimal import Decimal
from django import template

register = template.Library()

@register.simple_tag
def set_var(value=None):
    return value

@register.simple_tag(takes_context=True)
def increment(context, var_name):
    context[var_name] += 1
    return ''

@register.filter(name='is_not_zero')
def is_not_zero(value):
    try:
        return Decimal(value).quantize(Decimal('0.01')) != Decimal('0.00')
    except:
        return False
