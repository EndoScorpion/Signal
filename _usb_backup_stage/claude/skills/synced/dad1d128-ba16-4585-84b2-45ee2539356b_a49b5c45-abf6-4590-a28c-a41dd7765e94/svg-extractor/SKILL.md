---
name: svg-extractor
description: >
  Extract, clean, and back up all inline SVG elements from any HTML file or
  pasted HTML content. Use this skill when the user wants to: (1) extract SVGs
  from an HTML file, (2) back up inline SVG assets as standalone .svg files,
  (3) find all SVGs in a page and list their dimensions, (4) save SVG assets
  locally. Triggers: "extract SVGs", "backup SVGs", "pull out SVGs", "save SVG
  assets", "find all SVGs in this file", "export inline SVGs".
---

# SVG Content Extraction & Local Backup Skill

## Role

Act as an Expert Asset Extraction Assistant. Scan HTML for inline `<svg>`
elements, clean them up, name them intelligently, and deliver them as
standalone `.svg` files or a download script.

## Workflow

### Step 1 — Detect input type

- **Uploaded HTML file**: run `scripts/extract_svgs.py` directly on it
- **Pasted HTML in chat**: write it to a temp file, then run the script
- **URL**: fetch with `web_fetch`, save to temp file, then run the script

### Step 2 — Run the extraction script

```bash
pip install beautifulsoup4 lxml --break-system-packages -q
python3 scripts/extract_svgs.py <input.html> --output svg_backups/
```

The script will:
1. Count all `<svg>` tags found
2. Inject `xmlns="http://www.w3.org/2000/svg"` if missing
3. Name each file by `id` → `class` → `data-name` → sequential fallback
4. Prettify XML formatting
5. Write each to `svg_backups/`

### Step 3 — Report to user

After extraction state:
- Total SVGs detected
- List: filename + dimensions (width/height or viewBox) for each
- Any SVGs that were missing xmlns (and were patched)

### Step 4 — Deliver files

Call `present_files` with all extracted `.svg` files so the user can download them.

## Naming convention

| Priority | Source | Example output |
|---|---|---|
| 1 | `id` attribute | `1_logo.svg` |
| 2 | `class` attribute | `2_icon_nav.svg` |
| 3 | `data-name` attribute | `3_hero_graphic.svg` |
| 4 | fallback | `extracted_svg_4.svg` |

## Notes

- Always inject `xmlns` if missing — required for standalone SVG files
- Use `lxml` parser for self-closing tag fidelity (e.g. `<path/>`)
- Strip unsafe characters from names: `[^\w\-]` → `_`
- If 0 SVGs found, say so clearly and check if the file was minified (SVGs
  sometimes appear as data URIs or base64 — flag this to the user)

## Script location

`scripts/extract_svgs.py` — see below. Read it before running.
