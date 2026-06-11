#!/usr/bin/env python3
"""check-repo.py — integrity validator for the Elite Ball Knowledge library.

Zero-dependency (Python 3 standard library only). Run it from anywhere:

    ./scripts/check-repo.py            # validate; exit non-zero on any error
    ./scripts/check-repo.py --counts   # also print the per-folder count table
    ./scripts/check-repo.py --quiet    # only print problems and the final verdict

What it checks
--------------
1. Broken internal links — every relative Markdown link `[text](path)` and image
   `![alt](path)` is resolved against the file it lives in (URL-decoding `%20`,
   stripping any `#anchor`) and must point at a file that exists. External links
   (http/https/mailto) and pure in-page anchors (`#section`) are skipped. A broken
   link to *content* (another guide, an image, a PDF) is an error; a broken link
   to *code* (a `.py`/`.cpp`/… file in the separate `drone/` stack) is only a
   warning, since that stack is intentionally not vendored into this content repo.
2. Numbering integrity — within each numbered topic folder, the `NN-` prefixes
   must be unique and contiguous from 01 (a gap or duplicate is a likely mistake
   from a hand-edit, since `new-guide.sh` always takes the next free number).
3. Guide count — counts numbered guides in the 14 curriculum topic folders and
   compares the total against the figure advertised in README.md, so the headline
   number can never silently drift out of date.
4. Curriculum invariant — every numbered guide on disk must be linked from
   01-mastery-curriculum.md, and every guide the index links to must exist. This
   keeps the master index and the file tree from silently diverging (a guide added
   but never indexed, or an index row pointing at a deleted/renamed file).

Exit code is 0 only when there are no errors; numbering gaps and count drift are
reported as warnings unless `--strict` is passed, which promotes them to errors.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Repo root is the parent of this script's directory.
ROOT = Path(__file__).resolve().parent.parent

# The 14 curriculum "topic folders" whose numbered guides make up the headline
# count. Standalone collections (machine learning), the outreach toolkit, sports,
# and scratch folders are intentionally excluded.
TOPIC_FOLDERS = [
    "foundations",
    "autonomy",
    "career",
    "companies",
    "engineering",
    "software",
    "mathematics",
    "mindset-and-society",
    "information-environment",
    "general",
    "compute-and-hardware",
    "space",
    "products",
    "tooling",
]

# Directories never walked for link checking or counts.
SKIP_DIRS = {".git", ".github", "node_modules"}

# Markdown links and images: capture the target inside (...). The negative
# lookbehind on the image form is handled by matching both `!?[...]` shapes.
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")

# A leading "NN-" two-digit number prefix on a guide filename.
NUM_PREFIX_RE = re.compile(r"^(\d{2})-")

# Link targets with these extensions are content that must exist in this repo;
# a broken one is a hard error. Anything else (code, configs) that dangles is a
# cross-repo reference to the separate drone/ stack and is reported as a warning.
CONTENT_EXTENSIONS = {
    ".md",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".pdf",
}


def iter_markdown_files() -> list[Path]:
    """Return every tracked Markdown file in the repo, skipping SKIP_DIRS."""
    files: list[Path] = []
    for path in ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return files


def link_target_is_external(target: str) -> bool:
    """True for links that should not be resolved against the filesystem."""
    target = target.strip()
    if not target:
        return True
    if target.startswith("#"):  # pure in-page anchor
        return True
    return bool(re.match(r"^(?:[a-z][a-z0-9+.-]*:)?//", target)) or target.startswith(
        ("http://", "https://", "mailto:", "tel:")
    )


def check_links(files: list[Path]) -> tuple[list[str], list[str]]:
    """Return (content_errors, code_warnings) for broken relative links.

    Links inside fenced code blocks (``` ... ```) are skipped: those are
    illustrative examples (e.g. a sample README a reader would put in *their*
    own project), not navigation within this library.
    """
    errors: list[str] = []
    warnings: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        in_fence = False
        for lineno, line in enumerate(text.splitlines(), start=1):
            stripped = line.lstrip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for raw_target in LINK_RE.findall(line):
                target = raw_target.strip()
                # Markdown allows an optional "title": [x](path "title").
                target = target.split(" ", 1)[0].strip()
                if link_target_is_external(target):
                    continue
                # Drop any anchor; decode %20 and friends.
                file_part = unquote(target.split("#", 1)[0])
                if not file_part:  # was an anchor-only link after split
                    continue
                resolved = (path.parent / file_part).resolve()
                if resolved.exists():
                    continue
                rel = path.relative_to(ROOT)
                message = f"{rel}:{lineno}  broken link -> {raw_target}"
                # Only links to content (guides, images, PDFs) are hard errors.
                # Code files and bare directory refs point at the separate
                # drone/ stack and are reported as cross-repo warnings.
                suffix = Path(file_part).suffix.lower()
                if suffix in CONTENT_EXTENSIONS:
                    errors.append(message)
                else:
                    warnings.append(message)
    return errors, warnings


def check_numbering() -> tuple[list[str], list[str], dict[str, int]]:
    """Validate NN- numbering per topic folder.

    Returns (errors, warnings, counts). A duplicate number is an error (two
    guides claiming the same slot is always a bug). A gap is only a warning,
    since a guide may have been intentionally removed.
    """
    errors: list[str] = []
    warnings: list[str] = []
    counts: dict[str, int] = {}
    for folder in TOPIC_FOLDERS:
        directory = ROOT / folder
        if not directory.is_dir():
            warnings.append(f"missing topic folder: {folder}/")
            counts[folder] = 0
            continue
        numbers: dict[int, list[str]] = {}
        for md in directory.glob("[0-9][0-9]-*.md"):
            match = NUM_PREFIX_RE.match(md.name)
            if match:
                numbers.setdefault(int(match.group(1)), []).append(md.name)
        counts[folder] = len(
            [n for files in numbers.values() for n in files]
        )
        # Duplicates share a number — always a real problem.
        for num, names in sorted(numbers.items()):
            if len(names) > 1:
                errors.append(
                    f"{folder}/: duplicate number {num:02d} -> {', '.join(sorted(names))}"
                )
        # Gaps in the 01..max sequence usually mean an accidental skip.
        if numbers:
            expected = set(range(1, max(numbers) + 1))
            missing = sorted(expected - set(numbers))
            if missing:
                gap = ", ".join(f"{n:02d}" for n in missing)
                warnings.append(f"{folder}/: numbering gap(s) at {gap}")
    return errors, warnings, counts


def advertised_count() -> int | None:
    """Read the headline guide count out of README.md, if present."""
    readme = ROOT / "README.md"
    if not readme.is_file():
        return None
    match = re.search(r"\*\*(\d+)\s+in-depth guides", readme.read_text(encoding="utf-8"))
    return int(match.group(1)) if match else None


def check_curriculum_invariant() -> list[str]:
    """Every numbered guide on disk must be indexed, and every indexed guide exist.

    Compares the set of `NN-*.md` guides in the topic folders against the set of
    guide links in 01-mastery-curriculum.md. A guide present on disk but missing
    from the index, or an index row pointing at a file that does not exist, is an
    error — both break the contract that the index is the complete map of the
    library.
    """
    errors: list[str] = []
    index = ROOT / "01-mastery-curriculum.md"
    if not index.is_file():
        return ["01-mastery-curriculum.md is missing."]

    topic_prefixes = tuple(f"{folder}/" for folder in TOPIC_FOLDERS)

    # Guide links in the index that point into a topic folder (root-relative).
    indexed: set[str] = set()
    for raw_target in LINK_RE.findall(index.read_text(encoding="utf-8")):
        target = unquote(raw_target.split(" ", 1)[0].split("#", 1)[0].strip())
        if target.startswith(topic_prefixes) and NUM_PREFIX_RE.match(Path(target).name):
            indexed.add(target)

    # Numbered guides that actually exist on disk.
    on_disk: set[str] = set()
    for folder in TOPIC_FOLDERS:
        for md in (ROOT / folder).glob("[0-9][0-9]-*.md"):
            on_disk.add(str(md.relative_to(ROOT)))

    for guide in sorted(on_disk - indexed):
        errors.append(f"{guide}: on disk but not linked from 01-mastery-curriculum.md")
    for guide in sorted(indexed - on_disk):
        errors.append(f"{guide}: linked from 01-mastery-curriculum.md but missing on disk")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate repo integrity.")
    parser.add_argument("--counts", action="store_true", help="print the count table")
    parser.add_argument("--quiet", action="store_true", help="only print problems")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat all warnings (gaps, code refs) as errors too",
    )
    args = parser.parse_args()

    files = iter_markdown_files()
    link_errors, link_warnings = check_links(files)
    num_errors, num_warnings, counts = check_numbering()
    curriculum_errors = check_curriculum_invariant()
    total = sum(counts.values())

    if args.counts or not args.quiet:
        print("Guides per topic folder:")
        for folder in TOPIC_FOLDERS:
            print(f"  {counts.get(folder, 0):>3}  {folder}/")
        print(f"  {'-' * 3}")
        print(f"  {total:>3}  TOTAL (14 topic folders)")
        print()

    # Reconcile the headline count. Drift is an error: the README number must
    # stay truthful as guides are added or removed.
    count_errors: list[str] = []
    advertised = advertised_count()
    if advertised is not None and advertised != total:
        count_errors.append(
            f"README advertises {advertised} guides but found {total}."
        )

    # Report.
    for err in link_errors:
        print(f"ERROR  {err}")
    for err in num_errors:
        print(f"ERROR  {err}")
    for err in curriculum_errors:
        print(f"ERROR  {err}")
    for err in count_errors:
        print(f"ERROR  {err}")
    for warn in link_warnings:
        print(f"WARN   (code ref) {warn}")
    for warn in num_warnings:
        print(f"WARN   {warn}")

    errors = len(link_errors) + len(num_errors) + len(curriculum_errors) + len(count_errors)
    warnings = len(link_warnings) + len(num_warnings)
    if args.strict:
        errors += warnings
        warnings = 0

    print()
    if errors:
        print(f"FAILED: {errors} error(s), {warnings} warning(s).")
        return 1
    if warnings:
        print(f"OK with {warnings} warning(s).")
        return 0
    print(f"OK: {len(files)} files scanned, {total} guides, no problems.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
