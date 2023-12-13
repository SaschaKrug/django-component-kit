from django.test import TestCase
from django.utils.safestring import mark_safe, SafeString

from django_component_kit.attributes import (
    AttributeBag,
    attributes_to_string,
    merge_attributes,
    split_attributes,
    normalize_class,
    append_attributes,
)


class AttributeBagTest(TestCase):
    def test_str_converts_to_string(self):
        """Converts AttributeBag to string representation."""
        self.assertEqual(
            str(AttributeBag({"foo": "bar"})),
            'foo="bar"',
        )


class AttributesToStringTest(TestCase):
    def test_simple_attribute(self):
        """Converts attributes dictionary to string representation."""
        self.assertEqual(
            attributes_to_string({"foo": "bar"}),
            'foo="bar"',
        )

    def test_multiple_attributes(self):
        """Converts multiple attributes dictionary to string representation."""
        self.assertEqual(
            attributes_to_string({"class": "foo", "style": "color: red;"}),
            'class="foo" style="color: red;"',
        )

    def test_escapes_special_characters(self):
        """Escapes special characters in attributes values."""
        self.assertEqual(
            attributes_to_string({"x-on:click": "bar", "@click": "'baz'"}),
            'x-on:click="bar" @click="&#x27;baz&#x27;"',
        )

    def test_does_not_escape_special_characters_if_safe_string(self):
        """Does not escape special characters if attribute value is a SafeString."""
        self.assertEqual(
            attributes_to_string({"foo": mark_safe("'bar'")}),
            "foo=\"'bar'\"",
        )

    def test_result_is_safe_string(self):
        """The result of attributes_to_string is a SafeString."""
        result = attributes_to_string({"foo": mark_safe("'bar'")})
        self.assertTrue( isinstance(result, SafeString))

    def test_attribute_with_no_value(self):
        """Handles attribute with no value."""
        self.assertEqual(
            attributes_to_string({"required": None}),
            "",
        )

    def test_attribute_with_false_value(self):
        """Handles attribute with False value."""
        self.assertEqual(
            attributes_to_string({"required": False}),
            "",
        )

    def test_attribute_with_true_value(self):
        """Handles attribute with True value."""
        self.assertEqual(
            attributes_to_string({"required": True}),
            "required",
        )


class MergeAttributesTest(TestCase):
    def test_merges_attributes(self):
        """Merges two attribute dictionaries."""
        self.assertEqual(
            merge_attributes({"foo": "bar"}, {"bar": "baz"}),
            {"foo": "bar", "bar": "baz"},
        )

    def test_overwrites_attributes(self):
        """Overwrites attributes in the first dictionary with the second dictionary."""
        self.assertEqual(
            merge_attributes({"foo": "bar"}, {"foo": "baz", "data": "foo"}),
            {"foo": "baz", "data": "foo"},
        )

    def test_normalizes_classes(self):
        """Normalizes class attributes by combining them."""
        self.assertEqual(
            merge_attributes({"foo": "bar", "class": "baz"}, {"class": "qux"}),
            {"foo": "bar", "class": "baz qux"},
        )

    def test_merge_multiple_dicts(self):
        """Merges multiple attribute dictionaries."""
        self.assertEqual(
            merge_attributes(
                {"foo": "bar"},
                {"class": "baz"},
                {"id": "qux"},
            ),
            {"foo": "bar", "class": "baz", "id": "qux"},
        )

    def test_returns_attribute_bag(self):
        """The result of merge_attributes is an AttributeBag."""
        result = merge_attributes(AttributeBag({"foo": "bar"}), {})
        self.assertTrue(isinstance(result, AttributeBag))


class SplitAttributesTest(TestCase):
    def test_returns_normal_attrs(self):
        """Returns normal attributes from the dictionary."""
        self.assertEqual(split_attributes({"foo": "bar"}), ({}, {"foo": "bar"}))

    def test_returns_special_attrs(self):
        """Returns special attributes from the dictionary."""
        self.assertEqual(split_attributes({":let": "bar"}), ({":let": "bar"}, {}))

    def test_splits_attrs(self):
        """Splits normal and special attributes from the dictionary."""
        self.assertEqual(split_attributes({":let": "fruit", "foo": "bar"}), ({":let": "fruit"}, {"foo": "bar"}))


class AppendAttributesTest(TestCase):
    def test_single_dict(self):
        """Appends attributes from a single dictionary."""
        self.assertEqual(
            append_attributes({"foo": "bar"}),
            {"foo": "bar"},
        )

    def test_appends_dicts(self):
        """Appends attributes from multiple dictionaries."""
        self.assertEqual(
            append_attributes({"class": "foo"}, {"id": "bar"}, {"class": "baz"}),
            {"class": "foo baz", "id": "bar"},
        )


class NormalizeClassTest(TestCase):
    def test_str(self):
        """Normalizes class attribute when given a string."""
        self.assertEqual(
            normalize_class("foo"),
            "foo",
        )

    def test_list(self):
        """Normalizes class attribute when given a list."""
        self.assertEqual(
            normalize_class(["foo", "bar"]),
            "foo bar",
        )

    def test_nested_list(self):
        """Normalizes class attribute when given a nested list."""
        self.assertEqual(
            normalize_class(["foo", ["bar", "baz"]]),
            "foo bar baz",
        )

    def test_tuple(self):
        """Normalizes class attribute when given a tuple."""
        self.assertEqual(
            normalize_class(("foo", "bar")),
            "foo bar",
        )

    def test_dict(self):
        """Normalizes class attribute when given a dictionary."""
        self.assertEqual(
            normalize_class({"foo": True, "bar": False, "baz": None}),
            "foo",
        )

    def test_combined(self):
        """Normalizes class attribute when given a combination of different types."""
        self.assertEqual(
            normalize_class(
                [
                    "class1",
                    ["class2", "class3"],
                    {
                        "class4": True,
                        "class5": False,
                        "class6": "foo",
                    },
                ]
            ),
            "class1 class2 class3 class4 class6",
        )
