# The read-thru process

How to turn a codebase into a guide a reviewer will *trust* — not just a pretty
dump of the source. This is the playbook used to produce the froot explainers.
Steps marked **(agent)** are driven by a coding agent (e.g. Claude Code); steps
marked **(script)** are the tooling in this repo.

The goal is a document where a reader can go top to bottom and come away able to
**vouch** for the code. Two things earn that: comprehension (the narrative), and
correctness (every claim checked against the source).

---

## 1. Ingest the whole codebase **(agent)**

Read *every* file — source, tests, infra, CI, config. Not a sample. The narrative
has a single authorial voice, and you can only write that voice once you hold the
whole thing in your head. Note the load-bearing invariants, the seams, the
security-critical lines, and the parts a reviewer would be skeptical of.

## 2. Plan the arc, then assign a *focus technique* per section **(agent)**

Order sections the way the dependencies point (usually pure core → seams → shell
→ entrypoints → tests → deploy → synthesis). Then, for each section, pick the
**one technique** that best teaches that file, and vary them so the reader never
settles into a rhythm. The palette:

- **spotlight** one function, fold the rest
- **annotated walkthrough** keyed to line ranges
- **counterfactual** — "delete this line and watch the blast radius"
- **truth-table** / **transition table**
- **execution trace** — follow one value through the system
- **sequence** or **state diagram**
- **Q&A** — pose the skeptical question, answer it from the code
- **evidence table** — claim → file:line
- **montage / gallery** — collect a repeated pattern in one place

Variety is not decoration; it is what keeps comprehension high across a long
read. Assign techniques centrally so no single method is overused.

## 3. Author the sections **(agent, using the read-thru DSL)**

Each `Section` is an ordered list of blocks: `prose()`, `callout()`, `table()`,
`diagram()`, `code()` (cheatsheet: [`dsl.md`](./dsl.md)). For code, prefer
`code(path, peek=[(a,b)])` to spotlight the lines that matter while keeping the
rest folded and present. Size the guide to the change — see
[`depth-and-scope.md`](./depth-and-scope.md). Write the prose **tight from the
start** (see step 7) — short, varied sentences; sparse em-dashes; plain vocabulary.

## 4. Draw and render the diagrams **(agent + script)**

Author Mermaid sources (apply real craft: ownership colors, subgraphs, styled
links, emojis for recognition). Render them to inline SVG at build time:

```sh
extras/render_diagrams.sh <diagrams_dir> <svg_out_dir>   # optional; needs npx
```

Rendering at build time validates the syntax and yields crisp, CDN-free SVG.
Diagrams are optional — most guides need none, and they pull in a Node toolchain
(see [`../extras/README.md`](../extras/README.md)).

## 5. Build the self-contained HTML **(script)**

`read-thru build content.py --source <root>` inlines the fonts, Pygments styles,
CSS, JS, and SVG into one file. The build also enforces a **completeness
contract**: set `ALL_FILES` and it errors if any is missing and reports total
code rows. For a full edition, code rows should equal the source's line count.

## 6. Adversarially verify every claim **(agent)**

This is the step that earns "vouch." Fan out one skeptic per section (a workflow
of parallel agents). Each agent:

- reads the section's prose and the source files it cites,
- tries to **falsify** every factual claim: line-number references, behavioral
  descriptions, and absolutes ("never", "exactly one", "only"),
- returns findings as `{severity, claim, problem, correction, evidence: file:line}`.

Apply the corrections, then **re-verify the edited sections** (fixes introduce
new claims). On the froot guide this caught ~16 issues — wrong line ranges,
over-claims, one genuinely unsupported statement — and a second pass caught one
more introduced by a fix. A clean codebase still produces findings; budget for
a fix-and-recheck loop.

## 7. Gate the prose quality **(script)**

Run the [unsloppable](https://github.com/mseeks/unsloppable) linter over the built HTML:

```sh
uv run python extras/lint_prose.py <built.html>   # optional; needs unsloppable
```

It flags prose that reads as AI-written (heavy em-dashes, uniform sentence
length, tricolons, marketing vocabulary) with per-signal advice. Revise any
section scoring ≥ 3.0: vary sentence rhythm, break comma-triples, cut adjectives.
Treat it as a style aid, not a gate — the goal is prose that reads like a person
wrote it, which also reads better.

## 8. Produce an essential cut **(agent)**

A full line-by-line edition is exhaustive; a reviewer often wants the quarter
that matters. Author a second, leaner `content_lite.py`: ~12 sections covering
the architecture, the load-bearing invariants, the loop logic, the seam, the
safety-critical code, the durable spine, secret handling, the best test, the
deploy, and a synthesis verdict. Show code as `peek` snippets. Link the two
editions so the reader can drop into the full one for context.

## 9. Completeness + visual QA **(script)**

- Confirm every intended file rendered (the build's completeness report).
- Spot-check that code rows equal line counts.
- Screenshot a few sections in **both themes** to catch layout breaks:
  ```sh
  node extras/screenshot.js <built.html> out light "0,#some-section-id"
  ```

---

### What makes the difference

Most "explain the codebase" output is a narrated file dump. The two steps that
turn it into something a reviewer can stand behind are **#6 (adversarial
fact-check against the source)** and the **synthesis section** that collects the
codebase's invariants and disciplines into checklists they can re-verify. Without
those, you have a nice read. With them, you have a document someone can vouch for.
