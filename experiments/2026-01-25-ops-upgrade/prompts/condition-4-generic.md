# Condition 4: Generic Release-Notes Prompt

> There is a new ops (and ops-tracing, and ops-scenario) release. Carefully read the release notes and analyse how each change (feature, bug fix, deprecation, etc.) impacts this charm. Prepare a branch that upgrades to the new ops version, making use of new features wherever sensible and addressing any other items that arise from your analysis.

This prompt is used identically for every charm and every release -- no customisation needed. The agent is expected to:

1. Find and read the release notes for ops, ops-tracing, and ops-scenario
2. Analyse the charm's current code to determine which changes are relevant
3. Apply the relevant changes
4. Update dependencies as needed

This is the "zero human effort" baseline. If it performs comparably to the other conditions, it suggests that maintaining per-feature skills may not be worth the investment.
