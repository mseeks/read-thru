"""The authored froot reading doc — narrative, techniques, code, diagrams.

Run with the build venv's python:  .doc_build/venv/bin/python .doc_build/content.py
"""
from __future__ import annotations

from read_thru import Section, callout, code, diagram, prose, raw, table

SECTIONS: list[Section] = []


def add(s: Section) -> Section:
    SECTIONS.append(s)
    return s


# Render froot files with a project-relative title/key; infra files keep their
# repo path. `path` is always resolved from the worktree root in gen.code().
def src(rel: str, **kw) -> str:
    kw.setdefault("title", rel)
    kw.setdefault("logical", rel)
    return code("projects/froot/" + rel, **kw)


def infra(rel: str, **kw) -> str:
    full = "infra/k8s/froot/" + rel
    kw.setdefault("title", full)
    kw.setdefault("logical", full)
    return code(full, **kw)


# ── Completeness manifest: every code file that must appear in the document ──
SRC_FILES = [
    "src/froot/__init__.py", "src/froot/result.py",
    "src/froot/domain/__init__.py", "src/froot/domain/base.py",
    "src/froot/domain/version.py", "src/froot/domain/ecosystem.py",
    "src/froot/domain/candidate.py", "src/froot/domain/changelog.py",
    "src/froot/domain/ci.py", "src/froot/domain/repo.py",
    "src/froot/domain/pull_request.py", "src/froot/domain/state.py",
    "src/froot/domain/events.py", "src/froot/domain/effects.py",
    "src/froot/domain/outcome.py", "src/froot/policy/__init__.py",
    "src/froot/policy/candidates.py", "src/froot/policy/naming.py",
    "src/froot/policy/compose.py", "src/froot/policy/state_machine.py",
    "src/froot/ports/__init__.py", "src/froot/ports/protocols.py",
    "src/froot/adapters/__init__.py", "src/froot/adapters/_proc.py",
    "src/froot/adapters/npm.py", "src/froot/adapters/github.py",
    "src/froot/adapters/changelog_http.py", "src/froot/adapters/model.py",
    "src/froot/adapters/model_judge.py", "src/froot/adapters/telemetry.py",
    "src/froot/config/__init__.py", "src/froot/config/settings.py",
    "src/froot/workflow/__init__.py", "src/froot/workflow/types.py",
    "src/froot/workflow/constants.py", "src/froot/workflow/runtime.py",
    "src/froot/workflow/scan_workflow.py", "src/froot/workflow/bump_workflow.py",
    "src/froot/workflow/activities.py", "src/froot/workflow/temporal_client.py",
    "src/froot/worker.py", "src/froot/scan_starter.py",
]
TEST_FILES = [
    "tests/conftest.py", "tests/support.py", "tests/test_result.py",
    "tests/test_version.py", "tests/test_candidate.py",
    "tests/test_domain_models.py", "tests/test_naming.py",
    "tests/test_candidates_policy.py", "tests/test_compose.py",
    "tests/test_state_machine.py", "tests/test_npm_adapter.py",
    "tests/test_github_adapter.py", "tests/test_changelog_adapter.py",
    "tests/test_model_judge.py", "tests/test_telemetry.py",
    "tests/test_settings.py", "tests/test_scan_workflow.py",
    "tests/test_bump_workflow.py", "tests/test_activities.py",
    "scripts/e2e_run.py",
]
BUILD_FILES = [
    "pyproject.toml", "Dockerfile", "Makefile", ".env.example",
    ".github/workflows/ci.yml", ".dockerignore", ".gitignore",
    ".python-version",
]
INFRA_FILES = [
    "infra/k8s/froot/install.sh", "infra/k8s/froot/secrets.example.env",
    "infra/k8s/froot/manifests/00-namespace.yaml",
    "infra/k8s/froot/manifests/10-worker.yaml",
    "infra/k8s/froot/manage/namespace-create.yaml",
    "infra/k8s/froot/manage/start-scan.yaml",
]
ALL_FILES = SRC_FILES + TEST_FILES + BUILD_FILES + INFRA_FILES


# ════════════════════════════════════════════════════════════════════════════
# PROLOGUE
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="hero", act="Prologue", num="·",
    title="froot, read top to bottom", technique="",
    blocks=[raw("""
<div class="hero">
  <div class="hero-kicker">A code-level reading</div>
  <h1>froot</h1>
  <p class="tagline">Durable maintenance loops, pointed at any repo.</p>
  <p class="lede prose">This document walks the <strong>entire</strong> froot
  codebase — every module, every line — and tells the story of how the parts fit.
  You can expand any code block to read the verbatim source, or follow the prose,
  diagrams, and tables to understand <em>why</em> each piece exists. Read it
  straight through and you should be able to vouch for the whole thing.</p>
  <div class="ownerkey">
    <span class="k k-chassis">🔵 chassis · deterministic &amp; durable</span>
    <span class="k k-model">🟣 model · thin judgment</span>
    <span class="k k-terrain">🟢 terrain · external truth</span>
    <span class="k k-steward">🟠 steward · the human</span>
  </div>
  <div class="statbar">
    <div class="stat"><div class="num">2,986</div><div class="lbl">lines of source</div></div>
    <div class="stat"><div class="num">42</div><div class="lbl">modules</div></div>
    <div class="stat"><div class="num">4</div><div class="lbl">ports</div></div>
    <div class="stat"><div class="num">1</div><div class="lbl">model call</div></div>
    <div class="stat"><div class="num">0</div><div class="lbl">databases</div></div>
  </div>
</div>
"""),
        prose("""
### What froot is, in one breath

froot is a **Temporal worker** that runs autonomous code-maintenance *loops* and
points them at GitHub repositories. A loop watches a repo for one class of decay,
proposes a bounded fix as a pull request, lets the repo's **own CI** verify it,
and leaves the outcome behind as a signal a human (and the next run) can read.
**A human approves every merge.**

The first — and so far only — loop keeps npm dependencies patched. But froot is
deliberately *not* that loop. It is the **chassis** the loop runs on: one durable
substrate, many specialized loops, any number of repos. Almost everything in this
codebase is chassis; the loop-specific parts are tiny by design.
"""),
        callout("principle", """
**The thesis.** froot is [Many Hands Engineering](https://github.com/mseeks/many-hands-engineering)
put into practice. MHE defines a *loop* as six ingredients —
**signal → bounded action → verification → reversibility → signal-update → authority surface**.
The maintenance scripts froot grew from already had four of them. The two they
lacked — *a decaying trace left behind* and *a rule for when autonomy expands* —
are exactly the two that need **state that survives across runs**. That is the
whole reason froot is built on Temporal: durability is not a reliability upgrade
here, it is *what closes the loop*.
"""),
        diagram("loop",
                 "The dependency-patch loop, closing through external truth. "
                 "Nodes are colored by who owns each step — the legend above. "
                 "The dashed return edge is the loop closing: each outcome decays "
                 "into the next tick's signal.", klass="wide"),
        prose("""
Hold that picture in mind — the rest of this document is, in effect, a guided
tour of how each node is built and how they are wired together. We will start at
the still center (the pure domain) and work outward to the durable edge (Temporal
and the cluster), because that is the direction the dependencies point.
"""),
    ],
))

add(Section(
    id="reading-guide", act="Prologue", num="·",
    title="How to read this document", technique="Legend",
    blocks=[
        prose("""
A few conventions make the rest go down easier.

#### Collapsible code, like a PR review

Every source file appears in full. Long or boilerplate stretches are **folded**
behind a `⋯ N lines hidden` stub — click to expand, exactly like GitHub hides
unchanged regions in a diff. Each code block also has an **expand all** button in
its header, and every line number is a deep link. Nothing is hidden from you;
folding only keeps the eye on what the prose is talking about right now.
"""),
        callout("note", """
**Spotlighting.** When a few lines carry the weight of a section, they get an
amber **spotlight** bar in the gutter — that is where to look first. The
surrounding code stays present for when you want to dig.
"""),
        callout("note", """
**What's shown, and what isn't.** Every one of froot's **76 code files** — all
2,986 source lines, the full `tests/` tree, the build files, and the k8s
manifests — appears here verbatim (5,052 lines in total, each a clickable row).
Four things are *referenced but not reproduced line-by-line*: the prose docs
(`README.md`, `SPEC.md`) and the `LICENSE`, which are woven into the narrative
instead; the generated `uv.lock` (116k lines of resolved hashes); and the two
empty marker files (`py.typed`, `tests/__init__.py`), which have no lines to show.
"""),
        prose("""
#### The four owners, by color

froot's design turns on *who owns each decision*. Throughout, you'll see the same
four-color scheme from the diagram above:
"""),
        table(
            ["Owner", "Means", "In the code"],
            [
                ["🔵 **chassis**", "deterministic, durable, replay-safe",
                 "`domain`, `policy`, the Temporal workflows, the scan timer"],
                ["🟣 **model**", "the one place judgment is irreducible",
                 "`adapters/model_judge.py` — *“is this changelog a clean patch?”*"],
                ["🟢 **terrain**", "external systems froot reads as truth",
                 "GitHub (CI is the oracle), the npm registry, ClickStack"],
                ["🟠 **steward**", "the human in the loop",
                 "approves every merge; froot has write authority, not merge authority"],
            ],
            caption="The ownership palette, used in every diagram and callout."),
        prose("""
#### Focus techniques

To keep comprehension high without monotony, each section announces its **focus
technique** in the badge at its top-right — a spotlight, an execution trace, a
truth-table, a counterfactual (“what breaks if we delete this line?”), a sequence
diagram, and so on. The technique is chosen to fit what that particular file
*teaches*. Watch the badges; they tell you how to read each section.
"""),
        callout("insight", """
**One running example.** A single dependency bump — `left-pad` from `1.4.2` to
`1.4.3` — recurs throughout (it is the codebase's own favorite test fixture).
Watch it turn from a string, to a validated `Version`, to a `PatchCandidate`, to
a branch name, to a pull request, to a recorded outcome. By the end you'll have
seen the whole pipeline act on one concrete value.
"""),
    ],
))

add(Section(
    id="architecture", act="Prologue", num="·",
    title="The shape of the whole thing", technique="Map + table",
    files=["src/froot/__init__.py"],
    blocks=[
        prose("""
froot is a **functional core wrapped in an imperative shell** — classic
hexagonal / ports-and-adapters, with a Temporal spine as the outermost driver.
The package is layered and *strictly inward-depending*: an arrow may only point
toward the center. The pure core at the middle knows nothing of Temporal, npm,
GitHub, or HTTP; the impure shell at the edge knows all of them but contains no
business rules.
"""),
        diagram("architecture",
                 "Dependencies point inward. The pure core (domain + policy) has "
                 "no I/O and no framework; the shell implements the ports and "
                 "interprets the core's effects. The seam is a handful of typed "
                 "Protocols."),
        prose("""
The package's own `__init__` docstring is the canonical statement of this
layering — worth reading once, because it is the map for everything that follows:
"""),
        src("src/froot/__init__.py", spotlight=[(8, 18)]),
        prose("""
#### Every file, at a glance

Here is the entire source tree with each module's job and size. The acts of this
document follow these layers from the inside out.
"""),
        table(
            ["Layer", "Module", "Lines", "Its one job"],
            [
                ["🧊 domain", "`base` · `version` · `candidate` · `changelog` · `ci` · `repo` · `pull_request` · `state` · `events` · `effects` · `outcome` · `ecosystem`", "727", "frozen, closed value objects that make illegal states unrepresentable"],
                ["— support", "`result.py`", "62", "an `Ok`/`Err` Result type for the parsing boundary"],
                ["🧮 policy", "`candidates` · `naming` · `compose` · `state_machine`", "363", "pure decisions over the domain — selection, idempotency keys, PR text, the loop's transitions"],
                ["📜 ports", "`protocols.py`", "114", "four typed `Protocol`s — the seam to the impure world"],
                ["🔌 adapters", "`_proc` · `npm` · `github` · `changelog_http` · `model` · `model_judge` · `telemetry`", "845", "concrete integrations: subprocess, npm, git+GitHub REST, HTTP, the model, OTEL"],
                ["⚙️ workflow", "`types` · `constants` · `runtime` · `scan_workflow` · `bump_workflow` · `activities` · `temporal_client`", "521", "the durable Temporal spine: two workflows, six activities, the wiring"],
                ["🚀 entry", "`worker.py` · `scan_starter.py`", "159", "the runnable worker, and the one-shot that kicks the loops"],
                ["⚙️ config", "`settings.py`", "125", "all deployment config as frozen pydantic-settings"],
            ],
            caption="The froot source tree by layer. Each count is the sum of the "
                    "named modules and excludes each package's `__init__`; the "
                    "named modules total 2,916 lines, and the seven `__init__` "
                    "files add the remaining 70 to reach the 2,986 in the masthead."),
        callout("why", """
**Why this shape?** Three payoffs recur. **(1) Testability** — the core is
exercised with in-memory fakes; no test in the suite needs npm, git, GitHub, or a
real model. **(2) Replay-safety** — Temporal workflows must be deterministic, and
a pure core with all I/O pushed into activities is deterministic by construction.
**(3) The chassis/loop seam** — because the durable machinery never imports a
concrete adapter directly, a *new* loop is a new signal + lockfile command +
prompt, not a fork of the engine.
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT I — THE PURE CORE (domain)
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act1-intro", act="Act I · The pure core", num="1.0",
    title="Make illegal states unrepresentable",
    technique="Orientation",
    blocks=[
        prose("""
The domain layer is froot's still center: a dozen tiny modules of *frozen,
closed* value objects. The governing idea — stated in the layer's own docstring —
is that **the illegal states the loop must never reach cannot be constructed at
all**. A “patch bump” that secretly changes the minor version, a transaction in
two lifecycle states at once, an outcome recorded before CI resolved: none of
these are bugs to guard against at runtime, because the *types* refuse to
represent them.

That is a strong claim. The next dozen sections are the evidence. We begin with
the two-line base class that makes it possible.
"""),
    ],
))

add(Section(
    id="domain-base", act="Act I · The pure core", num="1.1",
    title="`Frozen` — the two-line substrate",
    technique="Spotlight",
    files=["src/froot/domain/base.py", "src/froot/domain/__init__.py"],
    blocks=[
        prose("""
Almost every domain type inherits from one class. It does two things, and both
are load-bearing for the whole “unrepresentable” thesis.
"""),
        src("src/froot/domain/base.py", spotlight=[(17, 17)]),
        prose("""
`frozen=True` makes instances **immutable** — a new state is a new value, never a
mutation of an old one. That is what lets the state machine hand the same value
around without anyone defensively copying it, and what makes domain values
hashable so they can be set/dict keys. `extra="forbid"` makes the model
**closed** — an unknown field (a typo, a stale serialized payload from an older
version, an attacker-shaped blob) is *rejected*, not silently absorbed.
"""),
        callout("principle", """
**Immutable + closed = the substrate.** Every guarantee later in this act —
construction-time invariants, discriminated unions, terminal-status subsets —
rests on these two flags. The domain package's docstring puts it plainly: *“a
'patch bump' that changes the minor version, a transaction in two lifecycle
states at once, cannot be constructed.”*
"""),
        src("src/froot/domain/__init__.py"),
    ],
))

add(Section(
    id="result", act="Act I · The pure core", num="1.2",
    title="`Result` — honesty at the boundary",
    technique="Q&A",
    files=["src/froot/result.py"],
    blocks=[
        prose("""
Before the first value object, one small support type. froot is a Pydantic
codebase — models validate on construction and *raise* on bad input. So why does
it also carry a hand-rolled `Ok`/`Err` Result type?
"""),
        callout("note", """
**Q: When is a parse failure not exceptional?**
**A: At the untrusted boundary.** When *froot's own code* constructs a value with
data that should already be valid, a raise is correct — it's a bug. But when
external text (`npm` output, GitHub JSON, a `FROOT_REPOS` env string) is being
*parsed into* a domain value, failure is an ordinary, expected outcome. There,
froot returns a `Result` and forces the caller to handle both arms.
"""),
        src("src/froot/result.py", fold=[(1, 19)], spotlight=[(40, 40), (43, 63)]),
        prose("""
Two frozen, slotted dataclasses — `Ok[T]` and `Err[E]` — and a PEP 695 type alias
`Result[T, E] = Ok[T] | Err[E]`. Callers pattern-match, and because both classes
are `@final`, mypy proves the `match` is exhaustive: forget the `Err` arm and the
type checker complains. `unwrap()` is the deliberate escape hatch for call sites
(tests, already-validated inputs) where an `Err` genuinely *is* a programming
error.
"""),
        callout("insight", """
**This is the only functional-error-handling in the codebase.** Everywhere else,
invariants are expressed through types and validators. `Result` exists for
exactly one job: the parse boundary. You'll see it returned by
`Version.parse`, `RepoRef.parse`, and the npm/registry parsers — always where
*outside* text becomes *inside* value.
"""),
    ],
))

add(Section(
    id="version", act="Act I · The pure core", num="1.3",
    title="`Version` — the value the whole loop turns on",
    technique="Annotated walkthrough",
    files=["src/froot/domain/version.py"],
    blocks=[
        prose("""
The loop's deterministic signal is *“a higher patch of a dependency exists.”*
Everything downstream depends on a precise definition of **patch**, and that
definition lives in one method on one value object. `Version` is worth reading
closely — it is small, but it is the hinge.
"""),
        src("src/froot/domain/version.py",
             fold=[(1, 19)],
             spotlight=[(92, 112)]),
        prose("""
#### The parser returns a `Result`, not a raise

`Version.parse` (lines 53–75) is a boundary parser, so it hands back
`Ok(Version)` / `Err(message)`. The regex tolerates a leading `v`, captures
`major.minor.patch`, allows an optional `-prerelease`, and *parses away* `+build`
metadata without comparing it (SemVer says build metadata has no precedence).
"""),
        prose("""
#### `is_patch_bump_of` — the precise relation

The spotlighted method is the definition of the signal. A version is a clean
patch bump of another only when **both are stable**, the **major and minor
match**, and the **patch strictly increases**. Read the conjunction on lines
106–112: each clause forbids a specific way a “bump” could smuggle in risk.
"""),
        table(
            ["`current` → `target`", "patch bump?", "why"],
            [
                ["`1.4.2` → `1.4.3`", "✅ yes", "same major.minor, patch up, both stable"],
                ["`1.4.2` → `1.5.0`", "❌ no", "minor changed"],
                ["`1.9.9` → `2.0.0`", "❌ no", "major changed"],
                ["`1.4.2` → `1.4.1`", "❌ no", "patch went backward"],
                ["`1.4.2` → `1.4.2`", "❌ no", "no change (strictly greater required)"],
                ["`1.4.2` → `1.4.3-rc.1`", "❌ no", "target is a prerelease (instability)"],
                ["`1.4.2-rc.1` → `1.4.3`", "❌ no", "current end is a prerelease"],
            ],
            caption="Every case `is_patch_bump_of` must get right — drawn straight "
                    "from test_version.py. A prerelease on either end is never clean."),
        callout("gotcha", """
**A deliberate non-correctness.** `_sort_key` (lines 83–90) compares prerelease
tags *lexically*, not by SemVer §11's numeric-identifier rules — so `"rc.2"`
would sort *after* `"rc.10"`, which §11 forbids. The comment owns this: it's fine
because **the patch loop only ever compares stable versions** (`is_patch_bump_of`
requires both ends stable), so the prerelease-vs-prerelease path is unreachable in
practice. Honest scoping beats gold-plating an unused code path.
"""),
        callout("insight", """
**`@total_ordering` earns its keep.** Defining just `__eq__` (free, from
`Frozen`) and `__lt__` gives the type the full suite of comparisons, which is what
lets the selection policy — specifically `_best_patch_target`, called by
`select_patch_candidates` — call `max(...)` over the candidate `Version`s to pick
the *highest* available patch. The value object carries its own ordering so the
policy can stay a one-liner.
"""),
    ],
))

add(Section(
    id="candidate", act="Act I · The pure core", num="1.4",
    title="`PatchCandidate` — an invariant you cannot dodge",
    technique="Spot-the-invariant + counterfactual",
    files=["src/froot/domain/candidate.py"],
    blocks=[
        prose("""
`Version` *defines* a patch bump; `PatchCandidate` *enforces* it. This is the
loop's bounded unit of work, and it carries a single load-bearing invariant
checked at construction.
"""),
        src("src/froot/domain/candidate.py",
             fold=[(1, 19)], spotlight=[(38, 46)]),
        prose("""
The `@model_validator(mode="after")` runs after Pydantic builds the fields and
re-checks the one rule that matters: `target.is_patch_bump_of(current)`. If it
fails, construction raises. There is no way to obtain a `PatchCandidate` whose
target is a minor bump, a downgrade, or a prerelease.
"""),
        callout("counter", """
**Delete lines 38–46 and watch the blast radius.** Without the validator,
`PatchCandidate("x", NPM, 1.4.2, 2.0.0)` becomes constructible — and now *every*
downstream consumer must re-validate, or risk opening a major-version “patch” PR.
The `select_patch_candidates` policy, the PR title template, the branch name, the
recorded outcome — all of them currently *trust* the candidate because the type
guarantees it. The invariant isn't convenience; it's what lets the other 2,900
lines stop worrying.
"""),
        prose("""
#### Two types, one boundary

Note the *second* class, `AvailableUpgrade` (lines 53–73). It deliberately is
**not** a candidate yet: it holds an installed version plus a tuple of published
versions in any order. Choosing *which* available version is the right patch
target is a business decision — and froot keeps that decision in the pure
`policy` layer, not in the adapter that gathered the raw versions. The adapter
reports facts; the policy decides.
"""),
        callout("principle", """
**Parse, don't validate — at every layer.** `AvailableUpgrade` → (policy) →
`PatchCandidate` is the same move as `str` → (parse) → `Version`: raw shapes are
refined into types that *encode* what's been proven about them. Once you hold the
refined type, the proof travels with the value.
"""),
    ],
))

add(Section(
    id="ecosystem", act="Act I · The pure core", num="1.5",
    title="`Ecosystem` — the seam that fails loudly",
    technique="Counterfactual",
    files=["src/froot/domain/ecosystem.py"],
    blocks=[
        prose("""
froot ships one ecosystem today — npm — but is built to grow to `uv` (Python)
next. The way it stays honest about that is a small enum plus an exhaustiveness
trick.
"""),
        src("src/froot/domain/ecosystem.py", fold=[(1, 14)],
             spotlight=[(27, 27), (35, 35)]),
        prose("""
`manifest_filename` and `lockfile_filename` `match` on the ecosystem and end with
`assert_never(ecosystem)`. Today the enum has a single member, so the `match` is
trivially total.
"""),
        callout("counter", """
**Add `uv` and the type checker becomes your TODO list.** The moment a second
member joins `Ecosystem`, every `match` that doesn't handle it stops being
exhaustive, and `assert_never` turns that into a *compile-time* `mypy` error at
exactly the spots that need a new branch — manifest name, lockfile name, and the
matching adapter. The SPEC calls this out as the design intent: *“the `match`
statements will fail to type-check until it is handled, which is the point.”*
You cannot forget to finish the port.
"""),
    ],
))

add(Section(
    id="changelog", act="Act I · The pure core", num="1.6",
    title="`Changelog` & the verdict — the loop's one judgment",
    technique="Union diagram",
    files=["src/froot/domain/changelog.py"],
    blocks=[
        prose("""
froot's design principle #2 is **spine-heavy, model-thin**: deterministic code
owns *when* and *whether*; the model owns only *what needs judgment*. For the
dependency-patch loop there is exactly one such question — *is this patch's
changelog clean, or does it hint at hidden behavioral change?* — and its answer
is this typed verdict.
"""),
        diagram("verdict-union",
                 "ChangelogVerdict is a discriminated union over `kind`. "
                 "`UnknownVerdict` is reachable without ever calling the model — "
                 "the spine doesn't pay to assess an empty changelog.",
                 klass="wide"),
        src("src/froot/domain/changelog.py", fold=[(1, 19)],
             spotlight=[(64, 68)]),
        prose("""
Three verdicts — `Clean`, `Risky` (which carries a tuple of concerns), and
`Unknown` — are tagged by a `Literal` `kind` and unioned with a Pydantic
`discriminator="kind"`. That discriminator is what lets the verdict serialize
across the Temporal boundary and deserialize back into the *right* subtype.
"""),
        callout("insight", """
**Framing, not a gate.** Read the module docstring (lines 1–9): the verdict
**never blocks** a bump. Every patch candidate is proposed regardless; the verdict
only shapes the PR's description and labels so the reviewing human triages faster.
A “risky” reading is information for the steward, not a veto by the model. This is
the whole spine-heavy/model-thin philosophy compressed into one type.
"""),
    ],
))

add(Section(
    id="ci", act="Act I · The pure core", num="1.7",
    title="`CIStatus` — two unions, and a subset that can't lie",
    technique="State lattice",
    files=["src/froot/domain/ci.py"],
    blocks=[
        prose("""
CI is froot's verification, and froot **never re-runs a repo's tests** (principle
#3: *CI is the oracle*). It opens a PR and reads the repo's existing checks. The
subtlety is making sure a *still-running* check can never be mistaken for a
verdict — and the type system is what enforces it.
"""),
        diagram("ci-lattice",
                 "Five readings, but only four are terminal. `TerminalCIStatus` is "
                 "a strict subset of `CIStatus` — and the recorded outcome is typed "
                 "to the subset, so a pending status is not even assignable.",
                 klass="wide"),
        src("src/froot/domain/ci.py", fold=[(1, 19)],
             spotlight=[(52, 68)]),
        prose("""
There are two unions here, and the relationship between them is the point.
`CIStatus` is all five readings. `TerminalCIStatus` is the four that are *final* —
everything except `CIPending`. Crucially, `CIAbsent` (the repo has no checks) and
`CITimedOut` (froot stopped waiting) are kept **distinct** from a real
`CIPassed`/`CIFailed`, so the recorded outcome never conflates “green” with
“couldn't tell.”
"""),
        table(
            ["Reading", "Terminal?", "Meaning"],
            [
                ["`CIPending`", "❌ no", "checks still running — the spine keeps waiting"],
                ["`CIPassed`", "✅ yes", "all required checks succeeded — ready for a human merge"],
                ["`CIFailed`", "✅ yes", "at least one check failed (carries the failing names)"],
                ["`CIAbsent`", "✅ yes", "the repo configured no checks — nothing to verify"],
                ["`CITimedOut`", "✅ yes", "froot's CI-wait deadline elapsed first"],
            ],
            caption="Only `CIPending` is non-terminal — which is exactly what "
                    "`is_terminal` narrows away."),
        callout("insight", """
**`TypeIs` is the magic word.** `is_terminal` (lines 66–68) returns
`TypeIs[TerminalCIStatus]`, not just `bool`. So when the bump workflow writes
`if is_terminal(status): return status`, mypy *narrows* `status` to the terminal
subset inside that branch — and because `LoopOutcome.ci` is typed
`TerminalCIStatus`, the compiler guarantees a pending reading can never be
recorded as an outcome. The “can't record a half-finished CI” rule is enforced by
the type checker, not a runtime `assert`.
"""),
    ],
))


add(Section(
    id="repo-pr", act="Act I · The pure core", num="1.8",
    title="Identities & the artifact — `RepoRef`, `TargetRepo`, the PR",
    technique="Annotated walkthrough",
    files=["src/froot/domain/repo.py", "src/froot/domain/pull_request.py"],
    blocks=[
        prose("""
Two small files name the *what* and the *where* of a loop: the repository it
points at, and the pull request it produces. Both lean on anchored regular
expressions to keep malformed identities out of the types entirely.
"""),
        prose("""
#### The target repo
"""),
        src("src/froot/domain/repo.py", fold=[(1, 16)],
             spotlight=[(21, 21)]),
        callout("security", """
**The anchor is load-bearing.** `_SEGMENT = r"\\A[A-Za-z0-9._-]+\\z"` matches an
*entire* owner/name segment — and the comment explains the unusual `\\A..\\z`
(rather than `^..$`): `$` in a regex would also match just before a trailing
newline, which would let `owner\\n` slip through. Since these segments are
interpolated into a `git clone` URL and GitHub API paths, a smuggled slash,
space, or newline is a real injection vector. The pattern is enforced on the
*field*, so it holds whether the value comes from `parse()` or a direct
constructor call — illegal repo identities never enter the type.
"""),
        prose("""
`RepoRef.parse` handles the `owner/name` boundary (returning a `Result`), while
`TargetRepo` adds the facts the chassis needs: the ecosystem (defaulting to npm),
the `default_branch` PRs target, and a `manifest_dir` for monorepos.

#### The pull request, in three shapes
"""),
        src("src/froot/domain/pull_request.py", fold=[(1, 14)],
             spotlight=[(16, 28)]),
        prose("""
The PR is modeled as three distinct types for three moments in its life.
`BranchName` validates a ref-safe string — and, as its docstring notes, it
doubles as froot's **idempotency key**: a deterministic branch name means
*“have I already proposed this exact bump?”* is answerable by name alone.
`PullRequestDraft` is the *content* froot wants to open (title + body, composed by
a pure template). `PullRequestRef` is the *handle* to an opened PR, carrying the
`head_sha` — the commit CI runs against and the thing froot polls a status for.
"""),
        callout("insight", """
**Field constraints as micro-specs.** `head_sha` requires `min_length=7`,
`number` requires `ge=1`, `url` and `title` require `min_length=1`. None of these
are dramatic, but together they mean a `PullRequestRef` you're holding is never
half-formed — there's no “PR #0 with an empty URL” to defend against three calls
later. The validations live *at the boundary of the type*, so every consumer
inherits them for free.
"""),
    ],
))

add(Section(
    id="lifecycle-algebra", act="Act I · The pure core", num="1.9",
    title="The lifecycle algebra — state · event · effect · outcome",
    technique="Parallel-unions table + diagram",
    files=["src/froot/domain/state.py", "src/froot/domain/events.py",
           "src/froot/domain/effects.py", "src/froot/domain/outcome.py"],
    blocks=[
        prose("""
Here is the conceptual heart of the domain — four files that, together, describe
*a single bump's journey* as an algebra of values. They set up the state machine
we'll meet in Act II. The trick to reading them: they are **three parallel
discriminated unions**, kept in lock-step.
"""),
        table(
            ["🧊 `BumpState` (where we are)", "📨 `LoopEvent` (what just happened)",
             "⚡ `Effect` (what to do next)"],
            [
                ["`Discovered` — a fresh candidate", "`ChangelogJudged` — model returned a verdict", "`JudgeChangelog` — fetch + judge"],
                ["`Judged` — verdict in hand", "`PullRequestReady` — PR is open", "`OpenPullRequest` — regen + open PR"],
                ["`AwaitingCi` — PR open, waiting", "`CiResolved` — CI reached a status", "`AwaitCi` — durably poll CI"],
                ["`Recorded` ∎ — terminal", "`OutcomeRecorded` — nothing left to do", "`RecordOutcome` — label + log"],
            ],
            caption="State, event, and effect advance together. Each row is one "
                    "step of the loop; the state machine in Act II is the function "
                    "that walks down this table."),
        diagram("algebra",
                 "The same alignment, drawn. A state emits an effect; the spine "
                 "runs the effect and produces an event; the event advances the "
                 "state. Pure values throughout — no I/O hides in any of these "
                 "types.", klass="wide"),
        prose("""
#### State carries exactly what's valid — no more

Read `state.py` and notice what each state *holds*. `Discovered` has only a
candidate. `Judged` adds a verdict. `AwaitingCi` *necessarily* has a verdict
**and** an open PR. `Recorded` has only an outcome. A state that holds a PR but
no verdict, or an outcome before CI resolved, is simply not constructible.
"""),
        src("src/froot/domain/state.py", fold=[(1, 21)]),
        prose("""
#### Events are *decided* inputs

`events.py` is deliberately thin. Each event carries an **already-decided**
result — the model already judged, the PR was already opened, CI already
resolved. By the time an event reaches the state machine, all interpretation has
happened out in the spine; the machine only decides *where the loop goes next*,
never *what the judgment was*.
"""),
        src("src/froot/domain/events.py", fold=[(1, 20)]),
        prose("""
#### Effects are *data*, not actions

This is the cornerstone of froot's testability. The state machine performs **no
I/O**. On each transition it emits an `Effect` — a plain frozen value describing
*what the spine should do*. The Temporal spine interprets each effect into an
activity (or, for `AwaitCi`, a durable poll-and-sleep) and feeds the resulting
event back in.
"""),
        src("src/froot/domain/effects.py", fold=[(1, 22)]),
        callout("principle", """
**Effects-as-data is why the whole loop is unit-testable.** Because a transition
returns *values* (`next state`, `effects`), you can assert the entire decision
flow — “a clean verdict in `Discovered` yields `Judged` plus an `OpenPullRequest`
effect” — without npm, GitHub, Temporal, or a model anywhere in the test. The I/O
is named but not performed. Act II's `state_machine.py` is 171 pure lines for
exactly this reason, and its tests run in milliseconds.
"""),
        prose("""
#### The outcome — the signal-update that closes the loop

When a bump reaches a terminal CI status, the loop records a `LoopOutcome` and
stops. Note its `ci` field is typed `TerminalCIStatus` — the subset from §1.7 —
so a still-pending status is *not assignable here*. The compiler enforces that an
outcome is only ever recorded against a resolved CI.
"""),
        src("src/froot/domain/outcome.py", fold=[(1, 18)],
             spotlight=[(31, 34)]),
        callout("principle", """
**Derive, never store.** The outcome's docstring states froot's principle #4:
froot keeps *no database*. The `LoopOutcome` is the value carried to two external
truths — GitHub (the PR, left open for the human, labeled by this outcome) and
ClickStack (the run telemetry). The record *is* those external facts, not a row
froot owns. Two independent external ledgers also give triangulation against
gaming for free.
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT II — PURE POLICY
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act2-intro", act="Act II · Pure policy", num="2.0",
    title="Decisions, still without a single side effect",
    technique="Orientation",
    files=["src/froot/policy/__init__.py"],
    blocks=[
        prose("""
The domain gave us *nouns*; policy gives us *verbs* — but still pure ones. Four
modules decide things over the domain: which version to target, what to name a
branch, what a PR should say, and how the loop transitions. Every one is
unit-testable with no Temporal, no npm, no GitHub, no model.
"""),
        src("src/froot/policy/__init__.py"),
    ],
))

add(Section(
    id="candidates", act="Act II · Pure policy", num="2.1",
    title="`select_patch_candidates` — choosing the target",
    technique="Follow the data",
    files=["src/froot/policy/candidates.py"],
    blocks=[
        prose("""
Recall the adapter only gathers raw facts (`AvailableUpgrade`). The *decision* —
which available version is the right patch target — lives here, where it's
testable. Follow one upgrade through it.
"""),
        src("src/froot/policy/candidates.py", fold=[(1, 21)],
             spotlight=[(23, 30)]),
        prose("""
`_best_patch_target` filters the available versions to those that are clean patch
bumps of the installed one (reusing `Version.is_patch_bump_of` from §1.3), then
takes the `max` — the **highest** stable patch. `select_patch_candidates` maps
each upgrade through it, drops the ones with no patch available (the walrus
`:=` keeps the comprehension tight), builds a validated `PatchCandidate`, and
returns them **sorted by package** for a stable, reviewable order.
"""),
        callout("trace", """
**Trace it.** Given `left-pad` installed at `1.4.2` with available
`[1.4.1, 1.4.3, 1.4.7, 1.5.0]`: the filter keeps `{1.4.3, 1.4.7}` (1.4.1 is
backward, 1.5.0 is a minor), `max` picks **1.4.7**, and the result is one
`PatchCandidate(left-pad, 1.4.2 → 1.4.7)`. A package whose only upgrades cross
the minor/major line yields *nothing* and is silently dropped. This is exactly
what `test_candidates_policy.py` asserts.
"""),
        callout("insight", """
**One per dependency, highest patch.** froot deliberately doesn't open a PR per
intermediate patch — it jumps straight to the newest patch in the series. Fewer
PRs, each still a clean patch, each still reversible. The sorting makes a scan's
output deterministic, which matters because the *branch names* derived from these
candidates are the loop's dedup keys (next section).
"""),
    ],
))

add(Section(
    id="naming", act="Act II · Pure policy", num="2.2",
    title="`naming` — deterministic names are idempotency",
    technique="Inputs → outputs table",
    files=["src/froot/policy/naming.py"],
    blocks=[
        prose("""
This is the smallest module with the largest leverage on froot's correctness.
Each name here is a **pure function of a stable identity**: the head branch is a
function of `(package + target)` (it never sees the repo — `branch_name` takes
only the candidate), while the per-bump workflow id folds in the repo too,
`(repo + package + target)`. That determinism is what makes the entire loop
idempotent.
"""),
        src("src/froot/policy/naming.py", fold=[(1, 19)],
             spotlight=[(31, 35)]),
        table(
            ["Function", "Input", "Output", "Used as"],
            [
                ["`branch_name`", "`left-pad → 1.4.3`", "`froot/dependency-patch/left-pad-1.4.3`", "the PR dedup key"],
                ["`branch_name`", "`@scope/pkg → 1.4.3`", "`froot/dependency-patch/scope-pkg-1.4.3`", "(scoped name sanitized)"],
                ["`bump_workflow_id`", "`acme/widgets`, `left-pad → 1.4.3`", "`froot-bump-acme-widgets-left-pad-1.4.3`", "the dispatch dedup key"],
                ["`scan_workflow_id`", "`acme/widgets`", "`froot-scan-acme-widgets`", "the per-repo loop singleton"],
            ],
            caption="Same inputs always yield the same names — the whole point. "
                    "`_slug` lowercases and collapses unsafe runs to single hyphens."),
        callout("insight", """
**Two dedup layers from one idea.** The deterministic *workflow id* means a
second dispatch of the same bump is rejected by Temporal before any work starts
(we'll see `REJECT_DUPLICATE` in §6.6). The deterministic *branch name* means even
if a workflow did run twice, opening the PR finds the existing one and
short-circuits (§4.3). Re-scanning a repo daily therefore never produces a
duplicate PR or a duplicate in-flight workflow — idempotency by construction, at
two independent layers, both derived from this 55-line file.
"""),
    ],
))

add(Section(
    id="compose", act="Act II · Pure policy", num="2.3",
    title="`compose` — the PR writes itself",
    technique="Rendered-output preview",
    files=["src/froot/policy/compose.py"],
    blocks=[
        prose("""
The model already did its one job — the verdict. So the PR's title and body cost
**no** model round-trip: they're a deterministic template over the candidate and
the verdict. Here's the function, then the actual text it produces.
"""),
        src("src/froot/policy/compose.py", fold=[(1, 24)],
             spotlight=[(48, 80)]),
        prose("""
For our running example with a clean verdict, `pull_request_draft` renders exactly
this:
"""),
        raw("""
<figure class="tablewrap"><table><thead><tr><th>Field</th><th>Rendered value</th></tr></thead><tbody>
<tr><td><code>title</code></td><td><code>deps: bump left-pad to 1.4.3</code></td></tr>
<tr><td><code>base</code></td><td><code>main</code></td></tr>
<tr><td><code>branch</code></td><td><code>froot/dependency-patch/left-pad-1.4.3</code></td></tr>
<tr><td><code>body</code></td><td><div style="font-family:var(--mono);font-size:12.5px;white-space:pre-wrap;line-height:1.5">Bumps `left-pad` from 1.4.2 to 1.4.3 (package.json + lockfile).

Changelog reads clean. Only fixes a whitespace edge case.

---
Opened by froot. froot does not merge; a human approves.</div></td></tr>
</tbody></table><figcaption>The deterministic PR draft for the running example
(clean verdict). The verdict summary is the only model-derived text — and it was
computed once, upstream.</figcaption></figure>
"""),
        prose("""
`_verdict_summary` (lines 35–45) `match`es on the verdict subtype — clean reads
“Changelog reads clean,” risky lists each concern as a bullet, unknown says
“Changelog unavailable” — and ends in `assert_never`, so adding a fourth verdict
kind would fail to type-check here until handled.
"""),
        callout("why", """
**Why only two fixed labels?** `PR_LABELS = ("froot", "dependency-patch")` — and
that's *all*, regardless of outcome. The docstring explains the restraint: how a
proposal *fared* (the changelog verdict, the CI result) is recorded durably in the
workflow history and the structured outcome log, **not** layered onto the PR as
labels that pile up across re-runs. The labels mark *what* froot did, not *how it
went*. Keeping them fixed keeps re-runs idempotent at the label layer too.
"""),
    ],
))

add(Section(
    id="state-machine", act="Act II · Pure policy", num="2.4",
    title="`state_machine` — the loop, as a pure function",
    technique="State diagram + transition table + execution trace",
    files=["src/froot/policy/state_machine.py"],
    blocks=[
        prose("""
This is the centerpiece of the pure core — the file that decides the loop's every
move, and the one the Temporal spine merely *drives*. It earns three lenses
because it is that important. `start` and `advance` are pure: given a state and a
decided event, they return a `Transition` — the next state plus the effects the
spine should run. No I/O, no clock; a transition replays deterministically and is
fully testable.
"""),
        diagram("state-machine",
                 "The bump lifecycle. Solid edges advance and emit an effect; the "
                 "self-loop on AwaitingCi is a still-pending CI being REJECTED so "
                 "the spine keeps waiting; the terminal acknowledgement is a "
                 "no-op IGNORED.", klass="wide"),
        src("src/froot/policy/state_machine.py", fold=[(1, 49)],
             spotlight=[(94, 113)]),
        prose("""
#### Lens 1 — the dispatch is total

`advance` (lines 94–113) `match`es on the *state*, delegating to a per-state
helper, and ends in `assert_never(state)`. The type checker therefore proves
**every state is handled**. Each helper, in turn, `match`es on the event and
returns either an `_advanced(...)` transition or a `_rejected(...)` one.
"""),
        table(
            ["State", "Expected event", "→ Next state", "Emits effect"],
            [
                ["`Discovered`", "`ChangelogJudged`", "`Judged`", "`OpenPullRequest`"],
                ["`Judged`", "`PullRequestReady`", "`AwaitingCi`", "`AwaitCi`"],
                ["`AwaitingCi`", "`CiResolved` (terminal)", "`Recorded`", "`RecordOutcome`"],
                ["`AwaitingCi`", "`CiResolved` (pending)", "*(unchanged)*", "— **REJECTED**"],
                ["`Recorded`", "`OutcomeRecorded`", "*(unchanged)*", "— **IGNORED** (loop ends)"],
                ["*any*", "*any other event*", "*(unchanged)*", "— **REJECTED**"],
            ],
            caption="The complete transition table. Every legal path advances and "
                    "emits one effect; everything else is a no-op REJECTED, never "
                    "an exception."),
        prose("""
#### Lens 2 — rejection is a value, not a raise

Look at `_from_awaiting_ci` (lines 144–159). A `CiResolved` whose status is
*still pending* returns `_rejected(state, "ci still pending; the spine must
wait")` — the state does **not** change and **no exception is thrown**. This is
how the “you can never record an unresolved CI” rule is expressed *in the pure
layer*: the machine simply refuses to move, leaving the spine to keep polling.
Only a terminal status builds the `LoopOutcome` and advances to `Recorded`.
"""),
        callout("trace", """
**Lens 3 — an execution trace (the happy path).** Watch the values flow,
exactly as `test_state_machine.py::test_happy_path_drives_to_recorded` asserts:

1. `start(left-pad 1.4.2→1.4.3)` → `Discovered`, emit `JudgeChangelog`.
2. `advance(Discovered, ChangelogJudged(clean))` → `Judged`, emit `OpenPullRequest`.
3. `advance(Judged, PullRequestReady(pr#1))` → `AwaitingCi`, emit `AwaitCi`.
4. `advance(AwaitingCi, CiResolved(CIPassed))` → `Recorded`, emit `RecordOutcome`; `outcome.ci_passed` is `True`.
5. `advance(Recorded, OutcomeRecorded())` → IGNORED, `effects == ()` → the driver loop ends.

Five pure calls, zero I/O — the entire loop's logic, proven in a unit test.
"""),
        callout("insight", """
**The `Transition` record is the contract with the spine.** Its `effects` tuple
is what the bump workflow drives: a non-empty tuple means “run this, feed me the
event, ask me again”; an empty tuple means “stop.” The spine in §6.5 is little
more than a `while transition.effects:` loop around this function — all the
*logic* is here, all the *durability* is there.
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT III — THE SEAM (ports)
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="ports", act="Act III · The seam", num="3.1",
    title="`ports.protocols` — four typed promises",
    technique="Interface table + hexagon",
    files=["src/froot/ports/__init__.py", "src/froot/ports/protocols.py"],
    blocks=[
        prose("""
We've reached the membrane. Everything inward of here is pure; everything outward
is I/O. The membrane itself is four `typing.Protocol`s — *structural* interfaces
the spine depends on, with zero knowledge of the concrete clients behind them.
"""),
        diagram("hexagon",
                 "The ports-and-adapters seam. The spine talks to four Protocols; "
                 "production wires real adapters behind them, tests wire in-memory "
                 "fakes. Neither side imports the other.", klass="wide"),
        src("src/froot/ports/protocols.py", fold=[(1, 26)]),
        table(
            ["Port", "Methods", "Real adapter", "Fake (tests)"],
            [
                ["`PackageManager`", "`list_upgrades`, `apply_patch_bump`", "`NpmPackageManager`", "`FakePackageManager`"],
                ["`Forge`", "`checkout`, `push_branch`, `find_open_pull_request`, `open_pull_request`, `ci_status`, `add_labels`", "`GitHubForge`", "`FakeForge`"],
                ["`ChangelogSource`", "`fetch`", "`HttpChangelogSource`", "`FakeChangelogSource`"],
                ["`ModelJudge`", "`judge`", "`PydanticAiJudge`", "`FakeJudge`"],
            ],
            caption="Four ports, each with a real implementation and an in-memory "
                    "fake. The spine names only the left column."),
        callout("why", """
**Why `Protocol` and not an ABC?** Structural typing means an adapter doesn't
have to *inherit* anything to satisfy a port — it just has to have the right
shape. So `NpmPackageManager` is a plain class with two async methods; `mypy`
checks it conforms where it's used. The fakes in `tests/support.py` likewise
satisfy the ports without any base class. This keeps the adapters decoupled even
from the port definitions, and it's why the activity bodies can import an adapter
*lazily* (next act) without dragging a class hierarchy into the workflow sandbox.
"""),
        callout("insight", """
**Every method is `async`.** A port method is awaited by an activity. An adapter
wrapping a *blocking* tool (`npm`, `git`) runs it off the event loop internally
(§4.1); one backed by an HTTP API uses an async client. The seam is uniformly
async so the spine never has to care which kind of work hides behind a call.
"""),
        src("src/froot/ports/__init__.py"),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT IV — THE IMPURE SHELL (adapters)
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act4-intro", act="Act IV · The impure shell", num="4.0",
    title="Where the I/O lives — and a rule about purity",
    technique="Orientation",
    files=["src/froot/adapters/__init__.py"],
    blocks=[
        prose("""
Now the messy outside world: subprocesses, git, the GitHub REST API, the npm
registry, a local model, OpenTelemetry. Seven modules, each backing one port.
But notice the discipline even here — the *pure cores* of each adapter (parsing
npm output, mapping GitHub checks to a `CIStatus`, mapping a model assessment to a
verdict) are pulled out as module-level functions, unit-tested with no network.
"""),
        src("src/froot/adapters/__init__.py"),
        callout("principle", """
**One sandbox rule to remember for all of Act IV.** Read the last sentence of that
docstring: these modules are imported **lazily, inside activity bodies — never at
a workflow module's top level**. The model stack, httpx, and OpenTelemetry must
never enter the Temporal *workflow sandbox* (which re-imports modules to enforce
determinism). Keep this in mind; it explains an otherwise-odd import style we'll
see throughout the spine.
"""),
    ],
))

add(Section(
    id="proc", act="Act IV · The impure shell", num="4.1",
    title="`_proc` — running tools, scrubbing secrets",
    technique="Security spotlight",
    files=["src/froot/adapters/_proc.py"],
    blocks=[
        prose("""
`npm` and `git` are blocking CLIs. This 36-line helper runs them off the event
loop and returns `(exit_code, stdout)` — and does one more thing that's easy to
miss but genuinely important.
"""),
        src("src/froot/adapters/_proc.py", fold=[(1, 13)],
             spotlight=[(19, 19), (36, 36)]),
        callout("security", """
**Credential redaction as defense-in-depth.** Line 19 compiles
`_USERINFO = re.compile(r"://[^@/\\s]+@")`, and line 36 scrubs any `user:pass@`
URL userinfo out of captured stdout before returning it. Why? froot's git remote
is `https://x-access-token:<TOKEN>@github.com/...` (§4.3). If a git command echoed
that remote in an error, the token would otherwise flow into a `RuntimeError`
message — and from there into Temporal's durable workflow history and the logs.
The redaction means even a leaked remote surfaces as `://***@`. `stderr` is
captured but *discarded* entirely; adapters surface failures via the exit code and
a domain-level message, never raw tool chatter.
"""),
        callout("insight", """
**`returncode or 0`** coerces the `int | None` exit code to a definite `int`, so
callers can always compare `if code != 0`. `returncode` is `None` only *before*
the process has exited — and here `await process.communicate()` has already
awaited exit, so in practice it's set. (A process killed by a signal returns a
*negative* int, e.g. `-9`, which is truthy and passes through `or 0` unchanged —
so the coercion only ever fires for the not-yet-exited `None`.) A tiny detail, but
the kind that keeps the type honest and the comparison total.
"""),
    ],
))

add(Section(
    id="npm", act="Act IV · The impure shell", num="4.2",
    title="`npm` — read upgrades, regen the lockfile, run no code",
    technique="Pipeline flowchart + parser spotlight",
    files=["src/froot/adapters/npm.py"],
    blocks=[
        prose("""
The npm adapter is where the loop's “bounded action” becomes real — and where one
of froot's safety guarantees is enforced. It does two things: report what's
upgradable, and rewrite the manifest + lockfile to a target. Let's follow the read
path first.
"""),
        diagram("npm-pipeline",
                 "list_upgrades: read direct deps from package.json, current "
                 "versions from the lockfile (not `npm outdated`), available "
                 "versions from `npm view`, hand the raw facts to the pure policy.",
                 klass="wide"),
        src("src/froot/adapters/npm.py", fold=[(1, 16)],
             spotlight=[(149, 162)]),
        prose("""
#### Three pure parsers, tested with fixtures

The interesting logic is in module functions, away from the subprocess.
`parse_direct_dependencies` reads `dependencies` + `devDependencies` (only direct
deps — bumping a transitive one would promote it to direct, which isn't a patch).
`parse_locked_versions` reads the lockfileVersion 2/3 `packages` map (skipping
nested `node_modules/.../node_modules/...` transitive entries) and falls back to
the legacy v1 `dependencies` map. `parse_versions` turns `npm view ... --json`
into domain `Version`s, dropping anything unparseable.
"""),
        callout("gotcha", """
**Why read the lockfile instead of `npm outdated`?** The module docstring nails a
subtle trap: `npm outdated`'s `current` field is **absent without a
`node_modules` tree**, and froot only ever does a shallow *clone*, never an
install. So the installed baseline must come from `package-lock.json`. Reading
state from committed files rather than an installed tree is what keeps the worker
install-free.
"""),
        callout("security", """
**The spotlighted lines are froot's blast-radius guarantee.** `apply_patch_bump`
runs `npm install <pkg>@<target> --package-lock-only --ignore-scripts`.
`--package-lock-only` resolves and rewrites the dependency tree **without
installing** `node_modules`; `--ignore-scripts` means **no third-party package's
install scripts ever execute** inside the privileged, token-bearing worker. The
real install, build, and tests happen later — in the target repo's CI, which is
already a sandbox. The worker carries package managers, not test toolchains. Tiny
blast radius, by construction (this is the proven Renovate/Dependabot mechanic,
owned rather than depended upon).
"""),
    ],
))

add(Section(
    id="github", act="Act IV · The impure shell", num="4.3",
    title="`github` — git, the GitHub API, and the oracle",
    technique="Truth-table + idempotency sequence",
    files=["src/froot/adapters/github.py"],
    blocks=[
        prose("""
The largest adapter (276 lines) is the `Forge`: checkout and branch-push go
through `git`; pull requests, CI status, and labels go through the GitHub REST API
via `httpx`. Three things deserve a close look — the pure CI mapping, the
idempotent PR open, and how auth failures are classified.
"""),
        src("src/froot/adapters/github.py", fold=[(1, 39), (109, 146)],
             spotlight=[(69, 96)]),
        prose("""
#### The CI mapping is a pure truth-table

`ci_status_from_checks` (spotlighted) is the oracle-reading logic, factored out as
a pure function over typed `CheckRow`s + the legacy combined status — so it's
unit-tested apart from the network. Its rules:
"""),
        table(
            ["check runs", "combined status", "→ `CIStatus`"],
            [
                ["none", "none", "`CIAbsent` (nothing to verify)"],
                ["any not `completed`", "—", "`CIPending` (keep waiting)"],
                ["—", "`pending`", "`CIPending`"],
                ["any bad conclusion*", "—", "`CIFailed(failing=…)`"],
                ["—", "`failure`", "`CIFailed`"],
                ["all completed & good", "`success`/none", "`CIPassed`"],
            ],
            caption="*bad conclusions: failure, timed_out, cancelled, "
                    "action_required, startup_failure, stale. The mapping unifies "
                    "the modern Checks API with the legacy combined-status API."),
        prose("""
#### Opening a PR is idempotent

`open_pull_request` is written so a re-run never double-opens. It POSTs the PR; if
GitHub answers **422** (a PR for that head branch already exists — a race), it
*re-finds* the open PR and returns it instead of erroring. And the activity that
calls it (§6.6) checks `find_open_pull_request` *first*, short-circuiting before
any checkout when a PR already exists.
"""),
        diagram("pr-idempotent",
                 "The idempotent open. The fast path short-circuits on an existing "
                 "PR with no checkout/apply/push; the 422 branch handles the "
                 "create-race. The deterministic branch name (§2.2) is what makes "
                 "the lookup possible.", klass="wide"),
        callout("security", """
**Permanent faults fail fast; transient faults retry.** A missing token raises
`ApplicationError(..., non_retryable=True)` — a misconfiguration is not something
to retry forever. Likewise `_raise_for_status` turns a **401/403** into a
non-retryable error, while other HTTP errors raise normally (so Temporal's retry
policy *does* back off and retry transient 5xx/network blips). The auth remote
embeds the token as `x-access-token:<token>@github.com`, and the token itself
comes from a `SecretStr` (§5.1) and is scrubbed from any captured output (§4.1).
"""),
        callout("insight", """
**The boundary coercions are explicit.** `_pull_request_ref` reads GitHub's untyped
JSON (`payload["head"]["sha"]`, etc.) and *coerces* it into a domain
`PullRequestRef` right at the edge — `int(...)`, `str(...)`, a validated
`BranchName`. Untyped shapes are not allowed to travel inward; they become domain
types the moment they cross the membrane.
"""),
    ],
))

add(Section(
    id="changelog-http", act="Act IV · The impure shell", num="4.4",
    title="`changelog_http` — best-effort, and proud of it",
    technique="Branch flowchart",
    files=["src/froot/adapters/changelog_http.py"],
    blocks=[
        prose("""
There is no universal changelog format, so froot fetches the one cheap, reliable
signal of *what changed*: the linked GitHub repo's **release notes** for the
version tag. Every failure path returns `None` — and `None` is a first-class,
expected answer.
"""),
        diagram("changelog-fetch",
                 "Every dead end returns None, which the judge activity maps to "
                 "UnknownVerdict without spending a model call. Only a real "
                 "changelog reaches the model.", klass="wide"),
        src("src/froot/adapters/changelog_http.py", fold=[(1, 27)],
             spotlight=[(55, 63)]),
        prose("""
`fetch` wraps the whole thing in a `try/except (httpx.HTTPError,
json.JSONDecodeError)` → `None`: a network error or a malformed 200 body both mean
“no usable changelog.” `github_repo_from_registry` is a pure function (tested
offline) that digs the GitHub slug out of the registry's `repository.url`, in all
its forms (`git+https://…`, `git://…`, a bare string). `_release_notes` tries both
`vX.Y.Z` and `X.Y.Z` tags.
"""),
        callout("why", """
**A deliberate omission.** The docstring is emphatic: a package's registry
*description* is **not** used as a fallback. Why? It describes what the package
*does*, not what *changed between versions* — feeding it to the judge produces
misleading risk verdicts. froot would rather return `None` (→ honest
`UnknownVerdict`) than feed the model a non-changelog. This is spine-thinking
applied to the model: never ask it to judge something that isn't the thing.
"""),
    ],
))

add(Section(
    id="model", act="Act IV · The impure shell", num="4.5",
    title="The one model call — `model` + `model_judge`",
    technique="The single judgment, spotlighted",
    files=["src/froot/adapters/model.py", "src/froot/adapters/model_judge.py"],
    blocks=[
        prose("""
Here is froot's *entire* use of an LLM. Two small files: one builds the model, one
asks it the single question the loop needs answered. Everything model-thin about
froot converges here.
"""),
        prose("""
#### Building the model — local, swappable, sandbox-isolated
"""),
        src("src/froot/adapters/model.py", fold=[(1, 25)]),
        prose("""
A local Ollama (Gemma) is driven through its OpenAI-compatible `/v1` by Pydantic
AI's OpenAI provider — so heavy inference stays off the request-tight cluster node
and on the Mac Studio (§9.4). The model and endpoint come from settings; the key
is the literal `"ollama"` because Ollama ignores it but the OpenAI client demands
a non-empty one.

#### Asking the one question
"""),
        src("src/froot/adapters/model_judge.py", fold=[(1, 30)],
             spotlight=[(31, 43), (54, 66)]),
        prose("""
The agent's `output_type` is a Pydantic `_Assessment` (`verdict`, `rationale`,
`concerns`), so Pydantic AI *constrains the model to return that shape*. The pure
`assessment_to_verdict` then maps it to the domain `ChangelogVerdict` — and ends
in `assert_never`, so the three verdict literals must all be handled. The model is
*injected* into the constructor, which is exactly how the test runs it offline
with a `TestModel`.
"""),
        callout("insight", """
**Read the system prompt — it's the whole philosophy.** Lines 31–43 tell the
model: *“The bot proposes the bump either way; your job is only to frame the risk
for the human reviewer.”* It asks for clean / risky / unknown, and adds a
**quote-or-omit** rule: base “risky” concerns on what the text *actually says*; do
not speculate. The model isn't a gatekeeper and isn't asked to be clever — it's a
triage aid for the steward, kept on a tight, typed leash.
"""),
        callout("principle", """
**Spine-heavy, model-thin, in one number: 1.** Across froot's ~3,000 lines, the
model is consulted exactly once per bump, only when a real changelog exists, and
its answer can only ever *frame* — never *gate*. Determinism is replay-safe, cheap,
and auditable; model autonomy is none of those, so froot spends it only where
judgment is irreducible.
"""),
    ],
))

add(Section(
    id="telemetry", act="Act IV · The impure shell", num="4.6",
    title="`telemetry` — observability that's off by default",
    technique="Annotated walkthrough + counterfactual",
    files=["src/froot/adapters/telemetry.py"],
    blocks=[
        prose("""
The run-telemetry half of “derive, never store”: traces and Temporal SDK metrics
export OTLP/HTTP to the in-cluster collector, which forwards to ClickStack. The
whole module is **gated** on one setting and is a complete no-op when off.
"""),
        src("src/froot/adapters/telemetry.py", fold=[(1, 36), (43, 70), (86, 118)],
             spotlight=[(38, 41), (121, 134)]),
        prose("""
Every side-effecting function short-circuits when telemetry is off — four of them
(`tracing_interceptors`, `metrics_runtime`, `instrument_httpx`,
`shutdown_tracing`) open with a plain `if not otel_enabled(): return …`, while
`setup_tracing` leads with a compound `if _tracing_configured or not
otel_enabled(): return` that adds idempotency, and `otel_enabled` is the gate
predicate itself. So a local run or a test spins up **no** exporter threads, makes
no network calls, and stays telemetry-free. And every OpenTelemetry import is
*inside* a function body, never at module top level — the same sandbox-hygiene rule
as the rest of Act IV.
"""),
        callout("gotcha", """
**The `shutdown_tracing` subtlety.** The `BatchSpanProcessor` buffers spans for
~5 seconds, and Python's `atexit` does **not** run on an unhandled `SIGTERM`. So
without an explicit flush on graceful shutdown, the worker's *last batch of spans
is dropped on every rollout* (Kubernetes sends SIGTERM, and the Deployment uses a
`Recreate` strategy — §9.4). `shutdown_tracing` (spotlighted) is what the worker
calls in its `finally` block (§7.1) to flush before exit. A genuinely easy bug to
ship; froot saw it coming.
"""),
        callout("insight", """
**Metrics are CUMULATIVE on purpose** (line ~104) — to match what's already in
ClickStack, so froot's series line up with the rest of the observability stack
rather than creating a parallel, delta-temporality island. Even the telemetry
obeys “fit the terrain that already exists.”
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT V — CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="settings", act="Act V · Configuration", num="5.1",
    title="`settings` — all the knobs, none of the secrets",
    technique="Settings table + security",
    files=["src/froot/config/__init__.py", "src/froot/config/settings.py"],
    blocks=[
        prose("""
Every deployment difference between “my laptop” and “the cluster” is one of these
five frozen `pydantic-settings` models, each reading a small slice of the
environment. Nothing secret lives in the repo; each consumer builds the tiny model
it needs at its point of use.
"""),
        src("src/froot/config/settings.py", fold=[(1, 27)],
             spotlight=[(41, 62), (84, 97)]),
        table(
            ["Model", "Env var(s)", "Default", "Read by"],
            [
                ["`Settings`", "`FROOT_REPOS`, `FROOT_SCAN_INTERVAL_SECONDS`", "— / `86400`", "the scan starter"],
                ["`TemporalSettings`", "`TEMPORAL_HOST/NAMESPACE/TASK_QUEUE`", "`localhost:7233` / `default` / `froot`", "worker, starter, activity client"],
                ["`GitHubSettings`", "`FROOT_GITHUB_TOKEN`", "`None`", "the GitHub forge"],
                ["`ModelSettings`", "`FROOT_OLLAMA_MODEL/URL`", "`gemma4:e4b` / local `/v1`", "the model builder"],
                ["`TelemetrySettings`", "`FROOT_OTEL`", "`False`", "the telemetry module"],
            ],
            caption="Five focused settings models. The same image runs anywhere by "
                    "changing only these env vars."),
        callout("security", """
**The token is a `SecretStr`.** `GitHubSettings.github_token` is typed
`SecretStr | None`, so it is **masked in `repr`, logs, and tracebacks** — printing
the settings object, or letting it into an exception, shows `**********`, never the
token. The real value is reachable only via an explicit
`.get_secret_value()` call, which appears **exactly once** — inside the `_token()`
helper in `github.py` — whose result then feeds the two places the token is
actually sent (the auth remote URL and the API `Authorization` header). The test
`test_github_token_is_secret_and_masked` asserts the token can't leak into `repr`.
"""),
        prose("""
#### Two parsing niceties

`repos` is `Annotated[..., NoDecode]` with a `field_validator(mode="before")`, so
`FROOT_REPOS` is read as a friendly **comma-separated** list of `owner/name` slugs
(each parsed through `RepoRef.parse`, raising on a bad slug) rather than JSON. And
`TelemetrySettings._blank_is_off` treats an empty/whitespace `FROOT_OTEL` as
`False` rather than a parse error — so an unset-but-present env var is simply off.
"""),
        callout("insight", """
**`frozen=True` here too.** The settings models are immutable like the domain.
Config is read once and can't be mutated mid-run, which removes a whole class of
“who changed the task queue at runtime?” surprise. `extra="ignore"` lets each
model coexist with the others' env vars without complaint.
"""),
        src("src/froot/config/__init__.py"),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT VI — THE DURABLE SPINE (workflow)
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act6-intro", act="Act VI · The durable spine", num="6.0",
    title="Durability is what closes the loop",
    technique="Orientation",
    files=["src/froot/workflow/__init__.py"],
    blocks=[
        prose("""
We arrive at the reason froot exists on Temporal at all. The spine is *thin* — two
workflows, six activities, a little wiring — because all the *logic* already lives
in the pure core. What the spine adds is **durability**: a self-triggering
schedule, a CI wait that survives an hour without holding a process open, and a
recorded outcome that persists. The workflows use only pure state and Temporal's
own APIs, so they **replay deterministically**.
"""),
        src("src/froot/workflow/__init__.py"),
        callout("principle", """
**The sandbox contract.** A Temporal *workflow* must be deterministic — Temporal
re-executes (“replays”) its code against history to recover state, so it may not
do I/O, read the wall clock, or import nondeterministic modules. froot honors this
three ways, which you'll see repeatedly in this act: **(1)** all I/O is in
*activities*, never workflows; **(2)** adapters are imported *lazily inside
activity bodies*; **(3)** workflow modules import even pure code through
`with workflow.unsafe.imports_passed_through()`, telling Temporal's sandbox these
are safe and need not be re-imported.
"""),
    ],
))

add(Section(
    id="wf-types", act="Act VI · The durable spine", num="6.1",
    title="`types` & `constants` — the serializable params and the clocks",
    technique="Two quick tables",
    files=["src/froot/workflow/types.py", "src/froot/workflow/constants.py"],
    blocks=[
        prose("""
Two small support modules first. `types.py` holds the frozen, domain-shaped models
that cross the Temporal boundary — every activity that needs more than one value
takes a single bundled input, so signatures stay stable and typed.
"""),
        src("src/froot/workflow/types.py", fold=[(1, 20)]),
        table(
            ["Type", "Carries", "For"],
            [
                ["`ScanParams`", "target, interval, `continuous`", "the scan loop input"],
                ["`ScanResult`", "`found`, `dispatched`", "one scan tick's report"],
                ["`BumpParams`", "target, candidate", "the bump loop input"],
                ["`OpenPrInput` / `CiCheckInput` / `RecordInput` / `DispatchInput`", "bundled activity args", "stable activity signatures"],
            ],
            caption="Workflow/activity payloads — all frozen domain values, "
                    "(de)serialized by the Pydantic data converter."),
        prose("""
`constants.py` collects every timeout in one stdlib-only (sandbox-safe) place. The
last two are the interesting ones — they define the **durable CI wait**.
"""),
        src("src/froot/workflow/constants.py", spotlight=[(14, 19)]),
        callout("why", """
**The durable wait is Temporal's sweet spot.** `CI_POLL_INTERVAL = 1 minute`,
`CI_WAIT_DEADLINE = 1 hour`. The wait is implemented as a *workflow timer* —
durable and **free while idle**: froot can sit on a slow CI run for an hour
without holding any process, thread, or connection open. This is precisely the
capability a local script can't have, and precisely why “durably wait on CI” is
listed as ingredient ③ of a closed loop. A generous 10-minute per-activity ceiling
covers a checkout + npm + git + a possibly-cold local model call.
"""),
    ],
))

add(Section(
    id="runtime", act="Act VI · The durable spine", num="6.2",
    title="`runtime` — the registry the worker assembles from",
    technique="Spotlight",
    files=["src/froot/workflow/runtime.py"],
    blocks=[
        prose("""
A three-symbol module that names what the worker (and the workflow tests)
register: `DATA_CONVERTER` (the data converter), `WORKFLOWS` (the two workflows),
and `ALL_ACTIVITIES` (the six activities).
"""),
        src("src/froot/workflow/runtime.py", fold=[(1, 19)],
             spotlight=[(21, 32)]),
        callout("insight", """
**`pydantic_data_converter` is what lets domain models cross the wire.** Temporal
serializes every workflow arg, return, and activity payload. froot's are frozen
Pydantic models and discriminated unions — so it sets Temporal's *Pydantic* data
converter, and the discriminators from Act I (`kind="clean"`, `kind="passed"`, …)
are what make those unions round-trip back into the right subtype.
`test_domain_models.py::test_discriminated_unions_round_trip` proves the property
the spine depends on.
"""),
    ],
))

add(Section(
    id="scan-workflow", act="Act VI · The durable spine", num="6.3",
    title="`scan_workflow` — the self-scheduling trigger",
    technique="Counterfactual (why continue-as-new)",
    files=["src/froot/workflow/scan_workflow.py"],
    blocks=[
        prose("""
This is froot's *signal* — ingredient ① — made durable. One long-lived workflow
per repo. Each tick checks out the repo, selects candidates, dispatches a bump
loop per candidate, then sleeps and restarts.
"""),
        diagram("scan-tick",
                 "One tick: scan → dispatch each (idempotent) → sleep on a durable "
                 "timer → continue_as_new into a fresh tick. No stored cursor; the "
                 "next tick re-derives the work from the repo.", klass="wide"),
        src("src/froot/workflow/scan_workflow.py", fold=[(1, 25)],
             spotlight=[(45, 56)]),
        prose("""
The shape is a self-perpetuating loop. A one-shot run (`continuous=False`, the
default — used by tests and the e2e harness) does a single tick and returns.
Production starts it once with `continuous=True`, and it runs forever: sleep the
interval, then `continue_as_new`.
"""),
        callout("counter", """
**Why `continue_as_new` instead of `while True:`?** A naïve infinite loop would
make the workflow's *event history* grow without bound — every tick's activities
appended forever — until it hits Temporal's history limits and degrades replay.
`continue_as_new` atomically restarts the workflow with fresh parameters and a
**fresh, empty history**, bounded to a single tick. The comment captures the other
subtlety: `continue_as_new` *raises*, so nothing after it runs — the loop can't
accidentally fall through. Delete it and the loop either grows unbounded or stops
after one tick; it's the linchpin of a durable schedule.
"""),
        callout("principle", """
**No stored seen-set — derive, never store.** There is no database of “bumps I've
already proposed.” Each tick re-derives the outstanding work *from the repo
itself*, and the deterministic per-bump workflow id (§2.2) makes re-dispatching an
already-handled bump a harmless no-op. The loop's memory lives in GitHub (open
PRs) and Temporal (running workflows), not in froot.
"""),
    ],
))

add(Section(
    id="bump-workflow", act="Act VI · The durable spine", num="6.4",
    title="`bump_workflow` — driving the pure machine, durably",
    technique="Sequence diagram + the durable wait",
    files=["src/froot/workflow/bump_workflow.py"],
    blocks=[
        prose("""
The crown jewel of the spine. One durable workflow per `(repo, package, target)`,
and it is astonishingly thin: a loop that asks the pure state machine for the next
effect, runs it as an activity, feeds the resulting event back, and repeats until
`Recorded`. *All* the logic is in §2.4; *all* the durability is here.
"""),
        diagram("bump-sequence",
                 "One full bump. Each pure effect becomes an activity call whose "
                 "result becomes the next event fed back to advance(). The AwaitCi "
                 "effect expands into the durable poll/sleep loop.", klass="wide"),
        src("src/froot/workflow/bump_workflow.py", fold=[(1, 57)],
             spotlight=[(63, 88), (123, 138)]),
        prose("""
#### The driver loop

`run` (lines 63–88) is the whole driver: `start(candidate)` gives the first
transition; `while transition.effects:` runs the single effect, calls
`advance(state, event)`, and repeats. It defends its own invariants with
*non-retryable* `ApplicationError`s — a non-linear transition (more than one
effect), a `REJECTED` transition, or a loop that somehow ends in a non-`Recorded`
state are all programming errors, surfaced loudly rather than retried.
"""),
        prose("""
#### The durable CI wait

`_await_ci` (spotlighted, lines 123–138) is ingredient ③ in code. It computes a
`deadline = workflow.now() + CI_WAIT_DEADLINE`, then polls: call `check_ci`; if the
status `is_terminal`, return it (the `TypeIs` from §1.7 narrows it for the caller);
if past the deadline, return `CITimedOut()`; otherwise `await workflow.sleep(1
minute)` and loop.
"""),
        callout("insight", """
**Every time-related call is a Temporal API, not Python's.** `workflow.now()` (not
`datetime.now()`) and `workflow.sleep()` (not `asyncio.sleep()`) are
*replay-deterministic*: on replay Temporal returns the same recorded time and
fast-forwards the same sleeps, so the workflow reconstructs identically. This is
why the hour-long wait is free and why the time-skipping test server (§8.4) can
fast-forward it to milliseconds. Use Python's clock here and replay would diverge.
"""),
        callout("why", """
**Why interpret effects instead of just calling activities directly?** Because the
*decision* of what comes next stays in the pure, tested state machine. The workflow
never decides “after judging, open a PR” — it asks `advance()` and is *told*. The
workflow is a dumb, durable executor of a smart, pure plan. That separation is what
keeps 171 lines of logic unit-testable and ~140 lines of durability replay-safe,
with neither contaminating the other.
"""),
    ],
))

add(Section(
    id="activities", act="Act VI · The durable spine", num="6.5",
    title="`activities` — the impure boundary, one effect at a time",
    technique="Effect→activity map + lazy-import spotlight",
    files=["src/froot/workflow/activities.py"],
    blocks=[
        prose("""
Activities are where froot is *allowed* to touch the world. Each one is the impure
interpreter for a single effect, wrapping the adapters from Act IV. They return
domain values; the workflow wraps those into events.
"""),
        src("src/froot/workflow/activities.py", fold=[(1, 34)],
             spotlight=[(43, 59), (105, 128)]),
        table(
            ["Activity", "Effect it serves", "Adapters used"],
            [
                ["`scan_candidates`", "(scan loop)", "`GitHubForge` + `NpmPackageManager` → pure policy"],
                ["`judge_changelog`", "`JudgeChangelog`", "`HttpChangelogSource` + `PydanticAiJudge`"],
                ["`open_pull_request`", "`OpenPullRequest`", "`GitHubForge` + `NpmPackageManager`"],
                ["`check_ci`", "`AwaitCi` (per poll)", "`GitHubForge`"],
                ["`record_outcome`", "`RecordOutcome`", "`GitHubForge` + the outcome log"],
                ["`dispatch_bump`", "(scan loop)", "the Temporal client"],
            ],
            caption="Six activities, one per effect (plus the two scan-loop steps). "
                    "Each imports its adapters lazily, inside the body."),
        prose("""
#### Lazy imports are the sandbox rule, enforced

Look at the top of any activity: `from froot.adapters.github import GitHubForge`
lives *inside* the function, not at module scope. The domain/policy imports stay at
module level (Temporal evaluates activity *signatures* at registration), but the
heavy, nondeterministic adapter stacks are imported only when the activity actually
runs — so they never enter the workflow sandbox's import graph.
"""),
        callout("insight", """
**`record_outcome` is the signal-update, in the literal sense.** It does two
things (lines 105–128): `add_labels` on the PR (the human-readable mark) and a
single structured `_log.info(json.dumps({...}))` on the `froot.outcome` logger,
carrying repo, package, from→to, changelog verdict kind, CI kind, `ci_passed`, and
the PR number/URL. That JSON record is the ClickStack half of “derive, never
store”: the code emits it on the logger, and the *deployment* routes the worker's
stdout to the cluster's filelog → ClickStack (the worker manifest's own comment
says “structured outcome logs go to stdout (free filelog)”). froot keeps no copy —
the PR plus this log line are the entire persisted outcome.
"""),
        prose("""
#### `dispatch_bump` — idempotent start

`dispatch_bump` (lines 131–153) starts a `BumpWorkflow` with the deterministic id
and `WorkflowIDReusePolicy.REJECT_DUPLICATE`, swallowing
`WorkflowAlreadyStartedError` as a no-op. This is the first of the two dedup layers
from §2.2: re-scanning a repo can't open a second loop for a bump that already has
one (running *or* completed).
"""),
        code("projects/froot/src/froot/workflow/activities.py",
             title="dispatch_bump — the idempotent start",
             logical="activities-dispatch-peek", peek=[(131, 153)]),
    ],
))

add(Section(
    id="temporal-client", act="Act VI · The durable spine", num="6.6",
    title="`temporal_client` — one client, lazily, no telemetry",
    technique="Q&A",
    files=["src/froot/workflow/temporal_client.py"],
    blocks=[
        prose("""
The scan loop's `dispatch_bump` needs a Temporal *client* to start bump workflows.
This module provides exactly one, connected on first use and cached for the
process.
"""),
        src("src/froot/workflow/temporal_client.py", fold=[(1, 18)],
             spotlight=[(41, 47)]),
        callout("note", """
**Q: Why a process-wide lazy singleton, and why is it so deliberately bare?**
**A:** An activity may run many times in a worker; reconnecting a Temporal client
each time would be wasteful, so it's connected once and cached in `_CLIENT` (reset
between tests by `conftest.py`). And it's *intentionally free of telemetry
imports* — it sits in the activity import graph, and pulling OpenTelemetry through
here could drag it toward the workflow-sandbox boundary. Bare on purpose: it builds
its own Pydantic data converter and reads `TemporalSettings`, nothing more.
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT VII — ENTRYPOINTS
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="worker", act="Act VII · Entrypoints", num="7.1",
    title="`worker` — the runnable assembly",
    technique="Annotated walkthrough",
    files=["src/froot/worker.py"],
    blocks=[
        prose("""
The image's default entrypoint. It connects to Temporal with the Pydantic data
converter and registers the whole runtime — both workflows, every activity — then
runs until signalled.
"""),
        src("src/froot/worker.py", fold=[(1, 16)],
             spotlight=[(34, 37), (71, 83)]),
        prose("""
The connection is fully env-configured (so the same image runs anywhere), and it
threads in the telemetry pieces from §4.6: `setup_tracing`, `tracing_interceptors`,
`metrics_runtime` — each a no-op when `FROOT_OTEL` is off.
"""),
        callout("why", """
**`max_concurrent_activities = 1`.** A deliberate throttle (lines 34–37): the model
judge calls a single local Gemma (which serializes anyway), and the
household/hobby volume never needs more. Critically, the *durable CI wait sleeps
between polls and does not hold this slot* — so a one-at-a-time worker can still
sit on many in-flight bumps, because the waiting ones aren't occupying the activity
executor. Concurrency where it's free, serialization where the model forces it.
"""),
        callout("gotcha", """
**Graceful shutdown is not optional here.** Lines 71–83 install `SIGTERM`/`SIGINT`
handlers that set an `asyncio.Event`, run the worker `async with` until it fires,
and then — in a `finally` — call `shutdown_tracing()`. This is the other half of
the dropped-spans bug from §4.6: Kubernetes stops the pod with SIGTERM, `atexit`
won't fire, so the flush *must* be wired to the signal. Without this signal
wiring, every `Recreate` rollout silently loses the last batch of telemetry.
"""),
    ],
))

add(Section(
    id="scan-starter", act="Act VII · Entrypoints", num="7.2",
    title="`scan_starter` — the go-live trigger",
    technique="Reuse-policy contrast",
    files=["src/froot/scan_starter.py"],
    blocks=[
        prose("""
The one-shot that *kicks* the loops. Run after the worker is up (a k8s Job, or
locally), it submits a long-lived `ScanWorkflow` for every repo in `FROOT_REPOS`.
"""),
        src("src/froot/scan_starter.py", fold=[(1, 18)],
             spotlight=[(46, 58)]),
        callout("insight", """
**A different reuse policy than dispatch — and that's the point.** `dispatch_bump`
used `REJECT_DUPLICATE` (a bump should run *at most once, ever*). The scan starter
uses **`ALLOW_DUPLICATE_FAILED_ONLY`**: a *running* scan loop is left untouched
(re-running the starter is safe and idempotent), but a *terminated/failed* loop can
be restarted. The two policies encode two different intentions — “never repeat this
unit of work” vs. “keep exactly one live loop, and revive it if it died.” Same
Temporal primitive, opposite-leaning configuration, each matched to its job.
"""),
        callout("note", """
**Re-running is safe by design.** The deterministic `scan_workflow_id` makes the
start idempotent, and the catch on `WorkflowAlreadyStartedError` prints
“left untouched” rather than erroring. To repoint froot at different repos, you
edit `FROOT_REPOS`, refresh the ConfigMap, and re-apply the Job (§9.4) — no manual
cleanup of old loops required beyond the obvious.
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT VIII — HOW IT'S PROVEN (tests)
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act8-intro", act="Act VIII · How it's proven", num="8.0",
    title="A test suite shaped like the architecture",
    technique="The pyramid",
    blocks=[
        prose("""
froot's ~1,460 lines of tests aren't an afterthought — they're the payoff of every
design choice in Acts I–VII. Because the core is pure and the seams are ports, the
suite is a clean pyramid: a broad base of fast pure-unit and property tests, a
middle of activities-over-fakes, and a thin top of *real-spine* integration tests
that run against Temporal's time-skipping server.
"""),
        diagram("test-pyramid",
                 "The testing pyramid mirrors the architecture: pure logic tested "
                 "with no I/O, the seam tested with fakes, the durable spine tested "
                 "on a time-skipping Temporal server.", klass="wide"),
        table(
            ["Tier", "Files", "What it proves", "How"],
            [
                ["🟩 pure unit + property", "`test_version`, `test_candidate`, `test_domain_models`, `test_result`, `test_naming`, `test_candidates_policy`, `test_compose`, `test_state_machine`, `test_settings`, the adapter parsers", "domain invariants, policy decisions, parsers", "plain calls + Hypothesis; no I/O"],
                ["🟦 seam", "`test_activities`", "each activity wires its ports correctly", "in-memory fakes via `monkeypatch`"],
                ["🟦 adapter logic", "`test_npm_adapter`, `test_github_adapter`, `test_changelog_adapter`, `test_model_judge`, `test_telemetry`", "the pure cores of impure adapters", "fixtures + `TestModel`; no network"],
                ["🟦 integration", "`test_bump_workflow`, `test_scan_workflow`", "the real spine end-to-end", "Temporal `start_time_skipping()`"],
            ],
            caption="Every tier and where it sits. Not one test needs npm, git, a "
                    "real GitHub, or a real model."),
    ],
))

add(Section(
    id="fakes", act="Act VIII · How it's proven", num="8.1",
    title="`support` & `conftest` — the fakes that close the ports story",
    technique="Spotlight",
    files=["tests/support.py", "tests/conftest.py"],
    blocks=[
        prose("""
Remember the right-hand column of the ports table in §3.1? Here it is. `support.py`
holds terse *builders* (valid domain values in one call) and in-memory *fakes* that
implement each port's Protocol — the stateful ones recording the calls made to them
so tests can assert behavior.
"""),
        src("tests/support.py", fold=[(1, 31)], collapsed=True,
            note="All four fakes (`FakeForge`, `FakePackageManager`, "
                 "`FakeChangelogSource`, `FakeJudge`) satisfy the ports "
                 "structurally — no base class. `FakeForge` and "
                 "`FakePackageManager` also *record* what they were asked to do "
                 "(`checked_out`, `pushed`, `labeled`, `applied`) so tests can "
                 "assert calls; `FakeChangelogSource` and `FakeJudge` are pure "
                 "stubs returning canned values. Builders like "
                 "`make_candidate`/`make_pr` keep tests short."),
        prose("""
`conftest.py` adds two autouse fixtures that keep tests hermetic: one `chdir`s each
test into a temp directory so a stray local `.env` can't leak into a settings test,
and one resets the process-wide Temporal client cache (§6.6) between tests.
"""),
        src("tests/conftest.py", collapsed=True),
        callout("insight", """
**This file is the proof that the seam works.** Because `FakeForge` can stand in
for `GitHubForge` with no inheritance and no adapter import, the activities can be
exercised entirely in memory. If the ports weren't real abstractions, these fakes
couldn't exist — the suite's hermeticity is the ports design paying off.
"""),
    ],
))

add(Section(
    id="property-tests", act="Act VIII · How it's proven", num="8.2",
    title="Property tests — laws, not just examples",
    technique="Hypothesis highlight",
    files=["tests/test_version.py"],
    blocks=[
        prose("""
Most tests assert *examples*. Two tests on `Version` assert *laws* — universally
quantified properties checked across hundreds of generated inputs by Hypothesis.
"""),
        src("tests/test_version.py", fold=[(1, 52)], spotlight=[(54, 65)],
            collapsed=False),
        callout("insight", """
**Two invariants, proven for the whole input space.** `test_property_parse_str_roundtrip`
asserts that *for any* `major.minor.patch`, parsing the string form returns the
original — `parse` and `__str__` are true inverses.
`test_property_next_patch_is_a_bump` asserts that *for any* version, the
next-higher patch `is_patch_bump_of` it (and not vice-versa). These are the
foundational guarantees the entire signal rests on (§1.3), so froot proves them as
laws rather than spot-checks. The example-based tests above them pin the tricky
specific cases (prereleases, build metadata, ordering).
"""),
    ],
))

add(Section(
    id="time-skipping", act="Act VIII · How it's proven", num="8.3",
    title="The integration tests — an hour-long wait in milliseconds",
    technique="Q&A payoff",
    files=["tests/test_bump_workflow.py", "tests/test_scan_workflow.py"],
    blocks=[
        prose("""
The top of the pyramid runs the **real** workflows — the actual driver loop, effect
interpretation, and durable CI wait — with only the *activities* mocked by name.
And it does so without waiting real time.
"""),
        callout("note", """
**Q: How do you test a workflow that durably waits up to an hour on CI?**
**A: You don't wait.** `WorkflowEnvironment.start_time_skipping()` gives a Temporal
test server that **fast-forwards workflow timers**. When the bump workflow calls
`workflow.sleep(1 minute)` between CI polls, the server advances its virtual clock
instantly. So a test that exercises “pending, pending, then pass,” or even “100×
pending until the 1-hour deadline → `CITimedOut`,” completes in milliseconds — yet
runs the genuine durable-wait code path.
"""),
        src("tests/test_bump_workflow.py", fold=[(1, 42)], spotlight=[(111, 123)],
            collapsed=False),
        prose("""
The scripted `_ci_replies` list (a queue the `check_ci` mock pops through) is the
trick that drives each scenario. `test_ci_pending_then_pass_waits_durably` feeds
`[Pending, Pending, Passed]`; `test_ci_timeout_when_never_resolves` feeds 100
pendings and asserts the outcome is `CITimedOut`. The four tests cover the loop's
four terminal shapes — green, red, pending-then-green, and timeout.
"""),
        src("tests/test_scan_workflow.py", fold=[(1, 41)], spotlight=[(64, 88)],
            collapsed=True,
            note="The scan-loop integration test verifies the fan-out (one "
                 "dispatch per candidate) and — in `test_continuous_loop_…` — that "
                 "advancing virtual time past one interval makes the loop "
                 "`continue_as_new` into another tick rather than ending."),
        callout("insight", """
**This is `workflow.now()`/`workflow.sleep()` (§6.4) paying dividends.** Because the
bump workflow reads time only through Temporal's APIs, the test server can lie about
the clock and the workflow can't tell the difference — which is the *same* property
that makes the production wait free and replay deterministic. One design choice;
two payoffs: cheap durability in prod, fast determinism in tests.
"""),
    ],
))

add(Section(
    id="tests-rest", act="Act VIII · How it's proven", num="8.4",
    title="The rest of the suite, in full",
    technique="Reference gallery",
    blocks=[
        prose("""
For completeness, here is every remaining test file — the example-based unit tests
for the domain, policy, adapters, and activities, plus the live end-to-end harness.
They're collapsed by default; expand any one to read it. Together with the files
above, this is the entire `tests/` tree and the `scripts/e2e_run.py` harness.
"""),
        src("tests/test_activities.py", collapsed=True,
            note="**The seam test.** Each activity is run with its adapters "
                 "`monkeypatch`ed to fakes — proving, e.g., that "
                 "`open_pull_request` short-circuits on an existing PR (no "
                 "checkout), and that `dispatch_bump` is a no-op when already "
                 "started."),
        src("tests/test_state_machine.py", collapsed=True,
            note="**The pure loop.** The happy path drive-to-`Recorded` (the trace "
                 "from §2.4), pending-CI rejection, and an unexpected-event "
                 "rejection in every state."),
        src("tests/test_domain_models.py", collapsed=True,
            note="**Invariants & round-trips.** Anchored repo-segment rejection, "
                 "branch-name validation, `is_terminal`, and the discriminated-"
                 "union round-trips the data converter depends on."),
        src("tests/test_candidate.py", collapsed=True,
            note="**The unrepresentable cases.** Every non-patch (current,target) "
                 "pair raises `ValidationError` at construction (§1.4)."),
        src("tests/test_candidates_policy.py", collapsed=True,
            note="**Selection.** Highest patch chosen, no-patch dropped, sorted "
                 "by package, one per dependency (§2.1)."),
        src("tests/test_naming.py", collapsed=True,
            note="**Determinism.** Branch/workflow ids are stable and scoped-name-"
                 "safe; same inputs → same id (§2.2)."),
        src("tests/test_compose.py", collapsed=True,
            note="**PR text.** Clean/risky/unknown bodies, and the assertion that "
                 "`PR_LABELS` is exactly the fixed pair (§2.3)."),
        src("tests/test_npm_adapter.py", collapsed=True,
            note="**Parsers.** Direct deps, lockfile v2/3 (skipping transitive) "
                 "with v1 fallback, and version parsing that drops garbage (§4.2)."),
        src("tests/test_github_adapter.py", collapsed=True,
            note="**The CI truth-table** and the PR-payload coercion, all pure "
                 "(§4.3)."),
        src("tests/test_changelog_adapter.py", collapsed=True,
            note="**Registry-URL parsing** in all its forms, and the None cases "
                 "(§4.4)."),
        src("tests/test_model_judge.py", collapsed=True,
            note="**The mapping** assessment→verdict, plus a full agent run "
                 "offline via `TestModel` (§4.5)."),
        src("tests/test_settings.py", collapsed=True,
            note="**Config.** Slug parsing, defaults, the masked token, and "
                 "`FROOT_OTEL` truthiness (§5.1)."),
        src("tests/test_telemetry.py", collapsed=True,
            note="**The gate.** OTEL off by default; the flag flips it on (§4.6)."),
        src("tests/test_result.py", collapsed=True,
            note="**The Result type.** `unwrap(Ok)` returns; `unwrap(Err)` raises "
                 "(§1.2)."),
        src("scripts/e2e_run.py", collapsed=True,
            note="**The live harness** (not part of the package): a local Temporal "
                 "server + the *real* worker (real npm, git, GitHub, Ollama) driving "
                 "one scan tick and waiting on the dispatched bump — for validating "
                 "the loop against live systems."),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT IX — BUILD, CI & DEPLOY
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="pyproject", act="Act IX · Build, CI & deploy", num="9.1",
    title="`pyproject.toml` — the strict gate that makes the types real",
    technique="Annotated walkthrough",
    files=["pyproject.toml"],
    blocks=[
        prose("""
Every guarantee in Act I — “illegal states unrepresentable,” `assert_never`
exhaustiveness, `TypeIs` narrowing — is only *real* if a type checker actually
enforces it. `pyproject.toml` is where froot turns the screws all the way: strict
`mypy`, the Pydantic plugin, and a `ruff` lint set tuned to the framework's quirks.
"""),
        code("projects/froot/pyproject.toml", title="pyproject.toml",
             logical="pyproject.toml",
             fold=[(48, 53)], spotlight=[(56, 75), (122, 137)]),
        prose("""
#### Strict mypy is the DDD safety net

Lines 56–75 enable the full strict suite — `disallow_untyped_defs`,
`warn_unreachable`, `warn_unused_ignores`, and the rest — and load the
`pydantic.mypy` plugin, which teaches mypy about model fields, frozen-ness, and
smart constructors. That plugin is what makes `assert_never` and the discriminated
unions *checkable* rather than decorative. Tests relax docstring/annotation rules
but their bodies are still type-checked.
"""),
        callout("gotcha", """
**The subtlest config in the repo (lines 122–137).** Ruff's `flake8-type-checking`
normally wants you to move type-only imports into an `if TYPE_CHECKING:` block. But
**Pydantic evaluates field annotations at runtime** to build validators, and
**Temporal resolves signal/query/run/activity type hints at runtime** to
(de)serialize payloads. Move those imports and you get a runtime `NameError` the
linter happily caused. So froot tells ruff exactly which base classes
(`pydantic.BaseModel`, `froot.domain.base.Frozen`) and which decorators
(`temporalio.workflow.run`, `activity.defn`, …) are *runtime-evaluated*, so their
imports are left at module scope. This single block is why the codebase can be both
aggressively lint-clean and correct under two frameworks that defy the usual
import-hygiene advice.
"""),
        table(
            ["Extra", "Pulls in", "Why it's optional"],
            [
                ["*(core)*", "pydantic, pydantic-settings, temporalio", "the pure core + spine — no model/HTTP"],
                ["`ai`", "pydantic-ai-slim[openai]", "kept out so the model stack never enters a workflow sandbox by default"],
                ["`github`", "httpx", "the forge's HTTP client"],
                ["`otel`", "opentelemetry + temporalio[opentelemetry]", "observability, off unless deployed"],
                ["`dev`", "pytest, hypothesis, mypy, ruff", "tooling only"],
            ],
            caption="Optional-dependency groups keep the default install minimal. "
                    "The Docker image installs ai+github+otel; the pure core needs "
                    "none of them."),
    ],
))

add(Section(
    id="dockerfile", act="Act IX · Build, CI & deploy", num="9.2",
    title="`Dockerfile` — an image that carries package managers, not test runners",
    technique="Annotated walkthrough",
    files=["Dockerfile"],
    blocks=[
        prose("""
The worker image is unusual for a Python service: it also carries `git` and
`npm`. That's the loop's needs showing through — and the blast-radius story from
§4.2 reappears here as a property of the image itself.
"""),
        code("projects/froot/Dockerfile", title="Dockerfile",
             logical="Dockerfile", spotlight=[(14, 17), (27, 28)]),
        callout("why", """
**git + npm, but no node_modules and no test toolchain.** The image installs
`git` (clone/branch/push the PR) and `nodejs`+`npm` (lockfile-only regen + `npm
view`), then `uv sync`s only the runtime extras (`ai`, `github`, `otel`) — not
`dev`. Because the loop regenerates lockfiles with `--package-lock-only
--ignore-scripts`, **no project or dependency code ever executes in this image**;
the real install + tests run in the target repo's CI. So the image stays slim and
its attack surface stays small: it's a package-manager-carrier, not a build farm.
The token and endpoints are read from the environment at runtime, never baked in.
"""),
        callout("insight", """
**`.dockerignore` is part of the security posture.** It excludes `.env`, the venv,
caches, `tests/`, and `scripts/` from the build context — so the token and the test
code never even reach the Docker daemon. The image `COPY`s only `pyproject.toml`,
`uv.lock`, `README.md`, and `src/`.
"""),
        code("projects/froot/.dockerignore", title=".dockerignore",
             logical=".dockerignore", lang="bash", collapsed=True),
    ],
))

add(Section(
    id="ci-make", act="Act IX · Build, CI & deploy", num="9.3",
    title="`Makefile` & CI — one green gate, then an image",
    technique="Table + walkthrough",
    files=["Makefile", ".github/workflows/ci.yml", ".gitignore",
           ".python-version"],
    blocks=[
        prose("""
The developer terrain is intentionally boring: short, single-purpose `make`
targets that each run one tool, so they're easy to read and easy to auto-approve.
"""),
        code("projects/froot/Makefile", title="Makefile", logical="Makefile",
             spotlight=[(31, 32)]),
        prose("""
`make check` is the whole gate — format-check, lint, types, tests — and CI runs the
identical commands. The workflow has two jobs: a **gate** on every pull request and
on pushes to `main` (the `push` trigger is scoped to `branches: [main]`), and an
**image** build-and-push that runs *only* on `main` after the gate passes.
"""),
        code("projects/froot/.github/workflows/ci.yml",
             title=".github/workflows/ci.yml",
             logical=".github/workflows/ci.yml", spotlight=[(28, 32)]),
        callout("insight", """
**The gate guards the image.** `image` declares `needs: gate` and
`if: github.ref == 'refs/heads/main'` — so an image is published to `ghcr.io` only
when a commit lands on `main` *and* the full check suite is green. The image is
tagged both `:latest` and `:<sha>`, and the cluster pulls `:latest` (§9.4). The
push permission is scoped to just that job (`packages: write`), while the gate runs
with read-only `contents`.
"""),
        prose("""
The two remaining housekeeping files: `.python-version` pins the interpreter to a
uv-managed 3.13 (the pyproject comment explains why — Homebrew's 3.14 ships a broken
`pyexpat`), and `.gitignore` keeps caches and — critically — `.env` out of the repo.
"""),
        code("projects/froot/.python-version", title=".python-version",
             logical=".python-version", lang="text", collapsed=True),
        code("projects/froot/.gitignore", title=".gitignore",
             logical=".gitignore", lang="bash", collapsed=True),
        code("projects/froot/.env.example", title=".env.example",
             logical=".env.example", lang="bash", collapsed=True,
             note="The local-config template (gitignored as `.env`): the GitHub "
                  "token, the repo list, the scan interval, Temporal connection, "
                  "and the model endpoint — the same knobs as §5.1."),
    ],
))

add(Section(
    id="deploy", act="Act IX · Build, CI & deploy", num="9.4",
    title="The deployment — one worker, pointed outward",
    technique="Topology diagram + manifests",
    files=["infra/k8s/froot/install.sh",
           "infra/k8s/froot/manifests/10-worker.yaml"],
    blocks=[
        prose("""
froot runs on a single-node DOKS cluster (`zo-k8s`). The deployment is
deliberately minimal: just the **worker** plus two one-shot Jobs (create the
Temporal namespace, kick the scan loop). The Temporal cluster, the Ollama egress,
and ClickStack already live on the cluster; froot connects *out* to all of them.
"""),
        diagram("deploy",
                 "The worker connects out: long-polling Temporal, cloning/PRing "
                 "GitHub, calling the Ollama proxy (which egresses over the tailnet "
                 "to the Mac Studio), and shipping telemetry to ClickStack. No "
                 "inbound traffic.", klass="wide"),
        prose("""
#### The worker Deployment

One replica, `Recreate` strategy (it holds long-poll connections; don't surge),
and — the detail that matters on a request-tight node — **tiny resource requests**
with generous limits.
"""),
        infra("manifests/10-worker.yaml", fold=[(1, 34)], spotlight=[(60, 67)]),
        callout("why", """
**Pinned-tiny requests, real-burst limits.** The node's *request budget* is ~98%
reserved (though actual CPU use is ~50%), and there's no metrics-server. So the
worker requests a deliberately small `cpu: 50m / memory: 64Mi` just to schedule at
all, while its `limits: cpu: 500m / memory: 512Mi` give real headroom for the
npm/git/model spikes. Requests are reservations, not usage — a new pod can go
`Pending` despite real headroom, so froot right-sizes the request rather than the
node. The model runs *externally* (the Ollama tunnel), so the worker itself only
brokers Temporal + a shallow clone + npm + HTTP.
"""),
        prose("""
#### The install script and the two Jobs

`install.sh` is idempotent: it injects the token into a Secret and the repo list
into a ConfigMap (both from the gitignored `infra/.env`, never from disk), applies
the namespace-create Job and the worker, then rolls out. Nothing private is ever
committed or written to Terraform state.
"""),
        infra("install.sh", fold=[(1, 17)], collapsed=True),
        prose("""
The two management Jobs complete the go-live. `namespace-create` idempotently
creates the `froot` Temporal namespace (describe-then-create, 168h retention);
`start-scan` runs `python -m froot.scan_starter` to kick one `ScanWorkflow` per
repo. Both pin tiny requests for the same scheduling reason as the worker.
"""),
        infra("manage/namespace-create.yaml", collapsed=True,
              note="Idempotent Temporal-namespace creation (a `temporalio/admin-"
                   "tools` Job in the `temporal` namespace)."),
        infra("manage/start-scan.yaml", collapsed=True,
              note="The go-live trigger: a one-shot Job running `scan_starter` "
                   "against the worker image (§7.2)."),
        infra("manifests/00-namespace.yaml", collapsed=True,
              note="froot's own k8s namespace — holds only the outbound-connecting "
                   "worker."),
        infra("secrets.example.env", lang="bash", collapsed=True,
              note="The template for what `infra/.env` must carry (token + repo "
                   "list). DO-NOT-commit real values; install.sh reads the real "
                   "ones from the environment."),
        callout("insight", """
**The whole deployment is “point outward.”** froot's namespace contains no
database, no inbound Service, no ingress — just a worker that long-polls Temporal
and reaches GitHub, the model proxy, and the collector. That's the SPEC's “derive,
never store” made physical: the only durable state lives in systems froot doesn't
own (Temporal history, GitHub, ClickStack).
"""),
    ],
))


# ════════════════════════════════════════════════════════════════════════════
# ACT X — CAN I VOUCH FOR THIS?
# ════════════════════════════════════════════════════════════════════════════

add(Section(
    id="act10-intro", act="Act X · Can I vouch for this?", num="10.0",
    title="Pulling the threads together",
    technique="Synthesis",
    blocks=[
        prose("""
You've now seen every line. This final act stops walking *files* and instead walks
*claims* — the design promises froot makes about itself — and points at the
evidence for each. If you've read this far, these should read as confirmations of
things you already saw, not new assertions. That's the test of whether you can
vouch for it.
"""),
    ],
))

add(Section(
    id="scorecard", act="Act X · Can I vouch for this?", num="10.1",
    title="The principles scorecard",
    technique="Evidence table",
    blocks=[
        prose("""
The SPEC lists seven principles that govern every froot decision. Here is each
one, scored against the code you've read, with the file that proves it.
"""),
        table(
            ["SPEC principle", "Upheld by", "Where"],
            [
                ["**1 · Loops must close** — all six ingredients present",
                 "durable schedule (signal), bounded PR (action), CI wait (verification), PR revert (reversibility), the outcome log + labels (signal-update), human-approves-every-PR (authority)",
                 "`scan_workflow`, `bump_workflow`, `record_outcome`"],
                ["**2 · Spine-heavy, model-thin** — model only where judgment is irreducible",
                 "exactly one model call per bump, framing-not-gating; ~90% of the loop is deterministic",
                 "`model_judge.py`, `changelog.py`"],
                ["**3 · CI is the oracle** — never re-run a repo's tests",
                 "froot reads CI status, never runs a test; the worker carries no test toolchain",
                 "`github.ci_status`, `Dockerfile`"],
                ["**4 · Derive, never store** — no database of froot's own",
                 "no DB, no seen-set; work re-derived each tick; outcome lives in GitHub + ClickStack",
                 "`scan_workflow`, `record_outcome`, `outcome.py`"],
                ["**5 · Chassis generalizes, loop specializes**",
                 "the durable machinery imports no concrete adapter; signal + lockfile-cmd + prompt are the only loop-specific bits",
                 "`ports`, `ecosystem.py`, `activities`"],
                ["**6 · Earn autonomy; record first, gate later**",
                 "every PR human-approved; the track record is recorded but not yet acted on",
                 "`compose.PR_LABELS`, `record_outcome`"],
                ["**7 · Grow by adding loops** — one loop until it closes",
                 "a single loop, end-to-end; `Ecosystem`/ports shaped so loop #2 is additive, not a fork",
                 "`ecosystem.py`, `ports/protocols.py`"],
            ],
            caption="Seven principles, seven pieces of code-level evidence. None "
                    "depends on taking the README's word for it."),
    ],
))

add(Section(
    id="illegal-states", act="Act X · Can I vouch for this?", num="10.2",
    title="The “unrepresentable” gallery",
    technique="Montage",
    blocks=[
        prose("""
The recurring promise of Act I was that *illegal states cannot be constructed*.
Collected in one place, here is the full arsenal froot uses to keep that promise —
each is a technique you saw in context, now visible as a pattern.
"""),
        table(
            ["Technique", "Forbids", "Seen in"],
            [
                ["`frozen=True, extra='forbid'` base", "mutation; unknown/typo'd fields", "`domain/base.py` §1.1"],
                ["`@model_validator` construction guard", "a `PatchCandidate` that isn't a clean patch", "`candidate.py` §1.4"],
                ["discriminated unions (`Literal kind`)", "an untagged/ambiguous variant; bad deserialization", "`changelog`, `ci`, `state`, `events`, `effects`"],
                ["subset type (`TerminalCIStatus`)", "recording an outcome against a *pending* CI", "`ci.py` + `outcome.py` §1.7"],
                ["`TypeIs` narrowing (`is_terminal`)", "treating a pending status as terminal in code", "`ci.py` §1.7"],
                ["`assert_never` on `match`", "forgetting a case when an enum/union grows", "`ecosystem`, `compose`, `state_machine`, `model_judge`"],
                ["state-carries-only-valid-data", "a PR with no verdict; an outcome before CI", "`state.py` §1.9"],
                ["REJECTED-not-raised transition", "an illegal event crashing the loop", "`state_machine.py` §2.4"],
                ["anchored field regex (`\\A..\\z`)", "a slug/branch with a smuggled slash or newline", "`repo.py`, `pull_request.py` §1.8"],
                ["`Result` at the boundary", "an unhandled parse failure escaping as an exception", "`result.py` §1.2"],
                ["`SecretStr`", "a token leaking into logs/`repr`/tracebacks", "`settings.py` §5.1"],
            ],
            caption="Eleven distinct ways froot makes a wrong state fail to compile, "
                    "fail to construct, or fail safely — the spine of its "
                    "trustworthiness."),
        callout("principle", """
**This is the answer to “why so few runtime guards?”** froot has remarkably few
defensive `if`s and `try`s in its business logic, because the work is done one
layer down — in the *types*. A reviewer doesn't have to trace whether some caller
forgot to validate; the value's type already carries the proof. That's what makes
3,000 lines auditable in an afternoon.
"""),
    ],
))

add(Section(
    id="replay-safety", act="Act X · Can I vouch for this?", num="10.3",
    title="The replay-safety contract",
    technique="Checklist",
    blocks=[
        prose("""
The other promise — that the Temporal workflows are deterministic and replay-safe —
is upheld by a small set of disciplines applied consistently across the spine.
Here they are as a checklist you can re-verify yourself by re-skimming Act VI.
"""),
        table(
            ["✓", "Discipline", "Mechanism"],
            [
                ["☑", "All I/O lives in activities, never workflows", "the six `@activity.defn` functions; workflows only call `execute_activity`"],
                ["☑", "No wall-clock or `asyncio.sleep` in a workflow", "`workflow.now()` and `workflow.sleep()` only (§6.4)"],
                ["☑", "Adapter stacks never enter the sandbox", "lazy `import` *inside* activity bodies (§6.5)"],
                ["☑", "Pure imports declared safe to the sandbox", "`with workflow.unsafe.imports_passed_through()` (§6.3–6.4)"],
                ["☑", "Bounded workflow history", "`continue_as_new` per scan tick (§6.3)"],
                ["☑", "Domain values survive the wire intact", "`pydantic_data_converter` + discriminators (§6.2)"],
                ["☑", "Permanent vs. transient faults distinguished", "`ApplicationError(non_retryable=True)` for misconfig/auth (§4.3, §6.4)"],
            ],
            caption="Seven disciplines. Each is checkable by eye, and the "
                    "time-skipping integration tests (§8.3) exercise the result "
                    "end-to-end."),
        callout("insight", """
**Determinism and testability are the same property here.** Every item above that
makes production replay-safe *also* makes the test server able to fast-forward time
and swap activities. You don't pay for durability with untestability — froot got
both from the one decision to keep the workflows pure and push all I/O outward.
"""),
    ],
))

add(Section(
    id="closing", act="Act X · Can I vouch for this?", num="10.4",
    title="What's deliberately absent — and what comes next",
    technique="Non-goals + roadmap",
    blocks=[
        prose("""
A codebase is as defined by what it refuses to do as by what it does. froot names
its non-goals explicitly, to stay KISS — each is deferred *on purpose*, not
forgotten.
"""),
        table(
            ["Deliberately NOT here", "Because"],
            [
                ["Auto-merge / earned autonomy", "record the track record first; act on it once it exists"],
                ["A reputation store", "derive it from GitHub + ClickStack when needed"],
                ["An agentic coding harness", "a mechanical loop doesn't need one — it arrives with the fixers"],
                ["Running tests/builds on the cluster", "CI does that; it's the oracle"],
                ["Multi-ecosystem beyond npm (+ uv next)", "add ecosystems as real loops demand them"],
                ["A cross-repo “loop platform” abstraction", "extract the shared chassis from the *second* loop, not a guess"],
            ],
            caption="The non-goals. Naming them is how froot avoids gold-plating "
                    "an unproven abstraction."),
        prose("""
And the staged path forward — each stage earning the next, never broadening one
loop before it closes:
"""),
        diagram("roadmap",
                 "The roadmap: close one loop, replicate it to prove it's a "
                 "template, let loops coordinate, and only then take on fixers that "
                 "write arbitrary code — decided on terrain that already works.",
                 klass="wide"),
        callout("principle", """
**So — can you vouch for it?** Walk back through what you can now assert from the
code itself, not the marketing: the loop genuinely closes (durable schedule →
bounded PR → CI oracle → recorded outcome → next tick); the model is on a tight,
typed, one-call leash; illegal states are unrepresentable by eleven distinct
mechanisms; the workflows are replay-safe by seven disciplines the tests exercise;
idempotency is structural at two layers; secrets are masked and dependency code
never runs in the worker. It is explicitly experimental and single-author-shaped —
the README says so first — but within that scope it is **coherent, honest about its
limits, and does exactly what it claims**. That's a thing you can stand behind.
"""),
        prose("""
> *froot is the chassis an army of loops grows on. You've just read the whole
> chassis — every line of it.*
"""),
        raw('<div style="height:40px"></div>'),
    ],
))


# === MORE SECTIONS INSERTED ABOVE THIS LINE ===
# Build with the CLI:  read-thru build content.py --source <workspace> --out froot.html
