from django import template

register = template.Library()

@register.filter
def formatnumber(value):
    try:
        value = float(value)
        return f'{value:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return value
