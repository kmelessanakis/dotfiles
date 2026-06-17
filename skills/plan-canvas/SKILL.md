---
name: plan-canvas
description: >-
  Generate a self-contained, human-readable HTML plan artifact for handing off
  work to a teammate or an agent. Use when the user (a team lead) asks to write,
  generate, or hand off a plan/spec/proposal as an HTML file (not markdown), or
  mentions /plans, a "plan canvas", or an interactive/printable plan. Produces a
  single offline .html in ./plans with collapsible phases, persistent task
  checklists, an in-page toolbar (expand/collapse all, print/PDF, reset progress),
  and a changelog that tracks edits across regenerations; renders in a browser or
  IDE preview and exports to PDF via Playwright.
---

# Plan Canvas

Turns a plan you've worked out into a polished, **self-contained HTML artifact**
for handoff. One file, no server, no network, no build step. It opens in any
browser or IDE preview pane, and prints/exports to PDF cleanly (e.g. Playwright
`page.pdf()`).

## When to use

The user is a team lead who hands plans to developers or agents and wants HTML
instead of markdown. Trigger on requests like "write this up as a plan",
"generate a handoff doc", "make a plan canvas", "put this in /plans", or any ask
for an interactive or printable plan.

## Workflow

1. **Do the thinking first.** Figure out the actual plan — phases, tasks, files
   to touch, risks, acceptance criteria — before writing any HTML. The artifact
   is a presentation layer; the substance is the plan itself.

2. **Write the body** as an HTML fragment to a temp file (e.g.
   `/tmp/plan-body.html`). This is everything that goes *inside* the page; do not
   write `<html>`, `<head>`, `<style>`, or `<script>` — the template supplies all
   chrome, CSS, and JS. Use the component vocabulary below.

3. **Assemble** into the output file:
   ```bash
   python3 <skill-dir>/assemble.py /tmp/plan-body.html plans/<slug>.html \
     --title "Short plan title" --change "Initial plan." --author "Kostas"
   ```
   - Output goes in **`./plans/`** (project-relative), created if missing.
   - `<slug>` is kebab-case (e.g. `auth-rate-limiting.html`). The slug also keys
     localStorage, so keep filenames stable across regenerations to preserve a
     teammate's checkbox progress.
   - `--title` is optional; if omitted it's derived from the first `<h1>`.
   - `--change` / `--author` add a dated changelog entry (see *Revising* below).
     On a brand-new plan you can pass `--change "Initial plan."` or omit it — the
     script auto-seeds an "Initial plan." entry on first generation.

4. **Tell the user** the path and that it's a single portable file they can open,
   commit, email, or render to PDF. The artifact ships with a screen-only toolbar
   and an editable Notes box — both template chrome, so you don't author them:
   - **Expand all / Collapse all** — toggle every phase.
   - **Copy remaining as prompt** — serializes the *unchecked* tasks (grouped by
     phase) plus the notes into a paste-ready prompt, so whoever holds the plan can
     hand the remaining work to the next agent mid-flight.
   - **Copy as Markdown** — the whole plan as Markdown (checkbox state preserved)
     for Slack/PR/another prompt.
   - **Reset progress** — clears the checklist (asks first).

   The export reads `details.phase` → `label.task` → `.task-text` straight from the
   DOM, so the *only* thing that makes it useful is clean task markup — another
   reason to express real work as `.task` checkboxes (below), not loose prose.

## Revising an existing plan

When you (or another agent) change a plan that already exists, **regenerate to the
same path** so checkbox progress and changelog history are preserved, and record
what changed with `--change`:

```bash
python3 <skill-dir>/assemble.py /tmp/plan-body.html plans/auth-rate-limiting.html \
  --change "Split phase 2 into middleware + tests; added Redis fallback risk." \
  --author "agent"
```

The script reads the prior artifact at that path, carries its changelog entries
forward, and prepends the new dated entry — so the artifact tells the story of how
the plan evolved. Keep the changelog placeholder in the body (below) every time;
the merge needs it.

## Component vocabulary

Write the body using these classes/elements — they're all styled by the template
(light + dark, screen + print).

**Header (start with this):**
```html
<header class="plan-head">
  <h1>Rate-limit the auth endpoints</h1>
  <div class="meta">
    <span><b>Owner:</b> <!--PLAN_OWNER--></span>
    <span><b>Date:</b> 2026-06-17</span>
    <span class="pill doing">In progress</span>
  </div>
</header>

<div class="progress">
  <div class="bar"><span id="pc-progress-fill"></span></div>
  <div class="label" id="pc-progress-label"></div>
</div>
```
> Always include the `.progress` block with the exact ids `pc-progress-fill` and
> `pc-progress-label` — the script fills them from the checklist state.
>
> Leave `<!--PLAN_OWNER-->` in the Owner field as-is: `assemble.py` fills it from
> `git config user.name` (override with `--owner "Name"`). Don't hardcode a name.

**Phases (collapsible, open by default, auto-expanded when printed):**
```html
<details class="phase" open>
  <summary><span class="phase-num">1.</span> Add the limiter middleware</summary>
  <div class="phase-body">
    <p>Context / what & why…</p>
    <ul class="tasks">
      <li><label class="task"><input type="checkbox"><span class="task-text">
        Create <span class="file">src/middleware/rateLimit.ts</span></span></label></li>
      <li><label class="task"><input type="checkbox"><span class="task-text">
        Wire it into <span class="file">src/routes/auth.ts:42</span></span></label></li>
    </ul>
  </div>
</details>
```

**Other pieces:**
- Status pills: `<span class="pill todo|doing|done">…</span>`
- File / code refs: `<span class="file">path/to/file.ts:88</span>`, inline `<code>`
- Code/commands: `<pre><code>…</code></pre>`
- Callouts: `<div class="note">…</div>` and `<div class="warn">…</div>`
- Tables: plain `<table>` (styled automatically)
- **Handoff block** (recommended near the end): assumptions, open questions,
  and an explicit "start here":
  ```html
  <div class="handoff">
    <h2>Handoff notes</h2>
    <p><b>Start here:</b> …</p>
    <ul><li>Assumption: …</li><li>Open question: …</li></ul>
  </div>
  ```
- **Changelog** (include once, near the end): a record of how the plan evolved.
  Always emit the list with the exact id and placeholder so `assemble.py` can merge
  prior history into it:
  ```html
  <section class="changelog">
    <h2>Changelog</h2>
    <ol class="changelog-list" id="pc-changelog-list"><!--PLAN_CHANGELOG--></ol>
  </section>
  ```
  > Leave the `<ol>` empty apart from `<!--PLAN_CHANGELOG-->`. The script fills it:
  > the new `--change` entry on top, then everything from the previous artifact.
  > Don't hand-write `<li>` entries — pass them via `--change` so dates and order
  > stay consistent.

**Diagrams — inline SVG only.** When a flow/architecture/sequence diagram helps,
hand-author it as inline SVG (no external runtime is bundled). Wrap it so it
scales and prints:
```html
<figure class="diagram">
  <svg viewBox="0 0 480 120" role="img" aria-label="request flow">…</svg>
  <figcaption>Request flow</figcaption>
</figure>
```
Keep diagrams simple; prefer a clear table or list when a diagram wouldn't add
much. Use `currentColor` / neutral strokes so they read in light and dark.

## Conventions

- **Self-contained, always.** Never add `<script src=…>` or `<link href=…>` to a
  CDN. Everything must work offline and in a sandboxed preview.
- **Checklists are the unit of progress.** Express actionable work as `.task`
  checkboxes so the progress bar and localStorage persistence are meaningful.
- **Plain HTML in the body.** No frameworks, no inline `<style>`/`<script>` in the
  body unless a one-off diagram genuinely needs a tiny inline `<style>`.
- Default phases to `open` so the plan reads top-to-bottom and prints fully.

## Export to PDF (optional)

If the user wants a PDF, render the generated file with Playwright:
```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto("file:///abs/path/to/plans/<slug>.html")
    pg.pdf(path="plans/<slug>.pdf", print_background=True, format="A4")
    b.close()
```
Collapsed phases auto-expand for print, and on-screen-only affordances are hidden.
