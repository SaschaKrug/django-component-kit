"""
Decorators for Django Component Kit.
"""
from django.template import NodeList, TemplateSyntaxError
from django.template.base import Parser, Token, Template

from django_component_kit.attributes import split_attributes
from django_component_kit.nodes import ComponentNode, SlotNodeList, SlotNode, INNER_SLOT_NAME
from django_component_kit.utils import token_kwargs


def _parse_bits(bits: list, parser: Parser, nodelist: NodeList) -> tuple:
    """Parses the bits of a tag token and extracts attributes and slots."""

    # Bits that are not keyword args are interpreted as `True` values
    all_bits = [bit if "=" in bit else f"{bit}=True" for bit in bits]
    raw_attributes = token_kwargs(all_bits, parser)
    special, attrs = split_attributes(raw_attributes)

    # process the slots
    slots = {}

    # All child nodes that are not inside a slot will be added to a default slot
    default_slot = SlotNode(
        name=INNER_SLOT_NAME,
        nodelist=NodeList(),
        unresolved_attributes={},
        special=special,
    )
    slots[INNER_SLOT_NAME] = SlotNodeList()

    for node in nodelist:
        if isinstance(node, SlotNode):
            slot_name = node.name

            # initialize the slot
            if slot_name not in slots:
                slots[slot_name] = SlotNodeList()

            slots[slot_name].append(node)
        else:
            # otherwise add the node to the default slot
            default_slot.nodelist.append(node)

    # add the default slot only if it's not empty
    if len(default_slot.nodelist) > 0:
        slots[INNER_SLOT_NAME].append(default_slot)

    return slots, attrs


def component_inline_tag(template: Template) -> callable:
    """Decorator for creating an inline component tag."""

    def dec(func):
        def do_component(parser: Parser, token: Token) -> ComponentNode:
            """Creates a ComponentNode for the inline component tag."""
            component_name = func.__name__
            _, *remaining_bits = token.split_contents()
            slots, attrs = _parse_bits(remaining_bits, parser, NodeList())
            return ComponentNode(component_name, attrs, slots, func, template)

        do_component.__name__ = func.__name__
        return do_component

    return dec


def component_block_tag(template: Template) -> callable:
    """Decorator for creating a block component tag."""

    def dec(func):
        def do_component(parser: Parser, token: Token) -> ComponentNode:
            """Creates a ComponentNode for the block component tag."""
            nonlocal template
            nonlocal func
            component_name = [
                key
                for key, value in parser.tags.items()
                if value.__name__ == func.__name__ and not key.startswith("end")
            ][0]
            _, *remaining_bits = token.split_contents()
            if not any([t for t in parser.tokens if component_name in t.contents]):
                raise TemplateSyntaxError(f"Unclosed component block tag: {component_name}")

            nodelist = parser.parse((f"end{component_name}",))
            parser.delete_first_token()
            slots, attrs = _parse_bits(remaining_bits, parser, nodelist)
            return ComponentNode(component_name, attrs, slots, func, template)

        do_component.__name__ = func.__name__
        return do_component

    return dec
