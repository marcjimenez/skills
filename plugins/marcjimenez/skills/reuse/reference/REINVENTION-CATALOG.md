# Reinvention catalog — things people rebuild that already exist

Rungs 2-5 of the ladder catch these. Any new block >10 lines that feels generic is guilty until proven
otherwise.

| You're about to write… | It already exists as… |
|---|---|
| debounce / throttle | `lodash` (`lodash/debounce`), or a framework hook |
| date parsing / math / formatting | `dayjs`, `date-fns`, or `Intl.DateTimeFormat` |
| a retry / backoff wrapper | the HTTP client's built-in retry, or `p-retry` / `tenacity` |
| input validation / schemas | `zod`, `pydantic`, `yup`, `valibot` |
| deep clone / deep equal / groupBy / chunk | `lodash`, `structuredClone`, `Object.groupBy` |
| a state machine | the framework's own (React reducer, XState if present, LangGraph) |
| string/array/collection/path/url helpers | the language standard library |
| UUID / hashing / crypto | stdlib `crypto` / `uuid` |
| env/config parsing | the framework's config layer, `dotenv`, `pydantic-settings` |

## Search order

The four tiers to search — this repo → installed deps → framework built-ins → language stdlib — are ladder
rungs 2-5 in `CLIMB-THE-LADDER.md`. Report what you searched at each tier. If you genuinely searched all
four and found nothing, say so explicitly per new utility — silence is not acceptable.
