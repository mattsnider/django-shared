from classytags.arguments import Argument
from classytags.core import Tag, Options
from django import template

register = template.Library()


class NumberCompareAbstract(Tag):
    """
    Abstract class for comparing two numbers.
    """
    options = Options(
        Argument('a'),
        Argument('b'),
    )

    def render_tag(self, context, **kwargs):
        return self.compare(kwargs['a'], kwargs['b'])

    def compare(self, a, b):
        """
        The method you should override in your custom tags
        """
        raise NotImplementedError


class Max(NumberCompareAbstract):
    """
    Applies the 'max' function against the two values.
    """
    name = 'max'

    def compare(self, a, b):
        return max(a, b)
register.tag(Max)


class Min(NumberCompareAbstract):
    """
    Applies the 'min' function against the two values.
    """
    name = 'min'

    def compare(self, a, b):
        return min(a, b)
register.tag(Min)
