from django import template

register = template.Library()


@register.filter
def capsentence(value):
    """
    Capitalise the first letter of each sentence in a string. Currently,
    only matched the period punctuation.
    """
    value = value.lower()
    return ". ".join([sentence.capitalize() for sentence in value.split(". ")])


@register.filter
def capfirst(value, force_lower=False):
    """Capitalizes only the first letter in a string"""
    if force_lower:
        return '%s%s' % (value[:1].upper(), value[1:].lower())
    else:
        return value.capitalize()
