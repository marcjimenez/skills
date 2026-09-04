<!-- Open this PR as a DRAFT before writing code. Fill Why + How + Queue first. -->

## Why

<!-- What breaks or stays broken if this doesn't merge? One paragraph. Link the ticket. -->

Closes KUD-

## How

<!-- The approach in 3-6 sentences. Then: what you rejected, and why. -->

**Rejected:**

## Task queue

<!-- [ ] queued  [~] in progress  [x] done  [!] blocked  [-] dropped
     An item is [x] only when the code is on the branch AND the Evidence line is written. -->

<details>
<summary><strong>[ ] 1. Task name</strong> — @owner</summary>

- **Exit criteria:**
- **Evidence:**
- **Files:**

</details>

<details>
<summary><strong>[ ] 2. Task name</strong> — @owner</summary>

- **Exit criteria:**
- **Evidence:**
- **Files:**

</details>

## Verification

- [ ] Unit tests pass locally
- [ ] Integration tests pass against a seeded database
- [ ] Exercised in staging <!-- how, and what you saw -->
- **Not covered by this PR:**

## Conditional sections

<!-- Declare each one required or N/A WITH A REASON, up front. Delete the blocks you marked N/A. -->

- Security: required / N/A because
- Performance: required / N/A because
- Data & migrations: required / N/A because
- Observability: required / N/A because

<details>
<summary><strong>[ ] Security</strong></summary>

<!-- Triggered by: auth/authz, a public resolver, secrets, PII or card data, a new dependency. -->

- **Authn/authz paths touched:**
- **PII or card data in scope:**
- **New inputs and how they're validated:**
- **Secrets / credentials:**
- **New dependencies (and why this one):**
- [ ] No secret, token or key added to the diff
- [ ] Every new endpoint or resolver has an explicit authorization check

</details>

<details>
<summary><strong>[ ] Performance</strong></summary>

<!-- Triggered by: new/changed SQL, a hot resolver, a loop over a network call, request-path lambda. -->

- **Before / after (with how you measured):**
- **Query plans for new or changed SQL:**
- **N+1 risk (resolvers, loops over calls):**
- **Payload / bundle size delta:**

</details>

<details>
<summary><strong>[ ] Data & migrations</strong></summary>

<!-- Triggered by: any change under db/migrations. -->

- **Forward plan:**
- **Backward plan (tested, not theorized):**
- **Rows affected / expected duration:**
- **Lock behavior:**
- [ ] Migration is safe to run before the deploy
- [ ] Backfill is idempotent and resumable

</details>

<details>
<summary><strong>[ ] Observability</strong></summary>

<!-- Triggered by: any new code path that can fail silently. -->

- **Metric / log / trace that proves this works in prod:**
- **Alert that fires when it stops:**
- **Dashboard:**

</details>

## Risk & rollback

<!-- Score it: blast radius (0-6) + data (0-5) + reversibility (0-5) + sensitivity (0-5) + verification (0-3)

     Blast radius     0 internal/docs · 2 one service · 4 shared service or public API · 6 money movement or rewards ledger
     Data footprint   0 no schema change · 1 additive · 3 backfill or rewrite · 5 destructive migration
     Reversibility    0 clean revert · 2 revert plus config · 5 irreversible once data is written
     Sensitivity      0 no PII/auth · 3 touches PII · 5 touches auth, secrets or card data
     Verification     0 unit + integration + staging · 2 unit only · 3 manual only or none

     Bands: 0-4 low · 5-10 guarded · 11-16 elevated · 17-24 high -->

RISK: n/24 (band) — radius n, data n, revert n, sensitivity n, verification n

- **Feature flag:**
- **Rollback procedure:**
- **Who to page:**
