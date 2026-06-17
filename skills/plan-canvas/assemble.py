#!/usr/bin/env python3
"""Assemble a self-contained plan HTML artifact from an agent-written body.

Usage:
    python3 assemble.py <body.html> <output.html> [--title "Plan title"]

- <body.html>  : HTML fragment for the plan body (everything inside <div class="wrap">).
- <output.html>: path to write the final self-contained file (e.g. plans/my-plan.html).
- --title      : page <title>; if omitted, derived from the first <h1> in the body,
                 else from the output filename.

Everything (CSS + JS) is inlined by the template, so the result needs no server
and no network. Diagrams are authored as inline SVG in the body, so they render
anywhere and export to PDF cleanly without any vendored runtime.
"""
import argparse
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text or "plan"


def derive_title(body: str, output: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.IGNORECASE | re.DOTALL)
    if m:
        # strip any inner tags, collapse whitespace
        raw = re.sub(r"<[^>]+>", "", m.group(1))
        title = html.unescape(re.sub(r"\s+", " ", raw)).strip()
        if title:
            return title
    return os.path.splitext(os.path.basename(output))[0].replace("-", " ").title()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("body")
    ap.add_argument("output")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    with open(args.body, encoding="utf-8") as f:
        body = f.read()
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()

    title = args.title or derive_title(body, args.output)
    plan_id = slugify(os.path.splitext(os.path.basename(args.output))[0])

    out = template
    out = out.replace("<!--PLAN_TITLE-->", html.escape(title))
    out = out.replace("<!--PLAN_ID-->", plan_id)
    out = out.replace("<!--PLAN_BODY-->", body)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(out)

    size_kb = os.path.getsize(args.output) / 1024
    print(f"wrote {args.output} — {size_kb:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
