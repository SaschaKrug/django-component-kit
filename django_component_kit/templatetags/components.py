"""
Django template tags for django_component_kit.
"""
from django import template

from django_component_kit.tags import do_merge_attrs, do_render_slot, do_slot, do_partial


register = template.Library()
register.tag("merge_attrs", do_merge_attrs)
register.tag("render_slot", do_render_slot)
register.tag("slot", do_slot)
register.tag("partial", do_partial)
