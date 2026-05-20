# Locator Registry

This folder stores stable locator knowledge as environment-aware registry files plus human-readable notes.

## Purpose

Use the registry for approved locators that have already been validated in a real Teamcenter environment.

Use the notes file for:

- why a locator is stable
- what changed between environments
- known fallbacks
- validation history
- MCP snapshot references

## Profile Layout

Each environment profile gets its own folder:

```text
src/knowledge/locator-registry/
  default/
    teamcenter_generic/
      locator-registry.json
      locator-notes.md
```

## Profile Selection

The runtime reads:

```env
TEAMCENTER_LOCATOR_PROFILE=default/teamcenter_generic
```

If the profile is not provided, the framework uses `default/teamcenter_generic`.

## Registry Schema

Each locator entry should contain:

- `strategy`
- `value`
- `status`
- `confidence`
- `source`
- `lastValidated`
- `notes`

Optional:

- `flags`
- `options`
- `fallbacks`

## Strategy Examples

- `label`
- `label_regex`
- `role`
- `role_regex`
- `text`
- `text_regex`
- `searchbox`
- `test_id`
- `css`
- `placeholder`
