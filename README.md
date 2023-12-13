# Django Component Kit
Introducing a Python library for Django that is small, non-intrusive, and provides all the necessary tools to build components in a flexible manner, following the Django approach.



# Getting Started
## Installation
```bash
pip install django-component-kit
```

## Add to your project
There are two different ways you can use the library:

### Adding it as an Django App
#### Add to `settings.py`
```python
INSTALLED_APPS = [
    ...,
    'django_component_kit',
]
```

### Add to template build-ins in `settings.py`
```python
TEMPLATES = [
    {
        "OPTIONS": {
            "builtins": ["django_component_kit.templatetags.components"],
        },
    },
]
```
