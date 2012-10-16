from django import template

register = template.Library()

@register.inclusion_tag('django_shared/form_row.html')
def form_row(field):
    return {'field': field}