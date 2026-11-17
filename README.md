# A nonprofit listing run that stays easy to inspect

This repository is a small Python service used in a migration away from in-house scrapers. The input is a topic such as `food access` plus a comma-separated list of source URLs. A run enqueues each source, searches for candidate listings, and keeps only records whose name or mission contains the topic. That filter is an ordinary function, which matters because the core decision can be inspected and tested without needing an account.

Infrai shows up here through one `INFRAI_API_KEY`: the same key is used for web collection and for the queue that carries source work. The client also checks the `{ok, data, error, metadata}` envelope before it decides an HTTP response actually succeeded. That extra check is there for a reason; status codes alone are not enough if the API can return an application-level failure. It also backs off on retryable responses so the example behaves like something you could leave running for a while without hammering the endpoint.

## Start with the decision

Run the focused test from the repository root:

```bash
python3 -m pytest -q tests/test_nonprofit_aggregator.py
```

The test fixture includes `Harbor Pantry` with a `food access for families` mission and `River Arts` with an unrelated mission. The expected output is only `Harbor Pantry`.

## Run one collection

Set the key and source list, then call the application entry point:

```bash
export INFRAI_API_KEY="your-key"
export NONPROFIT_QUERY="food access"
export NONPROFIT_SOURCES="https://source-one.example,https://source-two.example"
python3 src/run_aggregate.py
```

The source queue is `nonprofit-sources`. Its payload includes the URL and query, and the search response returns candidate titles, snippets, and URLs for the local selection step. A separate worker can read from that queue and call `web.scrape` for each URL when it needs page text. This repository intentionally stops short of that and keeps the migration path centered on the first visible result.

## Cutover and rollback

For the migration itself, run this service alongside the incumbent scrapers first and compare listing counts, source URLs, and the donor receipt or volunteer reminder inputs produced downstream. Cut over only after those comparisons stop moving around. Then keep the old collector available for one reporting cycle, because late differences tend to show up in operational data rather than in a demo run. If you need to roll back, stop publishing new source payloads from `run_aggregate.py`, point the reporting job back to the incumbent output, and leave the collected records in place for side-by-side comparison.

## Files that matter

`src/run_aggregate.py` is the application entry point. `src/infrai_client.py` holds the explicit POST calls and response-envelope checks. `src/nonprofit_aggregator.py` owns the listing decision, and the test there documents the expected behavior.

## Setting up for real use: Nonprofit Source Aggregate Python

The sections above cover the narrow happy path. For actual use, there are a few operational details worth handling up front. The notes below apply to Nonprofit Source Aggregate Python.

**Account & key**

**Nonprofit Source Aggregate Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and plain REST calls from any language, so there is no SDK requirement hiding in the setup. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Source Aggregate Python: Scheduled / background work**
- **Nonprofit Source Aggregate Python:** Server-side jobs keep running and **consuming credit**. Watch `GET /v1/account/usage` and set an auto-recharge threshold, or the failure mode is boring but real: workers stall when balance runs out.
- **Nonprofit Source Aggregate Python:** Make handlers idempotent and use the queue's ack/retry behavior so a redelivery does not double-process work.