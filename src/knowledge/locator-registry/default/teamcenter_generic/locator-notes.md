# Locator Notes

## Profile

- Profile ID: `default/teamcenter_generic`
- Teamcenter Version: `generic`
- Deployment Name: `default`

## Purpose

This is the bootstrap locator profile for the framework. It stores the current best-known generic Teamcenter locators before environment-specific validation.

## How To Use This Profile

1. Capture a real MCP snapshot from the target Teamcenter environment.
2. Compare the approved UI elements against this bootstrap registry.
3. Replace generic candidate locators with deployment-specific approved locators.
4. Update the `status`, `confidence`, and `lastValidated` fields in `locator-registry.json`.

## Promotion Rules

- Use `candidate` for unverified bootstrap locators.
- Use `approved` only after live validation in the actual Teamcenter environment.
- Use `deprecated` when a locator used to work but should no longer be preferred.

## Notes By Page

### Login Page

- Login labels often differ across Teamcenter deployments.
- SSO-enabled flows may not expose the same direct username and password locators.

### Home Page

- The Part Creation entry point is commonly customized by customers.
- Navigation text should be validated from the MCP snapshot before approval.

### Part Creation Page

- Save button and success toast are high-value locators to validate early.
- Optional fields such as revision or unit of measure may not exist in every deployment.

### Search Page

- Some deployments use a global toolbar search.
- Others use dedicated results pages or side-panel search components.
