# Audit mode — repo-wide sweep (not tied to a diff)

For a standalone sweep of existing code rather than a change under review, run the `simplicity`
(ponytail-review) reviewer over the whole tree instead of a diff — its tags (`delete:`/`stdlib:`/`native:`/
`yagni:`/`shrink:`) and `net: -<N> lines` metric are defined in `REVIEWERS.md`. Rank findings biggest-cut
first. This is a manual request, not part of the per-feature review loop. Pair it with the `reinvention`
reviewer for a DRY sweep across the repo.
