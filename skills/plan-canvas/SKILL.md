---
name: plan-canvas
description: >-
  Generate a self-contained, human-readable HTML plan or handoff artifact for passing work to a teammate or another agent. Use whenever the user wants to write up, generate, or hand off a plan/spec/proposal — especially as HTML rather than markdown — or mentions a handoff, /handoff, /plans, a "plan canvas", or an interactive/printable plan. Also use it to compact the current conversation into a handoff document so a fresh agent can continue the work — summarizing state, referencing existing artifacts (PRDs, plans, ADRs, issues, commits, diffs) by path/URL instead of duplicating them, redacting secrets, and listing suggested skills for the next session. Strongly prefer this skill any time "handoff" or "hand off" comes up in the context of passing work to a developer or agent. Produces a single offline .html with collapsible phases, persistent task checklists, an in-page toolbar (expand/collapse all, copy remaining work as a prompt, copy as Markdown, reset progress), an editable notes box, and a changelog that tracks edits across regenerations; renders in any browser or IDE preview and prints cleanly.
argument-hint: "(optional) what the next session will focus on"
---
  
# Plan Canvas

Turns a plan you've worked out into a polished, **self-contained HTML artifact** for handoff. One file, no server, no network, no build step. It opens in any browser or IDE preview pane, and prints cleanly.

The artifact uses a dark, purple-accented "handoff document" theme: a sticky app bar (brand + progress + controls), a two-column layout with an auto-generated contents rail, and numbered phase cards. All of that chrome is supplied by the template — you only author the plan body.

## When to use

The user is a team lead who hands plans to developers or agents and wants HTML instead of markdown. Trigger on requests like "write this up as a plan", "hand this off to …", "generate a handoff doc", "/handoff", "make a plan canvas", "put this in /plans", or any ask for an interactive or printable plan. Treat the word **handoff** (or "hand off") as a strong signal even when the user doesn't say "HTML" — this skill is the default way to package work for someone else to pick up.

It serves two related jobs that share one pipeline:
- **Plan mode** — you've worked out a plan and want a durable, committable artifact in `./plans`.
- **Conversation-handoff mode** — the user wants to *compact the current conversation* into a doc a fresh agent can pick up ("hand off this session", "/handoff", "write up where we are"). Same components and assembly; the difference is the content rules and output location in **[Conversation-handoff mode](#conversation-handoff-mode)** below. If the user passed an argument, treat it as what the next session will focus on and tailor the doc to it.

## Workflow

1. **Do the thinking first.** Figure out the actual plan — phases, tasks, files to touch, risks, acceptance criteria — before writing any HTML. The artifact is a presentation layer; the substance is the plan itself.

2. **Write the body** as an HTML fragment to a scratch file in the output folder, `./plans/.plan-body.html` (create `./plans/` if needed) — keep everything inside the project workspace, not `/tmp`, since sandboxed agents like Copilot can only write within the workspace. The leading dot keeps it out of a `plans/*.html` listing. This file is everything that goes *inside* the page; do not write `<html>`, `<head>`, `<style>`, or `<script>` — the template supplies all chrome, CSS, and JS. Use the component vocabulary below. It's a throwaway — delete it once you've assembled (step 3).

3. **Assemble** into the output file, then remove the scratch body:
   ```bash
   python3 <skill-dir>/assemble.py plans/.plan-body.html plans/<slug>.html \
     --title "Short plan title" --change "Initial plan." --author "Kostas"
   rm plans/.plan-body.html
   ```
   - Output goes in **`./plans/`** (project-relative), created if missing.
   - **Choosing `<slug>`** (kebab-case `.html`) — derive it in this priority:
     1. A **Jira ticket** if one is mentioned anywhere in the conversation, e.g. `PROJ-1234` → `proj-1234.html` (optionally append a short topic: `proj-1234-auth-rate-limiting.html`).
     2. Else the **current git branch** — `git rev-parse --abbrev-ref HEAD`, with any `feature/`, `fix/`, etc. prefix stripped and the rest slugified (branch `feature/ABC-12-rate-limit` → `abc-12-rate-limit.html`).
     3. Else a **topic slug** you derive from the plan itself (e.g. `auth-rate-limiting.html`).

     The slug also keys localStorage, so it must stay stable across regenerations to preserve a teammate's checkbox progress — a ticket or branch is ideal because it's tied to the work, not the wording, so revisions land on the same file.
   - `--title` is optional; if omitted it's derived from the first `<h1>`.
   - `--change` / `--author` add a dated changelog entry (see *Revising* below). On a brand-new plan you can pass `--change "Initial plan."` or omit it — the script auto-seeds an "Initial plan." entry on first generation.

4. **Tell the user** the path and that it's a single portable file they can open, commit, email, or print. The artifact ships with a screen-only toolbar (in the sticky app bar), a progress bar, an auto-built contents rail, and an editable Notes box — all template chrome, so you don't author them:
   - **Expand all / Collapse all** — toggle every phase.
   - **Copy remaining as prompt** — serializes the *unchecked* tasks (grouped by phase) plus the notes into a paste-ready prompt, so whoever holds the plan can hand the remaining work to the next agent mid-flight.
   - **Copy as Markdown** — the whole plan as Markdown (checkbox state preserved) for Slack/PR/another prompt.
   - **Reset progress** — clears the checklist (asks first).

   The export reads `details.phase` → `label.task` → `.task-text` straight from the DOM, so the *only* thing that makes it useful is clean task markup — another reason to express real work as `.task` checkboxes (below), not loose prose.

## Revising an existing plan

When you (or another agent) change a plan that already exists, **regenerate to the same path** so checkbox progress and changelog history are preserved, and record what changed with `--change`:

```bash
python3 <skill-dir>/assemble.py plans/.plan-body.html plans/auth-rate-limiting.html \
  --change "Split phase 2 into middleware + tests; added Redis fallback risk." \
  --author "agent" --commit auto
```

The script reads the prior artifact at that path, carries its changelog entries forward, and prepends the new dated entry — so the artifact tells the story of how the plan evolved. Keep the changelog placeholder in the body (below) every time; the merge needs it.

**Recording the commit.** When an agent revises the doc as part of a committed change, pass `--commit` so the changelog row carries the commit ref. Use `--commit auto` (or `--commit HEAD`) to stamp the current HEAD short SHA, or pass an explicit SHA. If the work is committed *after* regenerating, run assemble once more with `--commit <sha>` (same `--change`) so the ref points at the real commit. The ref is linked to the `origin` remote's commit page when one can be derived (GitHub/GitLab/Bitbucket).

## Conversation-handoff mode

When the goal is to hand the **current conversation** to a fresh agent (rather than write up a plan you've designed), use the same body components and `assemble.py`, but follow these rules:

1. **Summarize state, don't transcribe.** Capture what a new agent needs to continue: the goal, what's been done, what's in flight, decisions made and *why*, current blockers, and the obvious next step. Put the single best starting point in the `.handoff` block ("Start here:").

2. **Reference, don't duplicate.** Do not re-paste content already captured in other artifacts — PRDs, plans, ADRs, issues, commits, diffs, existing `./plans/*.html`. Link them by path or URL (use `<span class="file">` for paths, `<a>` for URLs) and summarize only what's needed to orient.

3. **Redact sensitive information.** Strip API keys, tokens, passwords, connection strings, and PII before they reach the body. If a value matters, refer to it by name (e.g. "the staging DB password in 1Password") rather than its value.

4. **Tailor to the next session's focus.** If the user passed an argument (what the next session is for), shape the summary, the phases/tasks, and "Start here" around that focus.

5. **Include a "Suggested skills" section** (component below) listing skills the next agent should invoke and when.

6. **Output location.** A conversation handoff is usually *ephemeral* and shouldn't be committed to the repo. Write it to the OS temp dir, deriving the path from `$TMPDIR` (e.g. `"$TMPDIR/<slug>.html"` on macOS, `/tmp/<slug>.html` elsewhere) instead of `./plans/`. Write the scratch body there too (e.g. `"$TMPDIR/.plan-body.html"`). Exception: a sandboxed agent (e.g. Copilot) that can only write inside the workspace should fall back to `./plans/` (gitignored if it must not be committed). When it *is* a durable plan, keep the default `./plans/` location.

Everything else — slug choice, `--change`/`--commit`, regeneration to the same path — works the same.

## Component vocabulary

Write the body using these classes/elements — they're all styled by the template (light + dark, screen + print).

**Header (start the body with this):**
```html
<header class="plan-head">
  <h1>Rate-limit the auth endpoints</h1>
  <div class="meta">
    <span><b>Created by:</b> <!--PLAN_OWNER--></span>
    <span><b>Date:</b> 2026-06-17</span>
  </div>
</header>
```
> **Don't author a progress bar.** Progress lives in the template's sticky app bar (ids `pc-progress-fill` / `pc-progress-label`) and is filled automatically from the checklist — the body should start straight at the `<header class="plan-head">`.
>
> **Don't author a contents/TOC list.** The template builds the contents rail automatically from your `details.phase` summaries (when there are ≥2 phases), with scrollspy.
>
> Leave `<!--PLAN_OWNER-->` in the "Created by" field as-is: `assemble.py` fills it from `git config user.name` (override with `--owner "Name"`). Don't hardcode a name.

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
- File / code refs: `<span class="file">path/to/file.ts:88</span>`, inline `<code>`. Always write the **full path** — the template auto-shortens long paths to just the filename on screen (full path on hover and in copied exports), so you never need to abbreviate yourself.
- Code/commands: `<pre><code>…</code></pre>`
- Callouts: `<div class="note">…</div>` and `<div class="warn">…</div>`
- Tables: plain `<table>` (styled automatically)
- **Handoff block** (recommended near the end): assumptions, open questions, and an explicit "start here":
  ```html
  <div class="handoff">
    <h2>Handoff notes</h2>
    <p><b>Start here:</b> …</p>
    <ul><li>Assumption: …</li><li>Open question: …</li></ul>
  </div>
  ```
- **Referenced artifacts** (conversation-handoff mode): instead of duplicating existing docs, list them so the next agent can open them. A plain section with a table or list works:
  ```html
  <section>
    <h2>Referenced artifacts</h2>
    <ul>
      <li><span class="file">docs/prd-auth.md</span> — product requirements</li>
      <li><a href="https://jira/PROJ-1234">PROJ-1234</a> — tracking ticket</li>
      <li><span class="file">plans/auth-rate-limiting.html</span> — the detailed plan</li>
    </ul>
  </section>
  ```
- **Suggested skills** (recommended for conversation handoffs): the skills the next agent should reach for, and when. Use a `.note` callout or a small table:
  ```html
  <section>
    <h2>Suggested skills</h2>
    <table>
      <thead><tr><th>Skill</th><th>When to use</th></tr></thead>
      <tbody>
        <tr><td><code>verify</code></td><td>After wiring the limiter, confirm it rejects over-limit requests.</td></tr>
        <tr><td><code>code-review</code></td><td>Before opening the PR.</td></tr>
      </tbody>
    </table>
  </section>
  ```
- **Changelog** (include once, near the end): a record of how the plan evolved. Always emit the list with the exact id and placeholder so `assemble.py` can merge prior history into it:
  ```html
  <section class="changelog">
    <h2>Changelog</h2>
    <ol class="changelog-list" id="pc-changelog-list"><!--PLAN_CHANGELOG--></ol>
  </section>
  ```
  > Leave the `<ol>` empty apart from `<!--PLAN_CHANGELOG-->`. The script fills it: the new `--change` entry on top, then everything from the previous artifact. Don't hand-write `<li>` entries — pass them via `--change` so dates and order stay consistent.

**Diagrams — inline SVG only.** When a flow/architecture/sequence diagram helps, hand-author it as inline SVG (no external runtime is bundled). Wrap it so it scales and prints:
```html
<figure class="diagram">
  <svg viewBox="0 0 480 120" role="img" aria-label="request flow">…</svg>
  <figcaption>Request flow</figcaption>
</figure>
```
Keep diagrams simple; prefer a clear table or list when a diagram wouldn't add much. Use `currentColor` / neutral strokes so they read in light and dark.

## Conventions

- **Self-contained, always.** Never add `<script src=…>` or `<link href=…>` to a CDN. Everything must work offline and in a sandboxed preview.
- **Checklists are the unit of progress.** Express actionable work as `.task` checkboxes so the progress bar and localStorage persistence are meaningful.
- **Plain HTML in the body.** No frameworks, no inline `<style>`/`<script>` in the body unless a one-off diagram genuinely needs a tiny inline `<style>`.
- Default phases to `open` so the plan reads top-to-bottom and prints fully.
