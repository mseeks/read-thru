# Depth & document size

Depth is driven mostly by what you're handed — a one-file fix and a whole-repo
tour are not the same document. But pick a **tier** up front so runs stay
consistent: a reviewer should be able to predict roughly how long a read-thru
guide is from the size of the thing it covers.

Rule of thumb: **pick the smallest tier that lets a reviewer vouch for the
change.** Prefer `peek` snippets over whole files unless the file *is* the point.
Padding a small change to look thorough wastes the reader; under-covering a big
one breaks trust.

| Tier | Covers | Sections | Words | Code shown |
|---|---|---|---|---|
| **XS** | a function / a snippet | 1–3 | ~300–800 | tight `peek` ranges |
| **S–M** | **a PR (default)** | 3–8 | ~1k–3k | changed lines via `peek`, plus the context needed to read them |
| **M** | a module / a feature | 6–12 | ~2k–5k | spotlight key functions, fold boilerplate |
| **L** | a whole repo | 20–50 | as needed | every file in full (`ALL_FILES`), optional lite cut |

## PR guides (the common case)

A PR guide answers: *what changed, why, and is it safe to merge?* Structure:

1. **Overview** — the change in 3–6 sentences: what, why, blast radius.
2. **One section per meaningful changed file (or cluster)** — `peek` the new/
   changed lines, narrate what to notice, and pull in just enough surrounding
   context (the function it lives in, the type it returns) to read them.
3. **A "why / risk" beat** — a `callout("why", …)` or `callout("gotcha", …)`
   where a reviewer would be skeptical: invariants touched, edge cases, migration.
4. **(optional) Verification** — how the change was tested, or what to check.

Find the changed files with `git diff --name-only <base>...<head>` and the line
ranges with the diff hunks. Show the code at HEAD (the merged state), not the
diff itself — read-thru renders verbatim source, and the narrative explains the
delta.

Scale within the tier by the PR's real size: a 1-file fix is XS; a 15-file
feature trends toward M. Don't invent sections to hit a count.

## Whole-repo guides (tier L)

Only when the ask is "explain this whole codebase." Then follow the full
methodology in [`process.md`](./process.md): plan an arc, assign a focus
technique per section, set `ALL_FILES` to enforce the completeness contract, and
consider a lite cut (`content_lite.py`) for the reviewer who wants the essential
quarter. The bundled `examples/froot/` is the worked L example.

## Calibrate against the goldens

- `examples/pr-sample/` — a tight **S** PR guide (4 sections). Self-contained
  (documents read-thru's own code) and the only one with a committed render:
  read `content.py` for the shape and prose level, open `sample.html` for the
  rendered target. **Start here.**
- `examples/froot-uv-pr/` — a real, meatier **M** PR (10 sections: froot's uv
  ecosystem change). Read `content.py` for how a substantial PR is structured.
  (Rebuilds only against the froot revision that has the uv adapter.)
- `examples/froot/` — the **L** exemplar (50 sections, every line of a 2,986-line repo).
