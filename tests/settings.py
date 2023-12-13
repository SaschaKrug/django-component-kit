from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

INSTALLED_APPS = ["django_component_kit"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "builtins": ["django_component_kit.templatetags.components", "tests.test_templatetags"],
        },
    },
]
