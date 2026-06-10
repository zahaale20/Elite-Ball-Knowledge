#!/usr/bin/env python3
"""
enrich_leads.py — Turn a list of company domains YOU supply into role-based business
contacts, using a licensed data provider's API under that provider's terms.

What this does:
  - Reads a CSV of company domains you already sourced legitimately (Step 2 of the README).
  - Calls a licensed provider (default: Hunter.io domain-search) with YOUR API key.
  - Writes verified, role-based business contacts into the leads schema.

What this deliberately does NOT do:
  - It does not scrape websites or social networks.
  - It does not guess/brute-force email addresses.
  - It only records what the licensed provider returns and verifies.

Usage:
  export HUNTER_API_KEY=your_key_here
  python3 enrich_leads.py --domains domains.csv --out ../templates/leads.csv \
      --departments hr,executive --limit-per-domain 3

domains.csv format (one column, header "domain"):
  domain
  example.com
  acme-corp.com

This is a tool you operate with your own licensed API key. Respect the provider's
rate limits and license terms, and only enrich domains you have a legitimate basis
to contact for business purposes.
"""

import argparse
import csv
import os
import sys
import time
import urllib.parse
import urllib.request
import json
from datetime import date

PROVIDER_HELP = (
    "This script ships with a Hunter.io adapter as an example because its domain-search "
    "endpoint returns role-based business contacts under a clear license. You can swap in "
    "Apollo, Clearbit, Cognism, etc. by editing fetch_contacts()."
)

LEAD_FIELDS = [
    "company", "domain", "first_name", "last_name", "title", "department",
    "email", "source", "confidence", "date_added", "status", "notes",
]


def fetch_contacts(domain, api_key, departments, limit):
    """Query Hunter.io domain-search. Returns a list of contact dicts.

    Swap this function to use a different licensed provider. The contract:
    given a domain, return verified business contacts the provider is licensed
    to share. Never synthesize or guess addresses here.
    """
    params = {"domain": domain, "api_key": api_key, "limit": str(limit)}
    if departments:
        params["department"] = ",".join(departments)
    url = "https://api.hunter.io/v2/domain-search?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            payload = json.load(resp)
    except Exception as exc:  # network/HTTP errors surface to the operator, not silently
        print(f"  ! {domain}: provider error: {exc}", file=sys.stderr)
        return []

    data = payload.get("data", {}) or {}
    org = data.get("organization") or domain
    contacts = []
    for item in data.get("emails", []) or []:
        # Only keep entries the provider actually returned an address for.
        if not item.get("value"):
            continue
        contacts.append({
            "company": org,
            "domain": domain,
            "first_name": item.get("first_name") or "",
            "last_name": item.get("last_name") or "",
            "title": item.get("position") or "",
            "department": item.get("department") or "",
            "email": item["value"],
            "source": "hunter.io domain-search",
            "confidence": str(item.get("confidence") or ""),
            "date_added": date.today().isoformat(),
            "status": "new",
            "notes": "",
        })
    return contacts


def read_domains(path):
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames or "domain" not in reader.fieldnames:
            sys.exit("Input CSV must have a 'domain' column.")
        # De-duplicate while preserving order.
        seen, domains = set(), []
        for row in reader:
            d = (row.get("domain") or "").strip().lower()
            if d and d not in seen:
                seen.add(d)
                domains.append(d)
        return domains


def load_existing_emails(out_path):
    """Avoid writing duplicates across re-runs."""
    if not os.path.exists(out_path):
        return set()
    with open(out_path, newline="", encoding="utf-8") as fh:
        return {(r.get("email") or "").lower() for r in csv.DictReader(fh)}


def main():
    parser = argparse.ArgumentParser(description="Enrich supplied domains into leads. " + PROVIDER_HELP)
    parser.add_argument("--domains", required=True, help="CSV of domains (column: domain)")
    parser.add_argument("--out", required=True, help="Output leads CSV (appends, de-duplicated)")
    parser.add_argument("--departments", default="hr,executive",
                        help="Comma-separated departments to request (e.g., hr,executive)")
    parser.add_argument("--limit-per-domain", type=int, default=3,
                        help="Max contacts per domain (keep small and role-relevant)")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Seconds between API calls (respect provider rate limits)")
    args = parser.parse_args()

    api_key = os.environ.get("HUNTER_API_KEY")
    if not api_key:
        sys.exit("Set HUNTER_API_KEY (your own licensed key) in the environment first.")

    departments = [d.strip() for d in args.departments.split(",") if d.strip()]
    domains = read_domains(args.domains)
    existing = load_existing_emails(args.out)

    new_rows, write_header = [], not os.path.exists(args.out)
    print(f"Enriching {len(domains)} domain(s) via licensed provider...")
    for i, domain in enumerate(domains, 1):
        print(f"[{i}/{len(domains)}] {domain}")
        for contact in fetch_contacts(domain, api_key, departments, args.limit_per_domain):
            if contact["email"].lower() in existing:
                continue
            existing.add(contact["email"].lower())
            new_rows.append(contact)
        time.sleep(args.sleep)

    with open(args.out, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=LEAD_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerows(new_rows)

    print(f"Done. Added {len(new_rows)} new contact(s) to {args.out}.")
    print("Review them, confirm each is an appropriate business contact, then run outreach.py "
          "(dry-run first).")


if __name__ == "__main__":
    main()
