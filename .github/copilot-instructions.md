# GitHub Copilot Instructions for Pull Request Review

## Primary Focus: Documentation Quality

This repository is primarily composed of **text and markdown files**, not code. When reviewing pull requests, prioritise documentation quality over code-specific concerns.

## Critical: UK English Spelling

**All documentation in this repository MUST use UK English spelling conventions.**

Common differences to watch for:
- Use "favour" not "favor"
- Use "colour" not "color"
- Use "organise" not "organize"
- Use "analyse" not "analyze"
- Use "behaviour" not "behavior"
- Use "licence" (noun) and "license" (verb), not "license" for both
- Use "centre" not "center"
- Use "-ise" endings not "-ize" (e.g., "optimise" not "optimize")
- Use "-ogue" not "-og" (e.g., "catalogue" not "catalog")

Flag any US spelling as a **critical issue** that must be corrected before merging.

## Documentation Review Criteria

When reviewing markdown and documentation files, assess:

1. **Spelling and Grammar**
   - Verify UK English spelling throughout
   - Check for grammatical errors and typos
   - Ensure consistent terminology

2. **Clarity and Readability**
   - Are instructions clear and easy to follow?
   - Is the structure logical and well-organised?
   - Are examples helpful and accurate?

3. **Completeness**
   - Does the documentation cover all necessary information?
   - Are there gaps or missing context?
   - Are cross-references accurate?

4. **Formatting**
   - Proper markdown syntax
   - Consistent heading hierarchy
   - Appropriate use of lists, code blocks, and emphasis

5. **Accuracy**
   - Are technical details correct?
   - Do file paths and commands work as documented?
   - Are links valid and pointing to the right resources?

## Code Review (When Applicable)

For the small amount of code in this repository (primarily Python charm code in experiments):

1. Follow Python best practices and PEP 8 style
2. Ensure Juju charm conventions are followed
3. Verify proper error handling
4. Check for security issues
5. Validate that tests are present and meaningful

## Repository-Specific Considerations

- **Experiments**: Individual experiments may be incomplete or intentionally experimental—focus review on whether the experiment is documented appropriately
- **Claude Instructions**: Changes to `CLAUDE.md` or `.claude/commands/` files should be clear and actionable for AI assistants
- **Structure**: Verify new experiments follow the `YYYY-MM-DD-charm-name` naming convention

## Tone and Style

- Use a constructive and helpful tone
- Be specific in feedback (provide line numbers or examples)
- Suggest improvements rather than just identifying problems
- Remember: documentation quality directly impacts usability
