#!/usr/bin/env python3
"""
extract_svgs.py — Extract all inline <svg> elements from an HTML file.
Part of the svg-extractor Claude skill.

Usage:
  python3 scripts/extract_svgs.py input.html
  python3 scripts/extract_svgs.py input.html --output ./my_svgs/
  python3 scripts/extract_svgs.py input.html --output ./my_svgs/ --list-only
"""

import os
import re
import sys
import argparse
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing beautifulsoup4 + lxml...")
    os.system(f"{sys.executable} -m pip install beautifulsoup4 lxml --break-system-packages -q")
    from bs4 import BeautifulSoup


def get_dimensions(svg_tag):
    """Extract width/height or viewBox from an SVG tag."""
    vb = svg_tag.get('viewBox') or svg_tag.get('viewbox')
    w = svg_tag.get('width', '')
    h = svg_tag.get('height', '')
    if vb:
        return f"viewBox={vb}"
    if w or h:
        return f"{w}x{h}".strip('x')
    return "dimensions unknown"


def safe_name(raw):
    """Sanitize a string for use as a filename."""
    if isinstance(raw, list):
        raw = "_".join(raw)
    return re.sub(r'[^\w\-]', '_', str(raw)).strip('_')


def extract_svgs(html_path, output_folder="svg_backups", list_only=False):
    html_path = Path(html_path)
    if not html_path.exists():
        print(f"Error: '{html_path}' does not exist.")
        sys.exit(1)

    content = html_path.read_text(encoding='utf-8', errors='replace')

    # Try lxml first for best self-closing tag support, fall back to html.parser
    try:
        soup = BeautifulSoup(content, 'lxml')
    except Exception:
        soup = BeautifulSoup(content, 'html.parser')

    svg_tags = soup.find_all('svg')

    if not svg_tags:
        print("No inline <svg> tags found.")
        print("Note: SVGs may be embedded as data URIs or base64 — check manually.")
        return []

    print(f"Found {len(svg_tags)} SVG element(s).")

    if list_only:
        for i, svg in enumerate(svg_tags, 1):
            name_attr = svg.get('id') or svg.get('class') or svg.get('data-name')
            label = safe_name(name_attr) if name_attr else f"svg_{i}"
            dims = get_dimensions(svg)
            print(f"  {i}. {label} — {dims}")
        return []

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    saved = []
    patched_count = 0

    for i, svg in enumerate(svg_tags, 1):
        # Inject xmlns if missing
        if not svg.get('xmlns'):
            svg['xmlns'] = "http://www.w3.org/2000/svg"
            patched_count += 1

        # Determine filename
        name_attr = svg.get('id') or svg.get('class') or svg.get('data-name')
        if name_attr:
            filename = f"{i}_{safe_name(name_attr)}.svg"
        else:
            filename = f"extracted_svg_{i}.svg"

        file_path = output_folder / filename
        file_path.write_text(svg.prettify(), encoding='utf-8')

        dims = get_dimensions(svg)
        print(f"  ✅ {filename} — {dims}")
        saved.append(str(file_path))

    print(f"\nExported {len(saved)} SVG(s) to '{output_folder}/'")
    if patched_count:
        print(f"  ℹ️  {patched_count} SVG(s) were missing xmlns — patched automatically.")

    return saved


def main():
    parser = argparse.ArgumentParser(description="Extract inline SVGs from an HTML file.")
    parser.add_argument('input', help="Path to the HTML file")
    parser.add_argument('--output', '-o', default='svg_backups', help="Output folder (default: svg_backups/)")
    parser.add_argument('--list-only', '-l', action='store_true', help="List SVGs without saving")
    args = parser.parse_args()

    extract_svgs(args.input, args.output, args.list_only)


if __name__ == '__main__':
    main()
