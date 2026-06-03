"""froot learns Python — the uv ecosystem PR, the reviewer's cut.

A code-level walkthrough of the change that gives froot a second package
ecosystem: uv (Python), beside the existing npm. It covers the parts a reviewer
would insist on seeing — the prepared seam, the two verified uv facts, the
adapter's pure core, the version decision, the dispatch, the config and
changelog reach, the PR-body fix, and the proof. Prose is kept plain.
"""
from __future__ import annotations

from read_thru import Section, callout, code, diagram, prose, raw, table

TITLE = "froot — Python (uv) support, explained"
TOC_TITLE = "froot · the uv ecosystem PR"

SECTIONS: list[Section] = []


def add(s: Section) -> Section:
    SECTIONS.append(s)
    return s


def src(rel: str, **kw) -> str:
    kw.setdefault("title", rel)
    kw.setdefault("logical", rel)
    return code("projects/froot/" + rel, **kw)


# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="hero", act="froot · uv", num="·",
    title="froot learns Python", technique="",
    blocks=[raw("""
<div class="hero">
  <div class="hero-kicker">A code-level review of one PR · the uv (Python) ecosystem</div>
  <h1>froot learns Python</h1>
  <p class="tagline">A second package ecosystem, slotted into a seam that was cut for it.</p>
  <p class="lede prose">froot is a Temporal worker that runs dependency-patch
  loops against a repo and lets the repo's own CI verify each bump. It shipped
  speaking one ecosystem, npm. This PR teaches it a second, uv (Python). The
  interesting thing about the change is how little of it there is, and where the
  new lines are not. Expand any code block to read the surrounding context.</p>
  <div class="ownerkey">
    <span class="k k-terrain">🆕 added by this PR</span>
    <span class="k k-chassis">♻️ chassis · unchanged</span>
    <span class="k k-model">🐍 uv &amp; PyPI · external truth</span>
  </div>
  <div class="statbar">
    <div class="stat"><div class="num">2</div><div class="lbl">ecosystems (was 1)</div></div>
    <div class="stat"><div class="num">1</div><div class="lbl">new adapter</div></div>
    <div class="stat"><div class="num">0</div><div class="lbl">lines changed in the state machine &amp; workflows</div></div>
    <div class="stat"><div class="num">116</div><div class="lbl">tests green</div></div>
    <div class="stat"><div class="num">3</div><div class="lbl">review findings fixed</div></div>
  </div>
</div>
"""),
        prose("""
### What "Python support" actually meant

froot's dependency-patch loop is mostly chassis: a durable schedule, a checkout,
a wait on CI, the PR plumbing, the recorded outcome. Only three small things make
a loop ecosystem-specific. The signal (which versions exist), the lockfile command
(how to pin a bump), and the changelog source (where the release notes live).

So adding Python was never going to be a rewrite. It is a new adapter behind an
existing port, one new line in an enum, and one small dispatcher that picks the
adapter by ecosystem. Everything downstream of the adapter, the part that makes
froot durable, did not move.
"""),
        diagram("seam",
                 "The whole shape of the change. A new dispatcher picks a package "
                 "manager by ecosystem; the new uv adapter sits behind the same "
                 "Protocol the npm one already satisfied. The durable loop below "
                 "is untouched.", klass="wide"),
        prose("""
The tour follows the change from the inside out. We start at the seam that was
already prepared, settle the two uv facts the whole adapter rests on, read the
adapter's pure core, then walk out through dispatch, config, the changelog, the
PR body, and the proof.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="seam", act="The seam", num="1",
    title="The extension point was cut on day one",
    technique="The prepared seam",
    files=["src/froot/domain/ecosystem.py"],
    blocks=[
        prose("""
One module is built for exactly this. Its docstring states the extension contract
in plain words: a new ecosystem is one enum member plus one adapter, and the
`match` statements below "fail to type-check until it is [handled], which is the
point." That contract predates this PR. The npm-only version already ended each
match in `assert_never`, so adding uv was a guided edit rather than an open-ended
one.
"""),
        src("src/froot/domain/ecosystem.py", peek=[(1, 11), (19, 43)]),
        prose("""
The change is one enum member plus two new cases. `UV = "uv"` joins the enum, and
each `match` gains a `case Ecosystem.UV` returning `pyproject.toml` and `uv.lock`.
The `assert_never(ecosystem)` after each match is the part that made this edit
mandatory rather than optional.
"""),
        callout("principle", """
**Chassis generalizes, the loop specializes.** This is froot's central design
rule, and the enum is where you can see it hold. The per-ecosystem facts live in
one place and the adapter beside it. Adding an ecosystem cannot quietly skip a
spot, because every `match` over `Ecosystem` ends in `assert_never` and stops
compiling until the new case is handled. The compiler keeps the chassis honest.
"""),
        callout("counter", """
**Add the enum member, forget a case, and the file stops compiling.** With the
case gone, `assert_never(ecosystem)` is handed a `Literal[Ecosystem.UV]` where
`Never` is required, so mypy points at that line and names the member you left
unhandled. Strip the `assert_never` and the `-> str` return type still catches the
slip, only as a vaguer "missing return statement". The point of `assert_never` is
the precision: it tells you which ecosystem you forgot, at the line you forgot it.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="facts", act="The uv adapter", num="2",
    title="Two facts, verified not guessed",
    technique="Q&A from the source",
    files=["src/froot/adapters/uv.py", "src/froot/adapters/npm.py"],
    blocks=[
        prose("""
An adapter is only as good as its grip on the real tool. Two questions decide the
whole uv adapter, and both were answered against a live uv and a live PyPI before
a line was written.

#### Q1. How do you list a package's available versions?

The npm adapter shells out to `npm view <pkg> versions`. uv has no equivalent.
Its `pip` subcommands inspect an *installed* environment, and froot never installs
anything. So the version list comes from the PyPI JSON API, which is the registry
query that plays the role `npm view` plays for npm.
"""),
        callout("insight", """
**Why a registry call, not the package manager.** froot's worker carries package
managers, not test toolchains, and it reads availability without installing. npm
happens to expose a registry query through its CLI; uv does not, so the adapter
talks to the registry directly. Same job, same blast radius (a read), different
door.
"""),
        prose("""
#### Q2. How do you pin a bump without running anything?

The npm adapter rewrites the lockfile with `--package-lock-only --ignore-scripts`.
The uv equivalent is one command, and its precise behavior is the hinge the whole
design hangs on.
"""),
        src("src/froot/adapters/uv.py", peek=[(239, 251)],
            note="The bump action, in full. Compare npm's `apply_patch_bump` below."),
        src("src/froot/adapters/npm.py", peek=[(149, 162)]),
        callout("trace", """
**Verified live before trusting it.** Running `uv lock --upgrade-package
'click==8.1.8'` on a throwaway project moved the locked version from 8.1.7 to
8.1.8 and left `pyproject.toml` byte-for-byte unchanged. That is exactly froot's
model: propose one patch, pin the lockfile to it, touch nothing the human did not
ask to change. CI then runs `uv sync --frozen` against the manifest and the new
lock, which still agree, so CI stays the oracle.
"""),
        prose("""
The two facts also draw the adapter's scope. Because `uv lock` edits only the
lock, a dependency that someone pinned exactly in `pyproject.toml` (`pkg==1.2.3`)
cannot be patched lockfile-only; uv errors, and `apply_patch_bump` raises rather
than papering over it. That is the right failure: loud, and at the one bump it
affects.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="adapter", act="The uv adapter", num="3",
    title="Pure parsers, a thin shell",
    technique="Spotlight the testable core",
    files=["src/froot/adapters/uv.py"],
    blocks=[
        prose("""
The adapter follows the same split as npm: a few pure functions that parse text,
wrapped in two thin methods that do the I/O. The parsers are where the care is,
because they run with no network and are unit-tested with fixtures. Three of them
turn the three inputs into facts.
"""),
        diagram("uv-pipeline",
                 "The adapter gathers three facts — direct names, current "
                 "versions, available versions — into raw AvailableUpgrades. The "
                 "shared pure policy picks the patch; the adapter pins it.",
                 klass="wide"),
        prose("""
#### Names that agree across two files

`pyproject.toml` writes a dependency as `Pydantic-Settings`; `uv.lock` writes it
as `pydantic-settings`. If the two never line up, every lookup misses. One
function settles it for both sides.
"""),
        src("src/froot/adapters/uv.py", peek=[(66, 74)]),
        prose("""
`normalize_name` applies the PEP 503 rule: lowercase, and collapse runs of `.`,
`-`, `_` to a single `-`. The direct-dependency set and the locked-version map are
both keyed through it, so a name declared one way and locked another still matches.

#### Direct dependencies, across three sections

A `pyproject.toml` can declare dependencies in three places, and froot reads all
of them: the main list, every optional-dependency group, and PEP 735 dependency
groups (where uv keeps its dev tools).
"""),
        src("src/froot/adapters/uv.py", peek=[(92, 117)]),
        callout("note", """
**Only direct dependencies, and only strings.** A requirement string is reduced
to its leading distribution name, so extras, version specifiers, and environment
markers fall away. Dependency groups can also hold `{include-group = ...}` tables;
those are skipped, because the group they point at is read on its own pass.
Transitive dependencies are never bumped — promoting one to direct is not a patch.
"""),
        prose("""
#### Available versions, with yanked releases dropped

The PyPI body lists every release. Two kinds are filtered before parsing: a
release that ships no files, and one whose files are all yanked. A yanked patch is
one PyPI is asking you not to install, so froot never proposes it.
"""),
        src("src/froot/adapters/uv.py", peek=[(146, 182)]),
        prose("""
The two methods on the class are deliberately thin. `list_upgrades` reads the
manifest and lock, then asks PyPI for each direct dependency, returning raw
`AvailableUpgrade`s. It does not decide anything; choosing the patch is the
shared pure policy's job, the same one npm feeds.
"""),
        src("src/froot/adapters/uv.py", peek=[(203, 237)]),
        table(
            ["Concern", "npm adapter", "uv adapter"],
            [
                ["direct deps", "`package.json` deps + devDeps", "`pyproject.toml` PEP 621 + PEP 735"],
                ["current version", "`package-lock.json`", "`uv.lock` `[[package]]`"],
                ["available versions", "`npm view <pkg> versions`", "PyPI JSON API"],
                ["pin the bump", "`npm install --package-lock-only --ignore-scripts`", "`uv lock --upgrade-package pkg==target`"],
                ["who picks the target", "`select_patch_candidates` (shared)", "`select_patch_candidates` (shared)"],
            ],
            caption="The adapters are the same shape. Only the three loop-specific "
                    "facts differ; the patch-selection policy is identical and "
                    "unchanged."),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="versions", act="The uv adapter", num="4",
    title="Reuse semver, drop the rest",
    technique="The decision and its evidence",
    files=["src/froot/domain/version.py", "src/froot/adapters/uv.py"],
    blocks=[
        prose("""
Here is the one genuine judgement call in the change. froot's `Version` is strict
three-part semver. Python versions are PEP 440, which is wider: epochs like
`1!2.0`, two- or four-segment releases, post and dev releases, prereleases with no
hyphen. The adapter does not teach `Version` PEP 440. It reuses semver as-is and
lets anything that does not fit fall out.
"""),
        src("src/froot/domain/version.py", peek=[(92, 112)]),
        prose("""
`is_patch_bump_of` is the relation the whole loop turns on, and it is unchanged.
A clean patch keeps the major and minor, raises the patch, and is stable on both
ends. A PEP 440 oddity does not parse into a `Version` at all, so it never reaches
this test. The funnel below is the result.
"""),
        diagram("versions",
                 "Every published version runs the same gauntlet. Non-semver forms "
                 "are dropped at parse time; only a clean, stable, higher patch of "
                 "the current version becomes a target.", klass="wide"),
        callout("principle", """
**Conservative on purpose: fewer bumps, never a wrong one.** Dropping a version
froot cannot confidently classify means froot proposes nothing for that
dependency that cycle. It never means froot proposes the wrong thing. The common
case, `X.Y.Z` to `X.Y.(Z+1)`, is exactly what semver parses cleanly, and that is
the case the loop exists to handle. Full PEP 440 is future work, to be added when
a real loop needs it, not on a guess.
"""),
        callout("trace", """
**The drop is real, and you can watch it.** Pointing the finished adapter at
froot's own `pyproject.toml` queried 13 of its 14 direct dependencies against
PyPI. The fourteenth, `opentelemetry-instrumentation-httpx`, was skipped. Its
locked version is `0.63b1`, a two-segment PEP 440 beta that is not semver, so
froot passes on it rather than guess what a patch of `0.63b1` would be.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="dispatch", act="Wiring it in", num="5",
    title="One place to choose an adapter",
    technique="Counterfactual",
    files=["src/froot/adapters/registry.py", "src/froot/workflow/activities.py"],
    blocks=[
        prose("""
Before this PR, two activities built `NpmPackageManager()` by hand. A second
ecosystem makes that wrong, because the choice now has to follow the target's
ecosystem. So it moves out of the activities and into one small function.
"""),
        src("src/froot/adapters/registry.py", peek=[(22, 33)]),
        callout("insight", """
**Lazy imports, and `assert_never` again.** The concrete adapter is imported
*inside* its `match` arm, not at module top. Resolving npm never imports uv's HTTP
stack, so neither adapter is dragged into the Temporal workflow sandbox; the
activities already follow that lazy-import rule. The match also ends in
`assert_never`. A third ecosystem will fail to type-check right here until it is
wired in, which leaves exactly one place to add the next one.
"""),
        prose("""
The activities then ask the registry for the right manager instead of naming one.
It is two lines each, in `scan_candidates` and `open_pull_request`.
"""),
        src("src/froot/workflow/activities.py", peek=[(47, 52), (76, 81)]),
        callout("counter", """
**Why a registry, not an `if` in each activity.** Two activities pick a package
manager. Inline the choice and you keep two `match` statements in sync, and you
get to forget the second one some day. Centralize it instead. Now one function
owns the mapping, one `assert_never` guards it, and each activity simply asks for
the manager for its target with no ecosystem knowledge of its own.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="reach", act="Reaching the loop", num="6",
    title="Config in, changelog out",
    technique="Trace + a gotcha the review caught",
    files=["src/froot/config/settings.py",
           "src/froot/adapters/changelog_http.py"],
    blocks=[
        prose("""
Two edges of the loop still spoke only npm: how you point froot at a Python repo,
and where it finds a Python package's changelog. Both are small, and one hid a
trap.

#### Pointing froot at a uv repo

Targets come from `FROOT_REPOS`, a comma-separated list of `owner/name` slugs. A
slug now takes an optional `@<ecosystem>` suffix. No suffix still means npm, so
every existing config keeps working.
"""),
        src("src/froot/config/settings.py", peek=[(48, 75)]),
        prose("""
#### Finding a Python changelog

For npm, froot reads the registry's `repository.url`. For uv, it reads PyPI's
`project_urls` and `home_page`, prefers a labelled source link over a homepage,
and from there the GitHub release-notes fetch is shared with npm. Both ecosystems
tag releases on GitHub the same way, so only the repo *discovery* differs.
"""),
        src("src/froot/adapters/changelog_http.py", peek=[(88, 113)]),
        callout("gotcha", """
**The funding-link trap, found in adversarial review.** A common PyPI label is
"GitHub Sponsors", pointing at `github.com/sponsors/<org>`. The first draft sorted
any label containing "github" to the front and matched that URL as the repo
`sponsors/<org>` — which 404s, suppressing the *real* changelog that sat one link
away. The fix is a reserved-owner guard: `sponsors`, `orgs`, `users` and the like
are GitHub namespaces, never repositories, so a URL under them yields no repo. The
over-broad "github" hint was dropped too, leaving only source-role words.
"""),
        src("src/froot/adapters/changelog_http.py", peek=[(44, 76)]),
        callout("note", """
**This path fails safe.** Every step here is best-effort. A missed or
mis-resolved repo returns `None`, which the judge reads as "changelog
unavailable" and frames for the human without a model call. The worst case is a
bump proposed with no release notes attached, never a bump attributed to the
wrong package's notes.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="prbody", act="Reaching the loop", num="7",
    title="The PR body has to match the diff",
    technique="The bug the review caught",
    files=["src/froot/policy/compose.py"],
    blocks=[
        prose("""
froot never merges. A human approves every pull request, which makes the body part
of the safety surface rather than decoration. The body carries one line that says
what the bump changed, and for uv the first draft of this PR got that line wrong.
"""),
        prose("""
npm rewrites both files. `npm install --package-lock-only` updates the dependency
spec in `package.json` and regenerates `package-lock.json`. uv rewrites only
`uv.lock`. The original template always named the manifest, so a uv PR told the
reviewer that `pyproject.toml` changed while the diff held only `uv.lock`. A
reviewer who trusted the body would hunt for a hunk that was not there.
"""),
        src("src/froot/policy/compose.py", peek=[(39, 56)]),
        prose("""
`_changed_files` now branches by ecosystem, so the sentence the human reads
matches the files the human sees. npm keeps "manifest + lockfile". uv reads
"uv.lock only; pyproject.toml unchanged". The body is built straight from it.
"""),
        src("src/froot/policy/compose.py", peek=[(87, 97)]),
        callout("insight", """
**The spine was already neutral; one template was not.** Look at what did not
change: the state machine, both workflows, the branch and workflow-id naming, the
CI wait, the recorded outcome. All of it was ecosystem-agnostic already. This
PR-body phrase was the lone place that had quietly inherited npm's "the manifest
changes too" habit. A `match` with `assert_never` guards it now, so the next
ecosystem has to say what its bump touches.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="proof", act="How it's proven", num="8",
    title="Fixtures for the pure parts, reality for the rest",
    technique="Evidence",
    files=["tests/test_uv_adapter.py"],
    blocks=[
        prose("""
The adapter is tested the way npm's is. The pure parsers get fixture tests with no
network; the I/O methods are exercised through the activities over in-memory
fakes. That keeps the suite fast and deterministic, and it is why the parsers were
written as free functions in the first place.
"""),
        src("tests/test_uv_adapter.py", peek=[(77, 91)]),
        prose("""
This one test pins the filtering rules in place: a clean release is kept, a
missing `yanked` key counts as not yanked, the prerelease `1.3.0rc1` is dropped as
non-semver, a fully yanked release and one with no files are dropped, and an
unparseable string is ignored. The dispatcher gets its own check that each
ecosystem returns its own manager.
"""),
        callout("trace", """
**Then it was run against the real world, twice.** First, `list_upgrades` was
pointed at froot's own `pyproject.toml` and `uv.lock`: it parsed all 14 direct
dependencies, queried 13 against the live PyPI (skipping the PEP 440 one), and the
shared policy proposed zero patches — correct, because froot's own deps are
already current. Second, `apply_patch_bump` ran a real `uv lock` bump of `click`
from 8.1.7 to 8.1.8 and left `pyproject.toml` untouched. Fixtures prove the logic;
the live runs prove the grip on uv and PyPI.
"""),
        table(
            ["What", "How it is checked"],
            [
                ["PEP 503 normalization, PEP 621/735 parsing, uv.lock parsing", "fixture unit tests"],
                ["PyPI filtering (yanked, fileless, non-semver)", "fixture unit test"],
                ["ecosystem → adapter dispatch", "`test_package_manager_for_dispatch`"],
                ["activities pick the adapter by `target.ecosystem`", "activity test over fakes"],
                ["`@<ecosystem>` config parsing, unknown rejected", "settings tests"],
                ["uv PR body says uv.lock only", "compose test"],
                ["repo discovery, sponsors guard, fragment URLs", "changelog tests"],
                ["the real uv + PyPI grip", "two live smoke runs"],
            ],
            caption="The whole change, and where each claim is backed. 116 tests "
                    "pass; ruff and strict mypy are clean."),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="verdict", act="The verdict", num="9",
    title="Did the seam hold?",
    technique="Evidence table + what did not change",
    blocks=[
        prose("""
The claim this PR makes is that a second ecosystem is one adapter, one enum
member, and one dispatcher, with the durable machinery untouched. Below, that
claim is scored against the actual change, with the file that proves each row.
"""),
        table(
            ["Claim", "Upheld by", "Where"],
            [
                ["**A new ecosystem is one adapter behind the existing port**", "`UvPackageManager` satisfies `PackageManager` structurally; the spine names only the protocol", "`adapters/uv.py`, `ports/protocols.py`"],
                ["**The seam was prepared, and the compiler enforces it**", "`assert_never` on every `Ecosystem` match; one enum member added", "`domain/ecosystem.py`"],
                ["**Patch selection is shared, not reimplemented**", "both adapters feed the same `select_patch_candidates`", "`policy/candidates.py` (unchanged)"],
                ["**The bump runs no third-party code in the worker**", "`uv lock --upgrade-package`, lockfile-only; CI does the install", "`adapters/uv.py`, `Dockerfile`"],
                ["**Conservative versions: never a wrong bump**", "non-semver versions dropped at parse; the live skip of `0.63b1`", "`adapters/uv.py`, `domain/version.py`"],
                ["**The human approver is told the truth**", "`_changed_files` matches the body to the diff per ecosystem", "`policy/compose.py`"],
            ],
            caption="Six claims, six pieces of code-level evidence."),
        callout("principle", """
**The strongest evidence is the empty diff.** The state machine, both workflows,
the CI lattice, the durable wait, the outcome record, the branch and
workflow-id naming — none of them changed. A reviewer can confirm that by
absence. If a new ecosystem had forced edits into the durable core, the "chassis
generalizes, the loop specializes" claim would be marketing. It did not, so the
claim is load-bearing.
"""),
        prose("""
Two findings from the adversarial review are folded in above: the PR-body mismatch
(§7) and the funding-link trap (§6). A third, a URL with a `#fragment` losing the
repo, was a pre-existing shared-code nit and was tightened in the same pass. All
three came with regression tests. So, from the code: the change is additive, the
new logic is conservative and tested, the one place that had assumed npm now
states its ecosystem, and the durable loop that makes froot worth running is
exactly as it was.
"""),
        raw('<div style="height:40px"></div>'),
    ],
))

# Build with the CLI:
#   read-thru build content.py --source <workspace> --out froot-uv-pr.html \
#       --svg-dir examples/froot-uv-pr/svg
