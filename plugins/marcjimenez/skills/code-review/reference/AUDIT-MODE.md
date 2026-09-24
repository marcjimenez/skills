# Audit mode — repo-wide sweep (not tied to a diff)

For a standalone sweep of existing code rather than a change under review, run the `UNIT-AUDIT.md` prompt
over a chosen directory instead of a diff, treating each exported function, class and module as a unit.
Rank findings by lines saved, biggest cut first.

Two adjustments for a sweep this size:

- Seed the run from `$CONFIG_HOME/repos/$REPO_KEY/utilities.md` and write every helper you read back into
  it. A sweep is the cheapest opportunity to build that index, and it makes every later review faster.
- Skip question 5 (comments and docstrings) unless the sweep was asked for specifically. Over a whole tree
  it produces more findings than anyone will act on, and it drowns the reuse findings that motivated the
  sweep.

This is a manual request, not part of the per-feature review loop.
