#!/usr/bin/env python3
"""
outreach.py — Personalize and send B2B outreach you have reviewed, the compliant way.

Design principles baked in (these are guardrails, not options):
  - DRY-RUN BY DEFAULT. It prints what it would send; you must pass --send to actually send.
  - SUPPRESSION-AWARE. Anyone in suppression.csv (opt-outs, do-not-contact) is always skipped.
  - STATE-AWARE. Skips leads whose status is already contacted/replied/bounced/opt-out.
  - RATE-LIMITED. Slow ramp protects your sending-domain reputation (and respects recipients).
  - CAN-SPAM FOOTER. Every message gets your physical mailing address + a working opt-out line.
  - YOUR ACCOUNT ONLY. Sends via your own SMTP credentials from environment variables.

This tool does not source, scrape, or guess addresses. It only contacts leads you have already
collected legitimately (see README) and reviewed. If you sell regulated financial products, get
principal/compliance approval of your templates BEFORE using --send (FINRA Rule 2210).

Usage:
  # 1) Always dry-run first and read the output:
  python3 outreach.py --leads ../templates/leads.csv --template intro \
      --suppression ../templates/suppression.csv

  # 2) When the drafts look right and templates are approved, actually send:
  export SMTP_HOST=smtp.example.com SMTP_PORT=587 SMTP_USER=you@example.com SMTP_PASS=...
  python3 outreach.py --leads ../templates/leads.csv --template intro \
      --suppression ../templates/suppression.csv --send --rate 30 --daily-cap 50

Config (sender identity + required CAN-SPAM footer) is read from sender_config.json next to this
script; copy sender_config.example.json and fill it in.
"""

import argparse
import csv
import json
import os
import smtplib
import ssl
import sys
import time
from datetime import date
from email.message import EmailMessage
from email.utils import formataddr

SENDABLE_STATUSES = {"", "new"}            # only contact fresh leads
SKIP_STATUSES = {"contacted", "replied", "bounced", "opt-out", "do-not-contact"}


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "sender_config.json")
    if not os.path.exists(path):
        sys.exit("Missing sender_config.json. Copy sender_config.example.json and fill it in. "
                 "Your real physical mailing address is required by CAN-SPAM.")
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    required = ["from_name", "from_email", "physical_address", "unsubscribe_line"]
    missing = [k for k in required if not cfg.get(k)]
    if missing:
        sys.exit(f"sender_config.json missing required fields: {', '.join(missing)}")
    return cfg


def load_suppression(path):
    if not path or not os.path.exists(path):
        return set()
    with open(path, newline="", encoding="utf-8") as fh:
        return {(r.get("email") or "").strip().lower() for r in csv.DictReader(fh) if r.get("email")}


def load_templates(path):
    """Templates file is simple: '## <name>' headers, then 'Subject: ...' then body."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    blocks, current = {}, None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip().lower()
            blocks[current] = {"subject": "", "body": []}
        elif current and line.lower().startswith("subject:"):
            blocks[current]["subject"] = line.split(":", 1)[1].strip()
        elif current is not None:
            blocks[current]["body"].append(line)
    return {k: {"subject": v["subject"], "body": "\n".join(v["body"]).strip()} for k, v in blocks.items()}


def render(text, lead):
    """Fill {first_name}, {company}, {title}, etc. Leaves unknown placeholders visible
    so you catch personalization gaps in the dry-run instead of mailing '{first_name}'."""
    out = text
    for key, val in lead.items():
        out = out.replace("{" + key + "}", val or "")
    return out


def build_message(lead, template, cfg):
    subject = render(template["subject"], lead)
    body = render(template["body"], lead)
    footer = (
        f"\n\n—\n{cfg['from_name']}\n{cfg.get('company','')}\n"
        f"{cfg['physical_address']}\n{cfg['unsubscribe_line']}"
    )
    msg = EmailMessage()
    msg["From"] = formataddr((cfg["from_name"], cfg["from_email"]))
    msg["To"] = lead["email"]
    if cfg.get("reply_to"):
        msg["Reply-To"] = cfg["reply_to"]
    msg["Subject"] = subject
    msg.set_content(body + footer)
    return msg


def main():
    parser = argparse.ArgumentParser(description="Compliant, dry-run-by-default outreach sender.")
    parser.add_argument("--leads", required=True, help="Leads CSV")
    parser.add_argument("--template", required=True, help="Template name (e.g., intro)")
    parser.add_argument("--templates-file", default="../templates/email_templates.md")
    parser.add_argument("--suppression", default="../templates/suppression.csv")
    parser.add_argument("--send", action="store_true",
                        help="Actually send. Omit to dry-run (default).")
    parser.add_argument("--rate", type=int, default=30, help="Max emails per hour")
    parser.add_argument("--daily-cap", type=int, default=50, help="Max emails this run")
    args = parser.parse_args()

    cfg = load_config()
    suppression = load_suppression(args.suppression)
    templates = load_templates(args.templates_file)
    if args.template.lower() not in templates:
        sys.exit(f"Template '{args.template}' not found. Available: {', '.join(templates)}")
    template = templates[args.template.lower()]

    with open(args.leads, newline="", encoding="utf-8") as fh:
        leads = list(csv.DictReader(fh))

    interval = max(0.0, 3600.0 / args.rate) if args.rate > 0 else 0.0
    mode = "SEND" if args.send else "DRY-RUN"
    print(f"=== {mode} === template='{args.template}' rate={args.rate}/hr cap={args.daily_cap}")
    if not args.send:
        print("(No mail will be sent. Review every draft below, then re-run with --send.)\n")

    server = None
    if args.send:
        host, port = os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT", "587"))
        user, password = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASS")
        if not all([host, user, password]):
            sys.exit("To --send, set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS in the environment.")
        server = smtplib.SMTP(host, port, timeout=30)
        server.starttls(context=ssl.create_default_context())
        server.login(user, password)

    sent = 0
    try:
        for lead in leads:
            email = (lead.get("email") or "").strip()
            status = (lead.get("status") or "").strip().lower()
            if not email:
                continue
            if email.lower() in suppression:
                print(f"  skip (suppressed): {email}")
                continue
            if status in SKIP_STATUSES or status not in SENDABLE_STATUSES:
                print(f"  skip (status={status or 'none'}): {email}")
                continue
            if sent >= args.daily_cap:
                print(f"  daily cap ({args.daily_cap}) reached; stopping.")
                break

            msg = build_message(lead, template, cfg)
            if args.send:
                server.send_message(msg)
                lead["status"] = "contacted"
                lead["notes"] = (lead.get("notes", "") + f" | sent {date.today().isoformat()}").strip(" |")
                print(f"  SENT -> {email}")
                sent += 1
                if interval:
                    time.sleep(interval)
            else:
                print("-" * 64)
                print(f"TO: {email}")
                print(f"SUBJECT: {msg['Subject']}")
                print(msg.get_content())
                sent += 1
    finally:
        if server:
            server.quit()

    # Persist status changes back to the leads file when actually sending.
    if args.send:
        fieldnames = list(leads[0].keys()) if leads else []
        with open(args.leads, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)

    verb = "sent" if args.send else "previewed"
    print(f"\nDone. {verb} {sent} message(s).")
    if not args.send:
        print("If these look right AND your templates are compliance-approved, re-run with --send.")


if __name__ == "__main__":
    main()
