# Teamcenter Locator Knowledge

This file is the high-level human note layer.

Use it for:

- cross-environment guidance
- locator rationale
- migration notes
- reminders about MCP validation

The structured source of truth for approved locators lives under:

- `src/knowledge/locator-registry/`

Use `TEAMCENTER_LOCATOR_PROFILE` to select the active locator profile at runtime.

## Login Page
Username field:
TODO: confirm actual locator
Suggested:
page.get_by_label('User ID')

Password field:
TODO: confirm actual locator
Suggested:
page.get_by_label('Password')

Login button:
TODO: confirm actual locator
Suggested:
page.get_by_role('button', name='Sign In')

## Home Page
Part Creation navigation:
TODO: confirm actual locator
Suggested:
page.get_by_text('Part Creation')

## Part Creation Page
Create New Part:
TODO: confirm actual locator
Suggested:
page.get_by_role('button', name='New Part')

Part ID:
TODO: confirm actual locator
Suggested:
page.get_by_label('Part ID')

Part Name:
TODO: confirm actual locator
Suggested:
page.get_by_label('Part Name')

Part Type:
TODO: confirm actual locator
Suggested:
page.get_by_label('Part Type')

Save button:
TODO: confirm actual locator
Suggested:
page.get_by_role('button', name='Save')

Success message:
TODO: confirm actual locator
Suggested:
page.get_by_text('Part created successfully')
