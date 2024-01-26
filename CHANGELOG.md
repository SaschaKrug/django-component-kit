# Changelog

## [0.4.1] - 2024-01-26
fix: startup with whitenoise can cause issues

## [0.4.0] - 2024-01-26
fix: compatibility with Whitenoise compression

BREAKING-CHANGE:
Assets now require the relative path you would normally use inside a static template tag

## [0.3.1] - 2024-01-09
- Cache rendered assets

## [0.3.0] - 2024-01-08
- Add assets support
- Add 'is_partial' attribute when rendering partials
- Add support for strings with ' enclosures
- Add PartialResponse class to render partials in views
- Add support for dict as input for `render_partial_from_template`

## [0.2.1] - 2023-12-22
- Cache 'render_partial_from_template' utility function
- Update dev dependencies

## [0.2.0] - 2023-12-22

- Add `{% partial NAME %}` tag to define a partial inside a template
- Add `render_partial_from_template` utility function to render a partial
- Add `partial=XXX` argument to components to render only a partial
- Improve docs

## [0.1.1] - 2023-12-18

- Bugfixes

## [0.1.0] - 2023-12-13

- Initial release
