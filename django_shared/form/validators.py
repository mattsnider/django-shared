from django.core.exceptions import ValidationError

def validate_format(value):
    format = value.lower()
    if 'xml' != format and 'json' != format:
        raise ValidationError(u'"%s" is not a valid format ("xml" or "json")' % format)