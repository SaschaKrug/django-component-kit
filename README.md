# Django Component Kit

Introducing Django Component Kit, a small and non-intrusive Python library for Django that provides all the necessary
tools to build flexible components in a Django-like manner.

By using standard Python decorators and Django custom template tags, you can easily create highly flexible components
with IDE-friendly tooling.

## Example
### Template Tag
```python
# templatetags/mycomponents.py
from django import template
from django.template.loader import get_template
from django_component_kit import component_block_tag

register = template.Library()


@register.tag
@register.tag('endcard')
@component_block_tag(get_template("mycomponents/card.html"))
def card(title: str) -> dict:
    return dict(title=title)
```

## Template
```html
<!-- templates/mycomponents/card.html -->
{% load django_component_kit %}

<div class="card shadow-lg p-3 bg-body rounded">
    <div class="card-header">
        <h> class="card-title">{{ title }}}</h>
    </div>
    <div class="card-body">
        {% render_slot slots.children %}
    </div>
    <div class="card-footer text-muted">
        <div class="links float-end">
            {% render_slot slots.footer %}
        </div>
    </div>
</div>
```

## Usage
```html
<!-- templates/myapp/index.html -->
<div>
  {% card title="Card title" %}
    <p class="card-text">Foo</p>
    {% slot footer %}
      <a href="#" class="card-link">Card link</a>
    {% endslot %}
  {% endcard %}
</div>
```

## Result
```html
<!-- https://myapp.com/index.html -->
<div>
    <div class="card mb-3 shadow-lg p-3 bg-body rounded">
        <div class="card-header">
            <h class="card-title">Card title</h>
        </div>
        <div class="card-body">
            <p class="card-text">Foo</p>
        </div>
        <div class="card-footer text-muted">
            <div class="links float-end">
                <a href="#" class="card-link">Card link</a>
            </div>
        </div>
    </div>
</div>
```

## But Why?

While exploring different frontend frameworks and concepts, I came across HTMX and Alpine.js, which I fell in love with
for creating nice frontends in Django. However, the Django Templating System lacked proper support for components,
making it difficult to use these frameworks effectively. Existing third-party libraries for components in Django were
either outdated or felt more like frameworks than libraries, requiring a steep learning curve.

To address this, I decided to create Django Component Kit, which is based on the unobtrusive and flexible
django-web-components library developed by Mihail Cristian Dumitru Xzya. I aimed to integrate it into my component
library and enhance its feature set.

During the integration process, I realized that significant modifications were needed to align with my vision. I ended
up creating Django Component Kit, which shares some codebase with django-web-components but adopts a different approach
to component development.

# Getting Started

## Installation

```bash
pip install django-component-kit
```

## Adding to Your Project

There are two ways to use the library:

### Adding as a Django App

This method allows for deeper integration but requires some standard Django configuration.

#### Add the app to `settings.py`

```python
# myproject/settings.py
INSTALLED_APPS = [
    ...,
    'django_component_kit',
]
```

### Optional: Adding as a Built-in Component

This method allows you to add the component as a built-in in your project's `settings.py` without forcing others to
install it.

```python
# myproject/settings.py
TEMPLATES = [
    {
        "OPTIONS": {
            "builtins": ["django_component_kit.templatetags.components"],
        },
    },
]
```

### Adding to Your Own Component Library

If you want to use Django Component Kit primarily to build your own components, you can add it to your component library
without requiring others to install it.

#### Add to your component library `templatetags/mycomponents.py`

```python
# templatetags/mycomponents.py
from django import template
from django_component_kit.tags import do_merge_attrs, do_render_slot, do_slot

register = template.Library()
register.tag("merge_attrs", do_merge_attrs)
register.tag("render_slot", do_render_slot)
register.tag("slot", do_slot)
```

That's it! Now you can start creating your own components.

# Usage

## Inline Components

Inline components are simple elements without any children. They allow you to add attributes and are commonly used for
form fields or other end elements.

### 1. Register a function with `@component_inline_tag()`

Use the `@component_inline_tag()` decorator to register a function as a custom tag.

```python
# templatetags/mycomponents.py
from django import template
from django.forms import Field
from django.template.loader import get_template
from django_component_kit import component_inline_tag

register = template.Library()


@register.tag
@component_inline_tag(get_template("mycomponents/text_input.html"))
def text_input(field: Field) -> dict:
    """Component for rendering a text input."""
    return dict(field=field)
```

### 2. Create a template for the component

Create a template that defines how the component should be rendered. Inline components receive the context provided by
the function and the parameters bundled into the `attributes` variable.

```html
<!-- templates/mycomponents/text_input.html -->
{% load django_component_kit %}

<div class="mb-3">
    <label for="{{ field.id_for_label }}" class="form-label">{{ field.label }}</label>
    <input type="text" id="{{ field.id_for_label }}" name="{{ field.name }}" class="form-control">
    <div class="form-text text-muted">{{ field.help_text }}</div>
</div>
```

## 3. Use the component in a template

Use the component in your template by calling the registered tag and passing the required parameters.

```html
<!-- templates/myapp/index.html -->
<form>
    {% text_input field=form.field %}
    <button type="submit">Submit</button>
</form>
```

## Result

The component will be rendered with the provided attributes:

```html
<!-- https://myapp.com/index.html -->
<form>
    <div class="mb-3">
        <label for="text_1" class="form-label">Foo</label>
        <input type="text" id="text_1" name="Bar" class="form-control">
        <div class="form-text text-muted">Batz</div>
    </div>
    <button type="submit">Submit</button>
</form>
```

## Details

- The `@component_inline_tag()` decorator should be placed between the `@register.tag` decorator and the function
  definition.
- The decorator requires a template for rendering the component.
- All parameters passed to the function will be extracted from the context for further processing.
- The function must return a dictionary that will be used as the context for rendering the inline component.
- Parameters passed to the tag will be bundled into the `attributes` variable in the template context.
- The `register.tag()` function provides IDE support for jumping from template tags to functions and viewing component
  usage.
- Providing a parameter without a key will treat it as a boolean value. See `attributes` for more details.

## Block Components

Block components behave similarly to inline components but allow for the inclusion of child elements, making them
suitable for more complex components.

### 1. Register a function with `@component_block_tag()`

Use the `@component_block_tag()` decorator to register a function as a custom tag.

```python
# templatetags/mycomponents.py
from django import template
from django.template.loader import get_template
from django_component_kit import component_block_tag

register = template.Library()


@register.tag
@register.tag('endcard')
@component_block_tag(get_template("mycomponents/card.html"))
def card() -> dict:
    """Component for rendering a card."""
    return dict()
```

### 2. Create a template for the component

Create a template that defines how the component should be rendered. Block components allow for the use of slots, which
are defined using the `slot` tag.

```html
<!-- templates/mycomponents/card.html -->
{% load django_component_kit %}

<div {% merge_attrs attributes class="card shadow-lg p-3 bg-body rounded" %}>
    {% if slots.header %}
    <div class="card-header">
        {% render_slot slots.header %}
    </div>
    {% endif %}
    <div class="card-body">
        {% render_slot slots.children %}
    </div>
    {% if slots.footer %}
    <div class="card-footer text-muted">
        <div class="links float-end">
            {% render_slot slots.footer %}
        </div>
    </div>
    {% endif %}
</div>
```

## 3. Use the component in a template

Use the component in your template by calling the registered tag and defining the slots using the `slot` tag.

```html
<!-- templates/myapp/index.html -->
<div>
    {% card class='mb-3' %}
    {% slot header %}
    <h> class="card-title">Card title</h>
    {% endslot %}

    <p class="card-text">Bar</p>

    {% slot footer %}
    <a href="#" class="card-link">Card link</a>
    {% endslot %}
    {% endcard %}
</div>
```

## Result

The component will be rendered with the provided attributes and slots:

```html
<!-- https://myapp.com/index.html -->
<div>
    <div class="card mb-3 shadow-lg p-3 bg-body rounded">
        <div class="card-header">
            <h class="card-title">Card title</h>
        </div>
        <div class="card-body">
            <p class="card-text">Foo</p>
        </div>
        <div class="card-footer text-muted">
            <div class="links float-end">
                <a href="#" class="card-link">Card link</a>
            </div>
        </div>
    </div>
</div>
```

## Details

- All details of inline components apply to block components as well.
- The tag must end with an `endXXX` tag, where `XXX` is the name of the component. Everything enclosed within the tags
  will be added to the component.
- The `endXXX` tag registration is optional but provides autocompletion and linking between the component and its usage.
- The `slots` variable is a dictionary that contains all provided slots and a base slot called `children`, which
  collects all child elements not inside a slot.
- Missing variables within the template will not be rendered.
- Use the `render_slot` tag to render the slots.
- Use the `{% slot %}` tag to define a slot. It must end with an `{% endslot %}` tag. Everything enclosed within the
  tags will be added to the slot.
- Use `merge_attrs` to merge attributes together.

# Passing Data to Components

You can pass data to components using keyword arguments, which accept hardcoded values or variables:

```html
{% with error_message="Something bad happened!" %}
{% alert type="error" message=error_message %}
{% endwith %}
```

All attributes will be added to the `attributes` dictionary, which will be available in the template context:

```json
{
  "attributes": {
    "type": "error",
    "message": "Something bad happened!"
  }
}
```

You can then access the attributes from the component's template:

```html

<div class="alert alert-{{ attributes.type }}">
    {{ attributes.message }}
</div>
```

### Rendering All Attributes

You can also render all attributes directly using `{{ attributes }}`. For example, if you have the following component:

```html
{% alert id="alerts" class="font-bold" %} ... {% endalert %}
```

You can render all attributes using:

```html

<div {{ attributes }}>
    <!-- Component content -->
</div>
```

This will render the following HTML:

```html

<div id="alerts" class="font-bold">
    <!-- Component content -->
</div>
```

### Attributes with Special Characters

You can pass attributes with special characters (`[@:_-.]`) as well as attributes with no value:

```html
{% button @click="handleClick" data-id="123" required %} ... {% endbutton %}
```

This will result in the following dictionary available in the context:

```python
{
    "attributes": {
        "@click": "handleClick",
        "data-id": "123",
        "required": True,
    }
}
```

And will be rendered by `{{ attributes }}` as `@click="handleClick" data-id="123" required`.

### Default/Merged Attributes

You can specify default values for attributes or merge additional values into some of the component's attributes using
the `merge_attrs` tag:

```html

<div {% merge_attrs attributes class="alert" role="alert" %}>
    <!-- Component content -->
</div>
```

If we assume this component is used like this:

```html
{% alert class="mb-4" %} ... {% endalert %}
```

The final rendered HTML of the component will be:

```html

<div class="alert mb-4" role="alert">
    <!-- Component content -->
</div>
```

### Non-Class Attribute Merging

When merging attributes that are not `class` attributes, the values provided to the `merge_attrs` tag will be considered
the "default" values of the attribute. These attributes will not be merged with injected attribute values but will be
overwritten. For example, a `button` component's implementation may look like this:

```html

<button {% merge_attrs attributes type="button" %}>
    {% render_slot slots.inner_block %}
</button>
```

To render the button component with a custom `type`, you can specify it when consuming the component. If no type is
specified, the default `button` type will be used:

```html
{% button type="submit" %} Submit {% endbutton %}
```

The rendered HTML of the `button` component in this example would be:

```html

<button type="submit">
    Submit
</button>
```

### Appendable Attributes

You can treat other attributes as "appendable" by using the `+=` operator:

```html

<div {% merge_attrs attributes data-value+="some-value" %}>
    <!-- Component content -->
</div>
```

If we assume this component is used like this:

```html
{% alert data-value="foo" %} ... {% endalert %}
```

The rendered HTML will be:

```html

<div data-value="foo some-value">
    <!-- Component content -->
</div>
```

### Manipulating the Attributes

By default, all attributes are added to an `attributes` dictionary inside the context. However, in some cases, you may
want to separate certain attributes from the `attributes` dictionary. For example, you may want to render an `alert`
component with a custom `id` or `class` attribute, while still being able to use additional attributes internally.

To achieve this, you can manipulate the context in your component's function to provide a better API for using the
component:

```python
# templatetags/mycomponents.py
from django import template
from django.template.loader import get_template
from django_component_kit import component_block_tag

register = template.Library()


@register.tag
@register.tag('endalert')
@component_block_tag(get_template("mycomponents/alert.html"))
def alert(attributes: dict) -> dict:
    """Component for rendering an alert."""
    dismissible = attributes.pop("dismissible", False)
    return {
        "dismissible": dismissible,
        "attributes": attributes
    }
```

The component's template can then be modified to handle the new structure:

```html
<!-- templates/mycomponents/alert.html -->
<div {{ attributes }}>
    {% render_slot slots.children %}
    {% if dismissible %}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    {% endif %}
</div>
```

This allows you to render the component like this:

```html
{% alert id="my-alert" class="my-class" dismissible %}
This is an alert.
{% endalert %}
```

The rendered HTML will be:

```html

<div id="my-alert" class="my-class">
    This is an alert.
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
</div>
```

# Slots

Slots allow you to pass additional content to your components. The `slots` context variable is passed to your components
and consists of a dictionary with the slot name as the key and the slot content as the value. You can render the slots
inside your components using the `render_slot` tag.

### The Default Slot

By default, any content not enclosed within a named slot will be added to the default slot, which is called `children`.
You can render this slot using the `render_slot` tag inside your component.

### Named Slots

Sometimes a component may need to render multiple named slots in different locations. You can define named slots using
the `slot` tag and render them using the `render_slot` tag.

### Scoped Slots

Slots also have access to the component's context, allowing you to pass variables to the slot content. You can use
the `:let` attribute to bind the value passed to `render_slot` to a variable within the slot content.

### Nested Components

You can nest components to create more complex elements. This allows you to build reusable and modular components.

# Partials
*Since: 0.2.0*

Partials allow you to render only a part of a template. This can be useful, when you have a complex component which
consists of multiple subcomponents. Like a card with actions, which are used to manipulate the content of the card.
Usually you would use one template for the card and then one for each kind of action component. This is fine,
until you have javascript, HTMX or AlpineJS logic inside of these components, which must reference each other.
That's indeed possible, but the DX is bad, as you don't know what functions or attributes you can use and what they do.
In this case partials are coming in for the rescue. Just put all subcomponents into a partial inside the main
component. With this, even IDE support is present for seeing where which function is being called.

Hint: The partials are cached, so you can use a lot of them without performance impact.

*Since: 0.3.0*
When a template is rendered as a partial, the 'is_partial' attribute is set.
Partials can be rendered directly via the `PartialResponse` class.

## Usage
You can directly write the partial inside the main component at any point in the template. Only if the `inline` argument
is set to `True`, the partial will be rendered inside the main component. If not, it will be hidden. The example uses
AlpineJS for demonstration purposes:

```html
<!-- templates/mycomponents/card.html -->
<div class="card" x-data="{ color: text-success }">
  <div class="card-header">
    {% render_slot slots.header %}
    {% partial "toggle_color_action" %}
      <button
              type="button"
              class="btn-close"
              aria-label="Toggle"
              @click="color=color==='text-success' ? 'text-danger' : 'text-success'"
      >
        Toggle color
      </button>
    {% endpartial %}
  </div>
  <div class="card-body" :class="color">
    {% render_slot slots.children %}
  </div>
</div>
```

```python
# templatetags/mycomponents.py
from django import template
from django.template.loader import get_template
from django_component_kit import component_block_tag, component_inline_tag

register = template.Library()

@register.tag
@register.tag('endcard')
@component_block_tag(get_template("mycomponents/card.html"))
def card() -> dict:
    return dict()


@register.tag
@component_inline_tag(get_template("mycomponents/card.html"), partial="toggle_color_action")
def toggle_color_action() -> dict:
    return dict()
```

```html
<!-- templates/index.html -->
{% card %}
  {% slot header %}
    {% toggle_color_action %}
  {% endslot %}
  <p>This is a text</p>
{% endcard %}
```

### Result
```html
<div class="card" x-data="{ color: text-success }">
  <div class="card-header">
    <button
            type="button"
            class="btn-close"
            aria-label="Toggle"
            @click="color=color==='text-success' ? 'text-danger' : 'text-success'"
    >
      Toggle color
    </button>
  </div>
  <div class="card-body" :class="color">
    <p>This is a text</p>
  </div>
</div>
```

# Assets
*Since: 0.3.0*

When registering a component, you can assign JS oder CSS assets to it. You can do this using the `js` or `css` arguments
in the `component_inline_tag` or `component_block_tag`. They will be ordered in the order they are registered,
CSS in front of JS. Duplicates are removed. You can then use the assets via the `assets` tag.

*Hint:* If you want to modify the assets, you can import the `assets` object and modify it before usage.

## Usage
```python
# templatetags/mycomponents.py
from django import template
from django.template.loader import get_template
from django_component_kit import component_inline_tag

register = template.Library()

@register.tag
@component_inline_tag(get_template("mycomponents/card.html"), js=["myjs.js"])
def card() -> dict:
    return dict()
```

```html
<!-- templates/index.html -->
{% assets %}
```

### Result
```html
<script src="myjs.js" defer></script>
```

# Contribution

If you have any questions, suggestions, or feedback, feel free
to [open an issue](https://github.com/SaschaKrug/django-component-kit/issues/new).

## Development and Testing

To set up the development environment and run the tests, follow these steps:

1. Install the dependencies using `poetry install`.
2. Activate the environment using `poetry shell`.
3. Run the tests using `poe test`.
4. Run the linting using `poe lint`.

# What's Next?

The current goal is to stabilize Django Component Kit and ensure it works as expected in different applications and use
cases. Future plans include adding more features to the library, but there is no specific roadmap at the moment. One
potential addition could be support for assets, although the need for this is diminished with the popularity of
Tailwind, HTMX, and Alpine.js.
