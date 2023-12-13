"""
Ready-to-register Django Component Kit tags.
"""
from django.template import TemplateSyntaxError
from django.template.base import Parser, Token

from django_component_kit.attributes import split_attributes
from django_component_kit.nodes import MergeAttrsNode, RenderSlotNode, SlotNode
from django_component_kit.utils import attribute_re, token_kwargs


def do_merge_attrs(parser: Parser, token: Token) -> MergeAttrsNode:
    """
    Merges attributes with the given default and append attributes.

    Usage: {% merge_attrs attributes [attr1=value1 attr2=value2] ... %}
    """
    tag_name, *remaining_bits = token.split_contents()
    if not remaining_bits:
        raise TemplateSyntaxError("'%s' tag takes at least one argument, the attributes" % tag_name)

    attributes = parser.compile_filter(remaining_bits[0])
    attr_list = remaining_bits[1:]

    default_attrs = []
    append_attrs = []
    for pair in attr_list:
        match = attribute_re.match(pair)
        if not match:
            raise TemplateSyntaxError(
                "Malformed arguments to '%s' tag. You must pass the attributes in the form attr=\"value\"." % tag_name
            )
        dct = match.groupdict()
        attr, sign, value = (
            dct["attr"],
            dct["sign"],
            parser.compile_filter(dct["value"]),
        )
        if sign == "=":
            default_attrs.append((attr, value))
        elif sign == "+=":
            append_attrs.append((attr, value))
        else:
            raise TemplateSyntaxError("Unknown sign '%s' for attribute '%s'" % (sign, attr))
    return MergeAttrsNode(attributes, default_attrs, append_attrs)


def do_render_slot(parser: Parser, token: Token) -> RenderSlotNode:
    """
    Renders the content of a slot.

    Usage: {% render_slot slot [argument] %}
    """
    tag_name, *remaining_bits = token.split_contents()
    if not remaining_bits:
        raise TemplateSyntaxError("'%s' tag takes at least one argument, the slot" % tag_name)

    if len(remaining_bits) > 2:
        raise TemplateSyntaxError("'%s' tag takes at most two arguments, the slot and the argument" % tag_name)

    values = [parser.compile_filter(bit) for bit in remaining_bits]

    if len(values) == 2:
        [slot, argument] = values
    else:
        slot = values.pop()
        argument = None

    return RenderSlotNode(slot, argument)


def do_slot(parser: Parser, token: Token) -> SlotNode:
    """
    Defines a slot with the given name and attributes.

    Usage: {% slot "slot_name" [attr1=value1 attr2=value2] ... %} ... {% endslot %}
    """
    tag_name, *remaining_bits = token.split_contents()

    if len(remaining_bits) < 1:
        raise TemplateSyntaxError("'%s' tag takes at least one argument, the slot name" % tag_name)

    slot_name = remaining_bits.pop(0).strip('"')

    # Bits that are not keyword args are interpreted as `True` values
    all_bits = [bit if "=" in bit else f"{bit}=True" for bit in remaining_bits]
    raw_attributes = token_kwargs(all_bits, parser)
    special, attrs = split_attributes(raw_attributes)

    nodelist = parser.parse(("endslot",))
    parser.delete_first_token()

    return SlotNode(name=slot_name, nodelist=nodelist, unresolved_attributes=attrs, special=special)
