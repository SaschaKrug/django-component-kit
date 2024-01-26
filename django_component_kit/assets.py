"""
Assets management for Django Component Kit.
"""
from typing import Iterable
from django.templatetags.static import static


class AssetRegistry:
    """Registry for assets"""

    def __init__(self):
        self.js = set()
        self.css = set()
        self._string = ""

    def add_js(self, js_list: Iterable[str] | None):
        """Add JS files"""
        self.js.update(js_list or [])

    def add_css(self, css_list: Iterable[str] | None):
        """Add CSS files"""
        self.css.update(css_list or [])

    def as_string(self, refresh: bool = False) -> str:
        """Return cached assets as string"""
        if not self._string or refresh:
            js_list = [f'<script src="{static(js)}" defer></script>' for js in self.js]
            css_list = [f'<link crossorigin="anonymous" href="{static(css)}" rel="stylesheet">' for css in self.css]
            self._string = "\n".join(js_list) + "\n" + "\n".join(css_list)
        return self._string


assets = AssetRegistry()
