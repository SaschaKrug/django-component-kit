import dataclasses

from django.template import Context
from django.template.base import Template, Node, NodeList


@dataclasses.dataclass
class PartialNode(Node):
    """Represents a partial node in the template."""

    partial_name: str
    inline: bool
    nodelist: NodeList

    def render(self, context: Context, force=False):
        """Set content into context and return empty string"""
        context["is_partial"] = force
        if force or self.inline:
            return self.nodelist.render(context)
        else:
            return ""


class PartialCache:
    def __init__(self):
        """Cache partials."""
        self.cache = {}

    @staticmethod
    def _to_name(template: Template, partial_name: str) -> str:
        """Generate a unique name for the partial."""
        return f"{template.name}:{partial_name}"

    def get(self, template: Template, partial_name: str) -> PartialNode:
        """Get a partial from the cache."""
        name = self._to_name(template, partial_name)
        return self.cache[name]

    def set(self, template: Template, partial_name: str, partial: PartialNode):
        """Set a partial in the cache."""
        name = self._to_name(template, partial_name)
        self.cache[name] = partial


partial_cache = PartialCache()


def render_partial_from_template(template: Template, context: Context, partial_name: str) -> str:
    """Render a partial from a template."""

    def _get_partial_from_nodelist(nodelist: list) -> str:
        """Recursively get a partial from a list of nodes."""
        for node in nodelist:
            if isinstance(node, PartialNode) and node.partial_name == partial_name:
                partial_cache.set(template, partial_name, node)
                return node.render(context, force=True)
            for sub_nodelist in node.child_nodelists:
                try:
                    return _get_partial_from_nodelist(getattr(node, sub_nodelist))
                except AttributeError:
                    continue
        raise AttributeError(f"Could not find partial with name '{partial_name}'")

    try:
        return partial_cache.get(template, partial_name).render(context, force=True)
    except KeyError:
        return _get_partial_from_nodelist(template.nodelist)
