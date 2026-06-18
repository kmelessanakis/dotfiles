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
import datetime
import html
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.html")

OWNER_PLACEHOLDER = "<!--PLAN_OWNER-->"
CHANGELOG_PLACEHOLDER = "<!--PLAN_CHANGELOG-->"
CHANGELOG_LIST_RE = re.compile(
    r'<ol[^>]*\bid="pc-changelog-list"[^>]*>(.*?)</ol>',
    re.IGNORECASE | re.DOTALL,
)


def git_user_name() -> str:
    """Best-effort current owner from git config; empty string if unavailable."""
    try:
        out = subprocess.run(["git", "config", "user.name"],
                             capture_output=True, text=True, timeout=3)
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def git_short_sha(ref: str = "HEAD") -> str:
    """Short SHA for a ref via git; empty string if unavailable."""
    try:
        out = subprocess.run(["git", "rev-parse", "--short", ref],
                             capture_output=True, text=True, timeout=3)
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def git_remote_commit_url(sha: str) -> str:
    """Best-effort web URL for a commit on the `origin` remote (GitHub/GitLab/
    Bitbucket, ssh or https). Empty string if it can't be derived."""
    if not sha:
        return ""
    try:
        out = subprocess.run(["git", "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=3)
        if out.returncode != 0:
            return ""
        url = out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    m = re.match(r"git@([^:]+):(.+?)(?:\.git)?$", url)
    if not m:
        m = re.match(r"https?://(?:[^@]+@)?([^/]+)/(.+?)(?:\.git)?$", url)
    if not m:
        return ""
    host, path = m.group(1), m.group(2)
    seg = "commits" if "bitbucket" in host else "commit"
    return "https://{}/{}/{}/{}".format(host, path, seg, sha)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    text = re.sub(r"[\s_-]+", "-", text)
    return text or "plan"


def extract_prior_changelog(output_path: str) -> str:
    """Return the inner HTML of an existing artifact's changelog list, if any.

    Lets a teammate's accumulated history survive a regeneration, the same way
    checkbox state survives via a stable filename. A leftover placeholder or the
    'no changes yet' empty-state line is dropped so it never piles up.
    """
    if not os.path.exists(output_path):
        return ""
    try:
        with open(output_path, encoding="utf-8") as f:
            prev = f.read()
    except OSError:
        return ""
    m = CHANGELOG_LIST_RE.search(prev)
    if not m:
        return ""
    inner = m.group(1)
    inner = inner.replace(CHANGELOG_PLACEHOLDER, "")
    inner = re.sub(r'<li[^>]*\bclass="empty"[^>]*>.*?</li>', "", inner,
                   flags=re.IGNORECASE | re.DOTALL)
    return inner.strip()


def build_change_entry(change: str, author: str, date: str,
                       commit: str = "", commit_url: str = "") -> str:
    bits = ['<time>{}</time>'.format(html.escape(date))]
    if author:
        bits.append('<span class="who">{}</span>'.format(html.escape(author)))
    bits.append("— " + html.escape(change))
    if commit:
        if commit_url:
            bits.append('<a class="commit" href="{}">{}</a>'.format(
                html.escape(commit_url), html.escape(commit)))
        else:
            bits.append('<code class="commit">{}</code>'.format(html.escape(commit)))
    return "<li>" + " ".join(bits) + "</li>"


def inject_changelog(body: str, output_path: str, change: str,
                     author: str, date: str,
                     commit: str = "", commit_url: str = "") -> str:
    """Fill the body's changelog placeholder with a merged history.

    New entry (if a --change was given, or an auto 'Initial plan.' on first
    generation) goes on top, followed by everything carried over from the
    previous artifact.
    """
    if CHANGELOG_PLACEHOLDER not in body:
        if change:
            print("warning: --change given but the body has no changelog list "
                  '(<ol class="changelog-list" id="pc-changelog-list">'
                  + CHANGELOG_PLACEHOLDER + "</ol>); entry was dropped.",
                  file=sys.stderr)
        return body

    prior = extract_prior_changelog(output_path)
    first_generation = not os.path.exists(output_path) and not prior

    entries = []
    if change:
        entries.append(build_change_entry(change, author, date, commit, commit_url))
    elif first_generation:
        entries.append(build_change_entry("Initial plan.", author, date, commit, commit_url))

    merged = "\n".join(entries + ([prior] if prior else []))
    if not merged:
        merged = '<li class="empty">No changes recorded yet.</li>'
    return body.replace(CHANGELOG_PLACEHOLDER, merged)


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
    ap.add_argument("--owner", default=None,
                    help="plan owner; defaults to `git config user.name`")
    ap.add_argument("--change", default=None,
                    help="summary of what changed; prepended as a dated changelog entry")
    ap.add_argument("--author", default=None,
                    help="who made the change (changelog entry); defaults to the owner")
    ap.add_argument("--date", default=datetime.date.today().isoformat(),
                    help="date for the changelog entry (default: today, YYYY-MM-DD)")
    ap.add_argument("--commit", default=None,
                    help="commit ref shown on the changelog entry; pass a SHA, or "
                         "'auto'/'HEAD' to use the current HEAD short SHA. Linked to "
                         "the origin remote when one can be derived.")
    args = ap.parse_args()

    with open(args.body, encoding="utf-8") as f:
        body = f.read()
    with open(TEMPLATE, encoding="utf-8") as f:
        template = f.read()

    # Owner: explicit flag wins, else current git user. Fills the <!--PLAN_OWNER-->
    # placeholder in the header meta; harmless if the body doesn't use it.
    owner = args.owner if args.owner is not None else git_user_name()
    body = body.replace(OWNER_PLACEHOLDER, html.escape(owner))

    # Resolve the commit ref (explicit SHA, or auto/HEAD -> current short SHA).
    commit = args.commit or ""
    if commit.lower() in ("auto", "head"):
        commit = git_short_sha("HEAD")
    commit_url = git_remote_commit_url(commit) if commit else ""

    # Merge changelog history before the output file is overwritten below.
    author = args.author if args.author is not None else owner
    body = inject_changelog(body, args.output, args.change or "",
                            author or "", args.date, commit, commit_url)

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
