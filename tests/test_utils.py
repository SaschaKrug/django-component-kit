from django.template import Context
from django.template.base import Parser
from django.test import TestCase

from django_component_kit.utils import token_kwargs


class TokenKwargsTest(TestCase):
    def test_parses_raw_value(self):
        """
        Test that token_kwargs function correctly parses raw values.
        """
        p = Parser([])
        context = Context()

        self.assertEqual(
            {key: value.resolve(context) for key, value in token_kwargs(['foo="bar"'], p).items()},
            {
                "foo": "bar",
            },
        )

    def test_parses_key_with_symbols(self):
        """
        Test that token_kwargs function correctly parses keys with symbols.
        """
        p = Parser([])
        context = Context()

        self.assertEqual(
            {
                key: value.resolve(context)
                for key, value in token_kwargs(['x-on:click="bar"', '@click="bar"', 'foo:bar.baz="bar"'], p).items()
            },
            {
                "x-on:click": "bar",
                "@click": "bar",
                "foo:bar.baz": "bar",
            },
        )

    def test_parses_variable_value(self):
        """
        Test that token_kwargs function correctly parses variable values.
        """
        p = Parser([])
        context = Context({"bar": "baz"})

        self.assertEqual(
            {key: value.resolve(context) for key, value in token_kwargs(["foo=bar"], p).items()},
            {
                "foo": "baz",
            },
        )
