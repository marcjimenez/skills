# Strict typing — `any` is never the answer

## Contents

The rule · TypeScript replacements · Python replacements · The banned escape hatches ·
The one boundary · Compiler settings · Sources

## The rule

**Never `any` in TypeScript. Never `Any` in Python.** Not in a signature, a generic, a cast, a field, a
`.d.ts`, or a test. This is a guardrail, so no intensity level cuts it and no deadline waives it.

The rule bans the workarounds in the same breath, because a ban on the word alone just moves the hole
somewhere harder to grep. `as unknown as Foo`, `# type: ignore`, `@ts-ignore` and an untyped `def` are
the same defect wearing a different name, and they are worse than `any` because a search for `any` no
longer finds them.

An unavoidable dynamic value is typed `unknown` in TypeScript or `object` in Python, and narrowed before
use. That is the difference that matters: `unknown` and `object` force the narrowing at the boundary,
`any` and `Any` let an unchecked value travel arbitrarily far from where it entered.

## TypeScript replacements

| Instead of | Use | Why |
|---|---|---|
| `any` on an incoming value | `unknown`, then narrow | The compiler forces a check before any access |
| `any` on a parameter you do not constrain | a generic `<T>` | Keeps the caller's type instead of erasing it |
| `any[]` | `unknown[]` or `readonly T[]` | Same, for collections |
| `any` for "some object" | `Record<string, unknown>` | Indexable without being assignable to everything |
| `as any` to silence a cast | a type guard, or `satisfies` | A guard is checked; a cast is a promise |
| `any` for a JSON payload | `zod` (or the repo's validator) | Parse at the edge, and the inferred type flows inward |
| `any` for a union you cannot express | a discriminated union | One tag field makes exhaustiveness checkable |
| `any` in a `catch` | `catch (e: unknown)` | The only legal alternative under `useUnknownInCatchVariables` |
| `any` to reach a private field | fix the visibility, or a test-only accessor | The type is telling you the design is wrong |

## Python replacements

| Instead of | Use | Why |
|---|---|---|
| `Any` on an incoming value | `object`, then narrow | `object` permits almost nothing until you check |
| `Any` on a passthrough parameter | a `TypeVar` | Preserves the caller's type end to end |
| `Any` for "has these methods" | a `Protocol` | Structural typing without inheritance |
| `dict[str, Any]` | a `TypedDict`, a dataclass, or pydantic | Names the keys, so a typo is a type error |
| `Any` for a fixed set of values | `Literal[...]` or an `Enum` | Exhaustiveness the checker can verify |
| `Any` because the return varies by argument | `@overload` | One precise signature per calling shape |
| `Any` for JSON | pydantic (or the repo's validator) | Validate at the edge, typed inward |
| `Any` on `*args` / `**kwargs` | `ParamSpec`, or name the parameters | Keeps a decorator's signature intact |
| `Any` for "never returns" | `Never` / `NoReturn` | Says the real thing |

## The banned escape hatches

Every one of these is a finding in review, the same severity as the `any` it hides:

- `as any`, `<any>x`, `as unknown as Foo`, and any double cast whose only purpose is to reach the target.
- `@ts-ignore`. Use `@ts-expect-error` with a one-line reason **and** a linked issue, never bare, and only
  where an upstream type is genuinely wrong. It fails the build once upstream fixes it, which is the point.
- `# type: ignore` without a specific error code. `# type: ignore[attr-defined]` with a reason is arguable;
  bare is not.
- A non-null `!` on anything that came from outside the process. Narrow it.
- An untyped `def`, or a signature where the return is inferred as `Any` because a helper returns `Any`.
  `Any` is contagious, so the fix belongs at the helper, not the call site.

## The one boundary

A dynamic value has to enter somewhere: a JSON body, a database row, an untyped dependency, a webhook.
That entry point is the only place where a value legitimately has no type yet.

Type it `unknown` / `object`, validate it into a real type in the same function, and let only the
validated type travel inward. The test is that the untyped value never crosses a function boundary. A
project with one validated edge per input has no use for `any` anywhere else.

For an untyped third-party package, write a `.d.ts` or a `.pyi` stub that types the surface you actually
call. Stubbing four functions is a smaller job than it sounds, and it is bounded, which `any` is not.

## Compiler settings

The rule is only real if the build enforces it. These belong in the repo, not in a reviewer's memory:

```jsonc
// tsconfig.json
{ "compilerOptions": {
  "strict": true,                        // implies noImplicitAny, strictNullChecks, and the rest
  "noUncheckedIndexedAccess": true,      // arr[i] is T | undefined, which is the truth
  "exactOptionalPropertyTypes": true,
  "useUnknownInCatchVariables": true     // on by default under strict; do not turn it off
}}
```

```toml
# pyproject.toml
[tool.mypy]
strict = true
disallow_any_explicit = true    # the flag that actually bans a written-out Any
disallow_any_generics = true
warn_return_any = true
```

`strict` alone does NOT ban an explicit `Any` in either language: TypeScript's `noImplicitAny` only
catches the ones you did not write, and mypy's `strict` omits `disallow_any_explicit`. Both lines above
are the ones doing the work.

## Sources

- [TypeScript: `unknown` vs `any`](https://www.typescriptlang.org/docs/handbook/2/functions.html#unknown)
- [TypeScript `tsconfig` reference, `strict`](https://www.typescriptlang.org/tsconfig/#strict)
- [`@ts-expect-error` vs `@ts-ignore`](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-3-9.html#-ts-expect-error-comments)
- [mypy, `disallow_any_explicit`](https://mypy.readthedocs.io/en/stable/config_file.html#confval-disallow_any_explicit)
- [PEP 484, `Any` and gradual typing](https://peps.python.org/pep-0484/#the-any-type)
- [typing docs, `Protocol`, `TypedDict`, `ParamSpec`, `Never`](https://docs.python.org/3/library/typing.html)
