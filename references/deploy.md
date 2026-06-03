# Deploying a PR guide & linking it from the PR

This is the workflow for the **zo workspace** (the maintainer's static site).
After you've built a guide for a PR, publish it and drop a link into the PR. The
guide-authoring above is generic; this deploy step is environment-specific.

## Where it goes — naming & namespace

Static content root: `projects/static/public/`, served at `https://static.mseeks.me`.
nginx serves clean URLs (`try_files $uri $uri.html`), so a file at
`public/X/Y.html` resolves at `https://static.mseeks.me/X/Y` (no `.html`).

Write the guide to:

```
projects/static/public/read-thru/<repo>/pr-<number>-<slug>.html
```

- `<repo>` — the repository the PR is in (e.g. `froot`).
- `<number>` — the PR number.
- `<slug>` — a short kebab summary of the PR (3–6 words), chosen **once**. On PR
  updates, rebuild into the **same filename** so the URL is stable (idempotent).

Example: PR #42 on `froot` about clean-URL routing →
`public/read-thru/froot/pr-42-clean-url-routing.html`.

## Steps

1. **Build** the guide (tier S–M; see [`depth-and-scope.md`](./depth-and-scope.md)):
   ```sh
   read-thru build doc.py --source <repo-root> \
     --out projects/static/public/read-thru/<repo>/pr-<n>-<slug>.html
   ```
   (create the `read-thru/<repo>/` dirs if needed).
2. **Publish** — commit and push the **static** repo's `main`. Its GitHub CI
   builds and pushes `ghcr.io/mseeks/static:latest`.
3. **Deploy** — from the zo root, roll the static deployment to pull the new image:
   ```sh
   infra/k8s/static/install.sh
   ```
4. **Link it in the PR** — add a **bare link, no preamble**, to the clean URL
   (no `.html`) in the PR body:
   ```
   https://static.mseeks.me/read-thru/<repo>/pr-<n>-<slug>
   ```
   Just the URL on its own line — no "Here's a reading guide:" lead-in.

## Notes

- The site uses nginx `autoindex`, so no index/manifest needs updating — the new
  page appears on its own.
- `Cache-Control: no-cache` plus reusing the same filename means an updated guide
  is live right after the rollout completes.
- If the cluster isn't reachable from where you're running, do steps 1–2 (commit
  the file) and note that the rollout (step 3) still needs to run.
