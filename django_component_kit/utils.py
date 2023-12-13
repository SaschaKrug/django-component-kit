import re

from django.template.base import Parser
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
