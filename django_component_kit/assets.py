"""
Assets management for Django Component Kit.
"""
from typing import Iterable


class AssetRegistry:
    """Registry for assets"""

    def __init__(self):
        self.js = set()
        self.css = set()
        self._string = ""

    def add_js(self, js_list: Iterable[str] | None):
        """Add JS files"""
        js_list = js_list or []
        self.js.update([f'<script src="{js}" defer></script>' for js in js_list])

    def add_css(self, css_list: Iterable[str] | None):
        """Add CSS files"""
        css_list = css_list or []
        self.css.update([f'<link crossorigin="anonymous" href="{css}" rel="stylesheet">' for css in css_list])

    def as_string(self, refresh: bool = False) -> str:
        """Return cached assets as string"""
        if not self._string or refresh:
            self._string = "\n".join(self.js) + "\n" + "\n".join(self.css)
        return self._string


assets = AssetRegistry()
