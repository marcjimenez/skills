# gh / GitHub API mechanics for review comments

All commands verified against gh 2.89 on live public PRs, except the two write endpoints (reply, resolve),
which are verified from official docs and GraphQL schema introspection but were NOT executed against a live
PR. Test those against a throwaway PR you own before trusting them in anger.

## Three comment surfaces (do not confuse them)

- **Issue comments**: the top-level "Conversation" chatter, not attached to a line.
  `GET /repos/{owner}/{repo}/issues/{n}/comments`. This is also what `gh pr view --json comments` returns.
- **Review comments**: inline, anchored to a file and line. `GET /repos/{owner}/{repo}/pulls/{n}/comments`.
  This is the primary surface.
- **Reviews**: the review envelope (Approved / Changes requested / Commented plus an optional summary).
  `GET /repos/{owner}/{repo}/pulls/{n}/reviews`. Each inline comment carries `pull_request_review_id`.

Footgun confirmed live: `gh pr view --json comments` gives issue comments only, and its `reviews` field
gives review-level author/state/body but NOT the inline thread comments and NOT resolution state. For
inline threads you must use REST `/pulls/{n}/comments` or the GraphQL `reviewThreads` query below.

## Fetch review threads with resolution state (the query to use)

GraphQL is the only source of both resolution state and the thread node id. Use it as the primary fetch:

```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$pr:Int!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$pr){
      reviewThreads(first:100){
        totalCount
        pageInfo{ hasNextPage endCursor }
        nodes{
          id                        # PRRT_... thread node id  (needed to RESOLVE)
          isResolved
          isOutdated
          resolvedBy{ login }
          path
          line
          comments(first:50){       # a first:/last: arg is REQUIRED or the query errors
            nodes{
              databaseId            # == the REST comment id  (needed to REPLY)
              author{ login }
              replyTo{ databaseId } # parent comment id; null on the thread root
              body
            }
          }
        }
      }
    }
  }
}' -F owner=OWNER -F repo=REPO -F pr=PR_NUMBER
```

Key fields: `id` is the thread node id (`PRRT_...`) used by `resolveReviewThread`; `comments.databaseId`
is the numeric comment id used to reply and equals the REST `id`. `isResolved` and `isOutdated` exist ONLY
here, not in REST. `replyTo.databaseId` links a reply to its thread root.

Pagination: for more than 100 threads, follow `pageInfo.hasNextPage`/`endCursor` with an `after:` cursor.
A skill that reads only the first page silently misses comments on large PRs.

## Fetch the flat inline list (REST, when you want the raw fields)

```bash
gh api repos/OWNER/REPO/pulls/PR_NUMBER/comments --paginate
```

REST default page size 30, max 100, so pass `--paginate`. Useful fields: `id` (reply target),
`in_reply_to_id` (null on root, else the root's id; group by this to reconstruct threads),
`path`, `line`/`original_line`, `side` (RIGHT=added/context, LEFT=deleted), `commit_id`, `body`,
`user.login`, `user.type`, `author_association`, `pull_request_review_id`, `subject_type` (line vs file),
`diff_hunk`, `html_url`. REST has NO resolution field, which is why the GraphQL query above is primary.

## Bot detection

`user.type == "Bot"` is the clean signal. Login quirk: Copilot's inline comments have
`user.login == "Copilot"`, but at the review level it is `copilot-pull-request-reviewer[bot]`. CodeRabbit
is `coderabbitai[bot]`. Do not key off login alone; use `user.type`.

## Reply to a comment (REST; body required)

```bash
gh api --method POST \
  repos/OWNER/REPO/pulls/PR_NUMBER/comments/COMMENT_ID/replies \
  -f body="Looked into this. <evidence>. Resolving."
```

`COMMENT_ID` is the numeric REST id (GraphQL `databaseId`). Reply to the thread ROOT so it lands in the
right thread. GraphQL equivalent: `addPullRequestReviewThreadReply(input:{ pullRequestReviewThreadId, body })`.
Verified from docs and schema, not executed live.

## Resolve a thread (GraphQL only; reversible)

```bash
gh api graphql -f query='
mutation($id:ID!){
  resolveReviewThread(input:{threadId:$id}){ thread{ isResolved } }
}' -F id=PRRT_THREAD_NODE_ID
```

`threadId` is the `PRRT_...` thread node id from the `reviewThreads` query, NOT the comment id. This id
mismatch (thread node id to resolve, numeric comment id to reply) is the main footgun. To undo, the
symmetric `unresolveReviewThread(input:{threadId})` exists (same input shape). Verified from schema, not
executed live.

## The standard loop

1. Fetch threads (GraphQL query above); drop `isResolved`; verify `isOutdated` against the current diff.
2. Map each `comments.databaseId` to its `thread.id` so you can reply and resolve later.
3. Classify (see `VALIDITY-RUBRIC.md`), act per the two-bucket gate (see SKILL.md).
4. After a fix lands: reply to the root comment id with the commit sha, then resolve the thread node id.
5. After posting a rebuttal: resolve the thread node id.

## Sources

GitHub REST reference for pulls/comments (docs.github.com/en/rest/pulls/comments); GraphQL schema
(`resolveReviewThread`, `unresolveReviewThread`, `addPullRequestReviewThreadReply`, `reviewThreads`).
Live verification against cli/cli#14180 (Copilot + human review) and cli/cli#14104 (a real reply chain).
