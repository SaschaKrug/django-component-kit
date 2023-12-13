"""
Django Component Kit template nodes.
"""
import inspect
from typing import Any

from django.template import TemplateSyntaxError, Context
from django.template.base import FilterExpression, Node, NodeList, Template
from django.utils.safestring import SafeString

from django_component_kit.attributes import AttributeBag, attributes_to_string, merge_attributes, append_attributes

INNER_SLOT_NAME = "inner_slot"


class ComponentNode(Node):
    name: str
    unresolved_attributes: dict
    slots: dict

    def __init__(self, component_name: str, attrs: dict, slots: dict, func: callable, template: Template):
        """Represents a component node in the template."""
        self.name = component_name
        self.unresolved_attributes = attrs
        self.slots = slots
        self.func = func
        self.template = template

    def _resolve_slots(self, context: Context) -> dict:
        """
        Resolves the slots of the component.

        We may need to access the slot's attributes inside the component's template, so we need to resolve them
        We also clone the SlotNodes to make sure we don't have thread-safety issues since
        we are storing the attributes on the node itself.
        """
        slots = {}
        for slot_name, slot_list in self.slots.items():
            # Initialize the slot
            if slot_name not in slots:
                slots[slot_name] = SlotNodeList()

            for slot in slot_list:
                if isinstance(slot, SlotNode):
                    cloned_slot = SlotNode(
                        name=slot.name,
                        nodelist=slot.nodelist,
                        unresolved_attributes=slot.unresolved_attributes,
                        special=slot.special,
                    )
                    # Resolve its attributes so that they can be accessed from the component template
                    cloned_slot.resolve_attributes(context)
                    slots[slot_name].append(cloned_slot)
                else:
                    slots[slot_name].append(slot)
        return slots

    def render(self, context: Context) -> str:
        """Renders the component node."""

        slots = self._resolve_slots(context)
        attributes = AttributeBag({key: value.resolve(context) for key, value in self.unresolved_attributes.items()})
        extra_context = {"attributes": attributes, "slots": slots}

        with context.push(extra_context):
            kwargs = {}
            for key, parameter in inspect.signature(self.func).parameters.items():
                if key != "context":
                    try:
                        if parameter.default == parameter.empty:
                            kwargs[key] = context["attributes"].pop(key)
                        else:
                            kwargs[key] = context["attributes"].pop(key, parameter.default)
                    except KeyError:
                        raise TemplateSyntaxError(f"{self.name} component is missing required argument: {key}")
            with context.update(self.func(**kwargs)):
                return self.template.render(context.flatten())


class SlotNode(Node):
    def __init__(
        self, name: str = None, nodelist: NodeList = None, unresolved_attributes: dict = None, special: dict = None
    ):
        """Represents a slot node in the template."""
        self.name = name or ""
        self.nodelist = nodelist or NodeList()
        self.unresolved_attributes = unresolved_attributes or {}
        self.special = special or {}

        # Will be set by the ComponentNode
        self.attributes = AttributeBag()

    def resolve_attributes(self, context: Context):
        """Resolves the attributes of the slot."""
        self.attributes = AttributeBag(
            {key: value.resolve(context) for key, value in self.unresolved_attributes.items()}
        )

    def render(self, context: Context) -> str:
        """Renders the slot node."""
        attributes = AttributeBag({key: value.resolve(context) for key, value in self.unresolved_attributes.items()})
        extra_context = {"attributes": attributes}

        with context.update(extra_context):
            return self.nodelist.render(context)


class SlotNodeList(NodeList):
    @property
    def attributes(self) -> dict:
        """Returns the attributes of the slot node list."""
        if len(self) == 1 and hasattr(self[0], "attributes"):
            return self[0].attributes
        return AttributeBag()


class RenderSlotNode(Node):
    def __init__(self, slot: FilterExpression, argument: FilterExpression | None = None):
        """Represents a render slot node in the template."""
        self.slot = slot
        self.argument = argument

    def render(self, context: Context) -> str:
        """Renders the render slot node."""
        argument = None
        if self.argument:
            argument = self.argument.resolve(context, ignore_failures=True)

        slot = self.slot.resolve(context, ignore_failures=True)
        if slot is None:
            return ""

        if isinstance(slot, NodeList):
            return SafeString("".join([self.render_slot(node, argument, context) for node in slot]))

        return self.render_slot(slot, argument, context)

    @staticmethod
    def render_slot(slot: SlotNode, argument: Any, context: Context) -> str:
        """Renders the slot."""
        if isinstance(slot, SlotNode):
            let: FilterExpression | None = slot.special.get(":let", None)
            if let:
                let = let.resolve(context, ignore_failures=True)

            # if we were passed an argument and the :let attribute is defined,
            # add the argument to the context with the new name
            if let and argument:
                with context.update({let: argument}):
                    return slot.render(context)
        return slot.render(context)


class MergeAttrsNode(Node):
    def __init__(self, attributes: FilterExpression, default_attrs: list, append_attrs: list):
        """Represents a merge attrs node in the template."""
        self.attributes = attributes
        self.default_attrs = default_attrs
        self.append_attrs = append_attrs

    def render(self, context: Context) -> str:
        """Renders the merge attrs node."""
        bound_attributes: dict = self.attributes.resolve(context)

        default_attrs = {key: value.resolve(context) for key, value in self.default_attrs}
        append_attrs = {key: value.resolve(context) for key, value in self.append_attrs}

        attrs = merge_attributes(default_attrs, bound_attributes)
        attrs = append_attributes(attrs, append_attrs)
        return attributes_to_string(attrs)
