import re

from django.template import Context
from django.template.base import Parser, Template
from django.utils.regex_helper import _lazy_re_compile

attribute_re = _lazy_re_compile(
    r"""
    (?P<attr>
        [\w\-\:\@\.\_]+
    )
    (?P<sign>
        \+?=
    )
    (?P<value>
        ['"]? # start quote
            [^"']*
        ['"]? # end quote
    )
    """,
    re.VERBOSE | re.UNICODE,
)

kwarg_re = _lazy_re_compile(
    r"""
    (?:
        (
            [\w\-\:\@\.\_]+ # attribute name
        )
        =
    )?
    (.+) # value
    """,
    re.VERBOSE,
)


def token_kwargs(bits: list[str], parser: Parser) -> dict:
    """
    Parse token keyword arguments and return a dictionary of the arguments
    retrieved from the ``bits`` token list.

    `bits` is a list containing the remainder of the token (split by spaces)
    that is to be checked for arguments. Valid arguments are removed from this
    list.

    There is no requirement for all remaining token ``bits`` to be keyword
    arguments, so return the dictionary as soon as an invalid argument format
    is reached.
    """
    if not bits:
        return {}
    match = kwarg_re.match(bits[0])
    kwarg_format = match and match[1]
    if not kwarg_format:
        return {}

    kwargs = {}
    while bits:
        match = kwarg_re.match(bits[0])
        if not match or not match[1]:
            return kwargs
        key, value = match.groups()
        del bits[:1]

        kwargs[key] = parser.compile_filter(value)
    return kwargs


def render_partial_from_template(template: Template, context: Context, partial_name: str) -> str:
    """Render a partial from a template."""

    def _get_partial_from_nodelist(nodelist: list) -> str:
        """Recursively get a partial from a list of nodes."""
        from django_component_kit.nodes import PartialNode

        for node in nodelist:
            if isinstance(node, PartialNode) and node.partial_name == partial_name:
                return node.render(context, force=True)
            for sub_nodelist in node.child_nodelists:
                try:
                    return _get_partial_from_nodelist(getattr(node, sub_nodelist))
                except AttributeError:
                    continue
        raise AttributeError(f"Could not find partial with name '{partial_name}'")

    try:
        return _get_partial_from_nodelist(template.nodelist)
    except AttributeError:
        return ""
