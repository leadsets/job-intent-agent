# Leadsets job intent agent

A small Python watcher that calls [Leadsets](https://www.leadsets.ai/) `scrape_jobs` on a list of company domains, stores the titles it has already seen, and prints only new open roles.

Hiring is a useful intent signal. A posting is not a purchase order. After you see a buyer-relevant role, find a person with `search_people` or `enrich_person` and verify the email before you send.

Leadsets is Unlimited B2B Contact Data for AI Agents, Starting from $29/mo (paid plans; fair-use rate limits apply).

## Requirements

- Python 3.10+
- A Leadsets API key on a **paid plan with scrape units**. Scraping is an add-on: one unit is one standard page. Packs are listed on [pricing](https://www.leadsets.ai/pricing).
- The free plan does not include scraping. Sign-up is waitlist-only until the public launch on 10 December 2026. [Join the waitlist](https://www.leadsets.ai/signup). At launch, you can try search and enrichment on the free plan (1,000 enrichments and 100 search records, no card), then add scrape units when you are ready to watch careers pages.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# put your key in the environment, not in git
export LEADSETS_KEY=ls_live_…
cp domains.example.txt domains.txt
# add real company website domains, one per line
python watch_jobs.py domains.txt
```

The first run stores titles in `jobs_state.json` (already gitignored patterns cover `.env`; add `jobs_state.json` and `domains.txt` to your own ignore list if they contain customer data). Later runs print only roles whose titles were not in the previous snapshot.

If the key cannot scrape, the official SDK raises `PermissionDeniedError` with an upgrade URL. If units are exhausted, it raises `ScrapeUnitsExhaustedError`. The script exits instead of retrying those errors in a loop.

## What not to infer

- A missing careers page or zero roles does not prove the company is not hiring. It may only mean the page could not be read.
- Do not invent a budget or a timeline the posting does not state.
- Do not use scraped text as a substitute for verified contact data.

The longer guide is [How to scrape job posts for hiring intent signals](https://telegra.ph/How-to-scrape-job-posts-for-hiring-intent-signals-11-20).

## Related

- [GTM recipes](https://github.com/leadsets/gtm-recipes) (ICP lists and email verification)
- [n8n workflows](https://github.com/leadsets/n8n-workflows)
- [Official Python SDK](https://github.com/leadsets/sdk-python)
- [Company enrichment fields](https://telegra.ph/Company-enrichment-fields-explained-source-freshness-and-what-to-use-11-20)

## License

MIT. See [LICENSE](LICENSE).
