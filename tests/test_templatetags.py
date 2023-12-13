from django.template import TemplateSyntaxError, Template, Context, NodeList, Node, Library
from django.template.base import TextNode, FilterExpression, VariableNode
from django.test import TestCase

from django_component_kit.attributes import AttributeBag
from django_component_kit.nodes import SlotNodeList, SlotNode, ComponentNode, INNER_SLOT_NAME
from django_component_kit import component_block_tag

register = Library()


class DoComponentTest(TestCase):
    """Tests the parsing and interpretation of component tags."""

    def setUp(self) -> None:
        register.tags.clear()

    def test_parses_component(self):
        """Parses a component tag and checks the resulting node."""

        @register.tag("hello")
        @component_block_tag(Template("""<p>hello</p>"""))
        def dummy():
            return {}

        template = Template("""{% hello %}{% endhello %}""")
        node = template.nodelist[0]

        self.assertTrue(isinstance(node, ComponentNode))
        self.assertEqual(node.name, "hello")
        self.assertEqual(node.unresolved_attributes, {})
        self.assertEqual(node.slots, {INNER_SLOT_NAME: NodeList()})

    def test_interprets_attributes_with_no_value_as_true(self):
        """Interprets attributes with no value as True."""

        @register.tag("hello")
        @component_block_tag(Template("""<p>hello</p>"""))
        def dummy():
            return {}

        template = Template("""{% hello required %}{% endhello %}""")
        node = template.nodelist[0]
        context = Context()

        self.assertEqual(
            {key: value.resolve(context) for key, value in node.unresolved_attributes.items()},
            {
                "required": True,
            },
        )

    def test_adds_non_slot_child_nodes_to_default_slot(self):
        """Adds non-slot child nodes to the default slot."""

        @register.tag("hello")
        @component_block_tag(Template("""<p>hello</p>"""))
        def dummy():
            return {}

        template = Template("""{% hello %}Hello{% endhello %}""")
        node = template.nodelist[0]
        self.assertTrue(INNER_SLOT_NAME in node.slots)

        default_slot = node.slots[INNER_SLOT_NAME][0]
        self.assertEqual(default_slot.name, INNER_SLOT_NAME)
        self.assertEqual(default_slot.unresolved_attributes, {})
        self.assertEqual(len(default_slot.nodelist), 1)
        self.assertEqual(default_slot.special, {})

    def test_passes_special_attributes_to_default_slot(self):
        """Passes special attributes to the default slot."""

        @register.tag("hello")
        @component_block_tag(Template("""<p>hello</p>"""))
        def dummy():
            return {}

        template = Template("""{% hello class="foo" :let="user" %}Hello{% endhello %}""")
        node = template.nodelist[0]
        context = Context()
        self.assertEqual(
            {key: value.resolve(context) for key, value in node.unresolved_attributes.items()},
            {
                "class": "foo",
            },
        )

        default_slot = node.slots[INNER_SLOT_NAME][0]
        self.assertEqual(
            {key: value.resolve(context) for key, value in default_slot.special.items()},
            {
                ":let": "user",
            },
        )

    def test_parses_slots(self):
        """Parses slots within a component tag."""

        @register.tag("hello")
        @component_block_tag(Template("""<p>hello</p>"""))
        def dummy():
            return {}

        template = Template("""{% hello %}{% slot title %}{% endslot %}Hello{% endhello %}""")

        node = template.nodelist[0]

        self.assertEqual(len(node.slots["title"]), 1)
        self.assertEqual(len(node.slots[INNER_SLOT_NAME]), 1)


class DoSlotTest(TestCase):
    """Tests the parsing and interpretation of slot tags."""

    def test_parses_slot(self):
        """Parses a slot tag and checks the resulting node."""
        template = Template("""{% slot title %}{% endslot %}""")

        node = template.nodelist[0]

        self.assertTrue(isinstance(node, SlotNode))
        self.assertEqual(node.name, "title")
        self.assertEqual(node.nodelist, NodeList())
        self.assertEqual(node.unresolved_attributes, {})

    def test_parses_slot_with_quoted_name(self):
        """Parses a slot tag with a quoted name."""
        template = Template("""{% slot "title" %}{% endslot %}""")

        node = template.nodelist[0]

        self.assertTrue(isinstance(node, SlotNode))
        self.assertEqual(node.name, "title")

    def test_interprets_attributes_with_no_value_as_true(self):
        """Interprets attributes with no value as True."""
        template = Template("""{% slot title required %}{% endslot %}""")

        node = template.nodelist[0]

        context = Context()

        self.assertEqual(
            {key: value.resolve(context) for key, value in node.unresolved_attributes.items()},
            {
                "required": True,
            },
        )

    def test_splits_special_attributes(self):
        """Splits special attributes from regular attributes."""
        template = Template("""{% slot title class="foo" :let="user" %}{% endslot %}""")

        node = template.nodelist[0]

        context = Context()

        self.assertEqual(
            {key: value.resolve(context) for key, value in node.unresolved_attributes.items()},
            {
                "class": "foo",
            },
        )
        self.assertEqual(
            {key: value.resolve(context) for key, value in node.special.items()},
            {
                ":let": "user",
            },
        )


class SlotNodeListTest(TestCase):
    """Tests the SlotNodeList class."""

    def test_attributes_returns_empty_if_no_elements(self):
        """Returns an empty AttributeBag if there are no elements."""
        self.assertEqual(
            SlotNodeList().attributes,
            AttributeBag(),
        )

    def test_attributes_returns_empty_if_element_doesnt_have_attributes_property(self):
        """Returns an empty AttributeBag if the element doesn't have an attributes property."""
        self.assertEqual(
            SlotNodeList([TextNode("hello")]).attributes,
            AttributeBag(),
        )

    def test_attributes_returns_attributes_of_first_element(self):
        """Returns the attributes of the first element."""
        node = Node()
        node.attributes = {"foo": "bar"}

        self.assertEqual(
            SlotNodeList([node]).attributes,
            {"foo": "bar"},
        )

    def test_attributes_returns_empty_if_multiple_elements(self):
        """Returns an empty AttributeBag if there are multiple elements."""
        node1 = Node()
        node1.attributes = {"foo": "bar"}
        node2 = Node()
        node2.attributes = {"foo": "bar"}

        self.assertEqual(
            SlotNodeList([node1, node2]).attributes,
            {},
        )


class DoRenderSlotTest(TestCase):
    """Tests the rendering of slot tags."""

    def test_raises_if_no_arguments_passed(self):
        """Raises an error if no arguments are passed."""
        with self.assertRaises(TemplateSyntaxError):
            Template(
                """
                {% render_slot %}
                """
            ).render(Context({}))

    def test_raises_if_more_than_two_arguments_passed(self):
        """Raises an error if more than two arguments are passed."""
        with self.assertRaises(TemplateSyntaxError):
            Template(
                """
                {% render_slot foo bar baz %}
                """
            ).render(Context({}))

    def test_renders_slot(self):
        """Renders a slot tag."""
        self.assertHTMLEqual(
            Template(
                """
                {% render_slot inner_block %}
                """
            ).render(
                Context(
                    {
                        "inner_block": SlotNode(
                            nodelist=NodeList(
                                [
                                    TextNode("Hello, world!"),
                                ],
                            ),
                        ),
                    }
                )
            ),
            """
            Hello, world!
            """,
        )

    def test_ignores_nonexistant_variables(self):
        """Ignores non-existent variables."""
        self.assertHTMLEqual(
            Template(
                """
                {% render_slot foo %}
                """
            ).render(Context({})),
            """
            """,
        )

    def test_renders_slot_with_argument(self):
        """Renders a slot tag with an argument."""
        slot_node = SlotNode(
            special={
                ":let": FilterExpression('"user"', None),
            },
            nodelist=NodeList(
                [
                    VariableNode(FilterExpression("user.name", None)),
                ]
            ),
        )

        self.assertHTMLEqual(
            Template(
                """
                {% render_slot inner_block arg %}
                """
            ).render(
                Context(
                    {
                        "inner_block": SlotNodeList(
                            [
                                slot_node,
                            ]
                        ),
                        "arg": {
                            "name": "John Doe",
                        },
                    }
                )
            ),
            """
            John Doe
            """,
        )


class DoMergeAttrsTest(TestCase):
    """Tests the merging of attributes."""

    def test_merges_attributes_with_defaults(self):
        """Merges attributes with defaults."""
        self.assertHTMLEqual(
            Template(
                """
                <div {% merge_attrs attributes foo="bar" %}></div>
                """
            ).render(Context({"attributes": {"class": "foo"}})),
            """
            <div class="foo" foo="bar"></div>
            """,
        )

    def test_appends_class(self):
        """Appends the class attribute."""
        self.assertHTMLEqual(
            Template(
                """
                <div {% merge_attrs attributes class="bar" %}></div>
                """
            ).render(Context({"attributes": {"class": "foo"}})),
            """
            <div class="foo bar"></div>
            """,
        )

    def test_appends_other_attributes(self):
        """Appends other attributes."""
        self.assertHTMLEqual(
            Template(
                """
                <div {% merge_attrs attributes data+="bar" %}></div>
                """
            ).render(Context({"attributes": {"data": "foo"}})),
            """
            <div data="foo bar"></div>
            """,
        )

    def test_supports_attributes_with_hyphen(self):
        """Supports attributes with hyphens."""
        self.assertHTMLEqual(
            Template(
                """
                <div {% merge_attrs attributes data-id="bar" %}></div>
                """
            ).render(Context({"attributes": {}})),
            """
            <div data-id="bar"></div>
            """,
        )

    def test_raises_if_no_arguments_passed(self):
        """Raises an error if no arguments are passed."""
        with self.assertRaises(TemplateSyntaxError):
            Template(
                """
                {% merge_attrs %}
                """
            ).render(Context({}))

    def test_raises_if_attributes_are_malformed(self):
        """Raises an error if attributes are malformed."""
        with self.assertRaises(TemplateSyntaxError):
            Template(
                """
                {% merge_attrs attributes foo %}
                """
            ).render(Context({}))
