#!/usr/bin/env python3
"""Keep schema.json in sync with VS Code's themable color list.

VS Code documents every themable color ("theme color reference"). The cleanest
machine-readable copy of that list is the markdown source in the vscode-docs
repo, where each color is a bullet like:

    - `activityBar.background`: Activity Bar background color.

This script fetches that list, diffs it against the `colors.properties` block in
schema.json, and reports:

  * missing  - documented by VS Code but absent from the schema (add these)
  * stale    - in the schema but not in the docs (deprecated/proposed; review)
  * theme-only / unknown - keys the theme file uses that neither source knows

By default it only reports. Pass --write to add the missing entries to the
schema (alphabetically, format "color", with the documented description).

Usage:
    python scripts/update_schema.py                 # report
    python scripts/update_schema.py --write          # apply missing entries
    python scripts/update_schema.py --source-file theme-color.md   # offline
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

# Official reference, markdown source (stable, easy to parse).
DOCS_URL = "https://raw.githubusercontent.com/microsoft/vscode-docs/main/api/references/theme-color.md"

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO_ROOT / "src" / "extension" / "schema.json"
THEME_PATH = REPO_ROOT / "src" / "extension" / "themes" / "Moonlight-color-theme.json"

# A documented color id: alnum segments, optionally dotted. Dotless base colors
# like `focusBorder`, `foreground`, `contrastBorder` are valid and must match too.
ENTRY_RE = re.compile(r"^\s*[-*]\s*`([A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z0-9]+)*)`\s*:\s*(.+?)\s*$")


def fetch_docs(source_file: str | None) -> str:
    if source_file:
        return Path(source_file).read_text(encoding="utf-8")
    req = urllib.request.Request(DOCS_URL, headers={"User-Agent": "schema-sync"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_color_entries(markdown: str) -> dict[str, str]:
    """Return {colorId: description} for every documented theme color."""
    entries: dict[str, str] = {}
    for line in markdown.splitlines():
        m = ENTRY_RE.match(line)
        if not m:
            continue
        color_id, desc = m.group(1), m.group(2)
        # strip trailing markdown link syntax / stray backticks from the description
        desc = re.sub(r"\s+", " ", desc).strip().strip("`")
        entries.setdefault(color_id, desc)
    return entries


def load_json(path: Path):
    raw = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in raw else "\n"
    return json.loads(raw), newline


def schema_color_props(schema: dict) -> dict:
    return schema.get("properties", {}).get("colors", {}).get("properties", {})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--write", action="store_true", help="add missing entries to schema.json")
    ap.add_argument("--source-file", help="parse a local theme-color.md instead of fetching")
    ap.add_argument("--schema", default=str(SCHEMA_PATH), help="path to schema.json")
    ap.add_argument("--theme", default=str(THEME_PATH), help="path to the theme json (for usage check)")
    args = ap.parse_args()

    schema_path = Path(args.schema)

    try:
        documented = parse_color_entries(fetch_docs(args.source_file))
    except Exception as exc:  # network down, bad path, etc.
        print(f"ERROR: could not load color reference: {exc}", file=sys.stderr)
        print("Tip: download the list and pass --source-file theme-color.md", file=sys.stderr)
        return 2

    if not documented:
        print("ERROR: parsed 0 colors - the source format may have changed.", file=sys.stderr)
        return 2

    schema, newline = load_json(schema_path)
    props = schema_color_props(schema)
    schema_keys = set(props)
    doc_keys = set(documented)

    missing = sorted(doc_keys - schema_keys)            # add to schema
    stale = sorted(schema_keys - doc_keys)              # review / maybe deprecated

    print(f"documented colors : {len(doc_keys)}")
    print(f"schema colors     : {len(schema_keys)}")
    print(f"missing (add)     : {len(missing)}")
    print(f"stale (review)    : {len(stale)}")

    if missing:
        print("\n--- MISSING (documented, not in schema) ---")
        for k in missing:
            print(f"  + {k}: {documented[k]}")

    if stale:
        print("\n--- STALE (in schema, not documented) ---")
        for k in stale:
            print(f"  ? {k}")

    # Bonus: keys the theme actually uses that no source recognizes (typos/unknowns).
    theme_path = Path(args.theme)
    if theme_path.exists():
        theme, _ = load_json(theme_path)
        used = set(theme.get("colors", {}))
        unknown = sorted(used - doc_keys - schema_keys)
        print(f"\ntheme uses {len(used)} color keys; unrecognized by docs+schema: {len(unknown)}")
        for k in unknown:
            print(f"  ! {k}  (typo or very new key?)")

    if args.write and missing:
        # Surgical text insertion: the schema uses a compact hand-formatted style
        # (inline arrays, first key on the "properties" line), so re-dumping the
        # whole object would reformat 4000+ lines. Instead, insert each new entry
        # as text right before its alphabetically-next existing key, keeping the
        # diff additions-only.
        raw = schema_path.read_text(encoding="utf-8")
        nl = "\r\n" if "\r\n" in raw else "\n"
        lines = raw.split(nl)
        all_keys = sorted(schema_keys | set(missing))

        def next_existing(key: str) -> str | None:
            i = all_keys.index(key)
            for j in range(i + 1, len(all_keys)):
                if all_keys[j] in schema_keys:
                    return all_keys[j]
            return None

        def entry_block(key: str) -> list[str]:
            return [
                f'        "{key}": {{',
                '          "type": "string",',
                '          "format": "color",',
                f'          "description": {json.dumps(documented[key], ensure_ascii=False)}',
                "        },",
            ]

        groups: dict[str, list[str]] = {}
        skipped = []
        for k in missing:
            anchor = next_existing(k)
            if anchor is None:  # sorts after every existing key; not expected here
                skipped.append(k)
                continue
            groups.setdefault(anchor, []).append(k)

        inserts = []
        for anchor, keys in groups.items():
            idx = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith(f'"{anchor}":')), None)
            if idx is None:
                skipped.extend(keys)
                continue
            blk = [line for k in sorted(keys) for line in entry_block(k)]
            inserts.append((idx, blk))

        for idx, blk in sorted(inserts, key=lambda x: -x[0]):
            lines[idx:idx] = blk

        out = nl.join(lines)
        json.loads(out)  # validate before writing
        schema_path.write_text(out, encoding="utf-8")
        wrote = len(missing) - len(skipped)
        print(f"\nWROTE {wrote} new entries to {schema_path}")
        if skipped:
            print(f"  skipped {len(skipped)} (no anchor): {', '.join(skipped)}")
    elif args.write:
        print("\nnothing to write - schema already current.")
    elif missing:
        print("\nrun with --write to add the missing entries.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
