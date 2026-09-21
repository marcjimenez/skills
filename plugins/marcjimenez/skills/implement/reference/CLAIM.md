# Claiming an issue before you work it

Two agents must never build the same ticket. Parallel workspaces make this a live problem, not a
theoretical one: two of your own sessions can reach the same issue within seconds of each other.

## Why the lock is a git ref and not a label

Labels look like the obvious lock and they do not work. Measured against live GitHub:

- `PATCH /issues/{n}` with `If-Match` returns **400**, "Conditional request headers are not allowed in
  unsafe requests unless supported by the endpoint". GraphQL `UpdateIssueInput` has no version field
  either. There is no compare-and-swap on an issue.
- Eight parallel `POST /issues/{n}/labels` for the same label returned 8×200 and produced **four**
  duplicate `labeled` events at an identical second. The label set converges; the event log does not. So
  the status code cannot tell you whether you won.
- When two agents share a token, every duplicate event carries the same `actor.login`, so the timeline
  cannot arbitrate either.
- `POST /issues/{n}/assignees` returns 201 even when it silently drops an assignee lacking push access, so
  it proves even less. `gh issue edit --add-assignee` is worse still: a read-modify-write that clobbers.

`POST /git/refs` is a genuine compare-and-swap. Ten concurrent creates, five trials, returned exactly one
`201` and nine `422 Reference already exists` every time. It is decided server-side, needs no read-back,
and works when both racers share an identity. `github/branch-deploy` builds its deployment lock this way.

So: **the ref is the lock, the label is how the claim becomes visible.**

## The protocol

Read `agent_handoff` for `claim_ref_prefix`, `in_progress_label` and `claim_ttl_hours`.

### 1. Idempotency gate

One GraphQL call, cost 1 whether you ask for four fields or twelve.

```bash
gh api graphql -f query='
query($owner:String!,$name:String!,$number:Int!){
  repository(owner:$owner,name:$name){ issue(number:$number){
    state
    assignees(first:10){ totalCount nodes{ login } }
    labels(first:20){ nodes{ name } }
    closedByPullRequestsReferences(first:5){ totalCount nodes{ number state url } }
  }}}' -f owner="$OWNER" -f name="$REPO" -F number="$N"
```

Stop when the issue is not `OPEN`, when `closedByPullRequestsReferences.totalCount > 0`, or when
`in_progress_label` is already present. Leave `includeClosedPrs` at its default so an abandoned PR does not
block a retry.

This is advisory. It saves a wasted claim attempt; it does not decide anything.

### 2. Take the lock

```bash
# Parentless commit on git's well-known empty tree, so the lock carries a holder and a
# timestamp without touching history. Pattern from suzuki-shunsuke/lock-action.
COMMIT=$(gh api -X POST "/repos/$OWNER/$REPO/git/commits" \
  -f message="claim issue-$N by $AGENT_ID" \
  -f tree=4b825dc642cb6eb9a060e54bf8d69288fbee4904 --jq .sha)

gh api -X POST "/repos/$OWNER/$REPO/git/refs" \
  -f "ref=refs/claims/issue-$N" -f "sha=$COMMIT" >/dev/null 2>&1 \
  || { echo "issue #$N is already claimed; stopping."; exit 0; }
```

A 422 (or 409, which `branch-deploy` catches defensively) means someone else holds it. Exit zero and do
nothing further: losing a claim is a normal outcome, not an error.

`refs/claims/` sits outside `refs/heads/`, so the lock never appears in the branch list or any PR UI.

### 3. Publish the claim

Only the winner reaches this, so ordinary non-atomic writes are safe now. Use `gh api` rather than
`gh issue edit`, which costs three round trips for labels and read-modify-writes assignees.

```bash
gh api -X POST "/repos/$OWNER/$REPO/issues/$N/labels" -f 'labels[]=agent-in-progress'
gh api -X POST "/repos/$OWNER/$REPO/issues/$N/assignees" -f "assignees[]=$GH_LOGIN"
```

### 4. Release on every exit path

```bash
trap 'gh api -X DELETE "/repos/'"$OWNER"'/'"$REPO"'/git/refs/claims/issue-'"$N"'" >/dev/null 2>&1' EXIT INT TERM
```

Remove `in_progress_label` too once the PR is open, so the issue reads as handed off rather than held.

### 5. Stale locks

Only on the 422 path, and only when `claim_ttl_hours` is non-zero. Read the holder and age off the commit
the ref points at:

```bash
gh api "/repos/$OWNER/$REPO/git/commits/$(gh api "/repos/$OWNER/$REPO/git/ref/claims/issue-$N" --jq .object.sha)" \
  --jq '{holder: .message, claimed_at: .committer.date}'
```

Past the TTL, say who holds it and how old it is, and ask before deleting. Reclaim is racy by
construction: ref deletion is unconditional, so two agents can both judge a lock stale and the second
deleter can remove the first's fresh claim. Asking makes that rare enough not to matter.

## What this does not cover

- **A human.** Someone can start work with no label, no assignee and no branch, and nothing here sees
  them. The claim excludes agents from each other, not people.
- **The window between step 1 and step 2**, roughly a second. Another agent can pass its own gate in that
  time. Step 2 still arbitrates, so the cost is a wasted gate check, not a double start.
- **An agent that never calls this.** The protocol only binds its callers.
- **Different ref prefixes.** The ref name *is* the lock identity. Two workers using different values for
  `claim_ref_prefix` on one issue hold two unrelated locks and exclude nothing.

Ref reads are eventually consistent even though the create is not, so never let correctness depend on a
read returning empty. Only the 201 decides.
