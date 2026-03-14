# Policy Watch

## Scope

`policy_watch` is the first functional-skill extension in the repository.

- `browser_research_skill`: declares a controlled browser/fetch capability for official government pages.
- `government_policy_crawl_skill`: crawls official policy/news pages for the top 10 economies and writes local snapshots.

This runbook covers the scheduled policy side.

- scheduled government policy/news intake should use `policy_watch`
- ad hoc user questions should use `web_research` first, then summarize the search result back to Discord

Current implementation status:

- registry metadata is in place
- a local Python crawler is implemented
- results are written into `data/policy_watch/<date>/<run_id>/`
- ad hoc web research now uses Bing RSS search results plus follow-up page fetches through `WEB_PROXY_URL`
- `agent-browser` is not yet embedded as a live plugin runtime; the current adapter uses controlled HTTP fetch and keeps an `agent_browser` adapter slot in the manifest for future replacement

## Sources

Source definitions live in:

- [top10_government_sites.yaml](/home/tgm/project/tradechain/configs/policy_sources/top10_government_sites.yaml)

Each source declares:

- country and economy rank
- official policy/news URL
- allowed domains
- policy keywords used to filter candidate links

## How To Run

Direct Python script:

```bash
python scripts/run_policy_crawl.py
```

API workflow:

```bash
curl --noproxy '*' \
  -X POST http://127.0.0.1:8000/v1/workflows/policy-crawl/run \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: external-dev-key' \
  -d '{"limit_per_source": 5}'
```

Ad hoc web research workflow:

```bash
curl --noproxy '*' \
  -X POST http://127.0.0.1:8000/v1/workflows/web-research/run \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: external-dev-key' \
  -d '{"query": "日本央行最新政策", "max_results": 5}'
```

Example response fields:

- `run_id`
- `source_count`
- `document_count`
- `output_dir`
- `sources`

## Output Layout

Each run writes:

- `summary.json`
- `summary.md`
- one folder per source with `result.json` and `result.md`

This is designed for later hand-off to:

- n8n scheduled jobs
- archive ingestion
- manual analyst review

## Routing Rule

- user questions in Discord should go to `web_research` first
- scheduled official policy collection should go to `policy_watch`
- `intel_update` remains the event-to-proposal chain and is no longer the default first hop for ad hoc user research questions

## Current Limits

- It only fetches HTML pages and extracts candidate policy links from anchors.
- It does not yet open JavaScript-heavy pages in a real browser.
- It does not yet auto-read PDF bodies.
- It does not yet write policy items into database tables.
- It is a controlled crawler, not an autonomous self-improving tool builder like OpenClaw.
