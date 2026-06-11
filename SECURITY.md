# Security Policy

This repository is an educational study library — Markdown guides, a few helper
scripts, and no deployed service. The realistic "security" surface is therefore
narrow, but reports are still welcome.

## What counts as a report here

- A helper script (`scripts/`) that behaves unsafely (e.g. unsafe shell handling).
- A committed secret, credential, or private personal detail that slipped in.
- A link that points somewhere malicious.
- Content that leaks export-controlled or operationally sensitive specifics, which
  the library is explicitly written to avoid (see `information-environment/`).

## How to report

Please do **not** open a public issue for anything sensitive. Instead, use GitHub's
private vulnerability reporting on this repository
(**Security → Report a vulnerability**), or open a private channel with the
repository owner. Include the affected file(s), what the problem is, and a
suggested fix if you have one.

The owner reviews reports and will respond. Thanks for helping keep the library
clean and trustworthy.
