# Audit mode — repo-wide sweep (not tied to a diff)

For a standalone sweep of existing code rather than a change under review, run the `UNIT-AUDIT.md` prompt
over a chosen directory instead of a diff, treating each exported function, class and module as a unit.
Rank findings by lines saved, biggest cut first.

Derive `CONFIG_HOME` and `REPO_KEY` as `SKILL.md` §0 does before starting; a sweep skips the rest of that
section but still needs both paths.

Two adjustments for a sweep this size:

- Seed the run from `$CONFIG_HOME/repos/$REPO_KEY/utilities.md` and fold the returned `UTILITIES` block back
  into it. A sweep is the cheapest opportunity to build that index, and it makes every later review faster.
- Skip questions 5 and 6 (comments, docstrings, doc staleness) unless asked for specifically. Over a whole tree
  it produces more findings than anyone will act on, and it drowns the reuse findings that motivated the
  sweep.

This is a manual request, not part of the per-feature review loop.
