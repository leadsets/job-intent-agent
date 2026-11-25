"""Watch careers pages for new open roles (a hiring intent signal).

Needs a paid Leadsets plan with scrape units. One unit is one standard page.
Run: export LEADSETS_KEY=ls_live_…   then  python watch_jobs.py domains.txt

A posting is a signal, not a purchase order. Pair new roles with search_people
and verify_email before you reach out.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from leadsets import Leadsets, PermissionDeniedError, ScrapeUnitsExhaustedError

STATE_PATH = Path("jobs_state.json")


def load_domains(path: str) -> list[str]:
    out: list[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                out.append(line.lower())
    return out


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {"domains": {}}


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True))


def title_key(domain: str, title: str) -> str:
    return f"{domain}::{title.strip().lower()}"


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python watch_jobs.py domains.txt", file=sys.stderr)
        return 2
    if not (os.environ.get("LEADSETS_KEY") or os.environ.get("LEADSETS_API_KEY")):
        print("Set LEADSETS_KEY first. Join the waitlist: https://www.leadsets.ai/signup (public launch 10 December 2026)", file=sys.stderr)
        return 2

    domains = load_domains(sys.argv[1])
    ls = Leadsets()
    usage = ls.usage.get()
    print("plan:", usage.plan, "scraping enabled:", usage.scraping, "scrape units:", usage.scrape_units)

    state = load_state()
    seen = set()
    for domain, payload in state.get("domains", {}).items():
        for title in payload.get("titles", []):
            seen.add(title_key(domain, title))

    new_roles = []
    for domain in domains:
        try:
            res = ls.scrape.jobs(domain=domain, max_pages=3)
        except PermissionDeniedError as e:
            print("Scraping needs a paid plan with units:", e.upgrade_url)
            return 3
        except ScrapeUnitsExhaustedError:
            print("No scrape units left. Add a pack in Billing: https://www.leadsets.ai/pricing")
            return 4

        titles = [job.title for job in res.jobs if job.title]
        state.setdefault("domains", {}).setdefault(domain, {})
        state["domains"][domain]["careers_url"] = res.careers_url
        state["domains"][domain]["titles"] = titles
        print(f"{domain}: {res.count} open roles at {res.careers_url}")
        for job in res.jobs:
            if not job.title:
                continue
            key = title_key(domain, job.title)
            if key not in seen:
                new_roles.append(
                    {
                        "domain": domain,
                        "title": job.title,
                        "team": job.team,
                        "location": job.location,
                        "careers_url": res.careers_url,
                    }
                )
        units_left = res.usage.scrape_units_left
        if units_left is not None:
            print("  scrape units left:", units_left)

    save_state(state)
    print(f"\n{len(new_roles)} new role(s) since last run")
    for role in new_roles:
        print(f"- {role['title']} @ {role['domain']} ({role['team'] or 'no team'}, {role['location'] or 'no location'})")
        print(f"  {role['careers_url']}")
    print(
        "\nNext: for buyer-relevant roles, run search_people and verify_email. "
        "Guide: https://telegra.ph/How-to-scrape-job-posts-for-hiring-intent-signals-11-20"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
