"""froot — the essential reading (the most representative ~25%).

A reviewer's tour: the architecture, the load-bearing invariants, the loop
logic, the seam, the safety-critical adapter code, the one model call, the
durable spine, secret handling, the cleverest test, the deploy, and the verdict.
Prose is kept deliberately plain. Build with the doc venv's python.
"""
from __future__ import annotations

from gen import Section, build, callout, code, diagram, prose, raw, table

SECTIONS: list[Section] = []


def add(s: Section) -> Section:
    SECTIONS.append(s)
    return s


def src(rel: str, **kw) -> str:
    kw.setdefault("title", rel)
    kw.setdefault("logical", rel)
    return code("projects/froot/" + rel, **kw)


def infra(rel: str, **kw) -> str:
    full = "infra/k8s/froot/" + rel
    kw.setdefault("title", full)
    kw.setdefault("logical", full)
    return code(full, **kw)


# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="hero", act="froot", num="·",
    title="froot, the essential reading", technique="",
    blocks=[raw("""
<div class="hero">
  <div class="hero-kicker">A code-level review · the essential 25%</div>
  <h1>froot</h1>
  <p class="tagline">Durable maintenance loops, pointed at any repo.</p>
  <p class="lede prose">This is the reviewer's cut. It keeps the parts of the
  codebase you would insist on seeing before vouching for it, and leaves the
  exhaustive line-by-line walk to the full edition. Expand any code block to read
  more around a snippet.</p>
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
### What froot is

froot runs autonomous code-maintenance loops on Temporal and points them at
GitHub repositories. A loop watches a repo for one kind of decay. It proposes a
bounded fix as a pull request, lets the repo's own CI verify the change, and
records the outcome. A human approves every merge.

The first loop keeps npm dependencies patched. froot is not that loop. It is the
chassis the loop runs on: one durable substrate, many specialized loops, any
number of repos. Almost everything in the codebase is chassis. The loop-specific
parts are small on purpose.
"""),
        callout("principle", """
**Why it sits on Temporal.** A loop needs six ingredients: a signal, a bounded
action, verification, reversibility, a trace it leaves behind, and a rule for
when its autonomy grows. The maintenance scripts froot grew from had the first
four. The last two need state that survives across runs. Durability is what lets
the loop close, so the loop lives on a durable workflow engine.
"""),
        diagram("loop",
                 "The dependency-patch loop. Nodes are colored by who owns each "
                 "step. The dashed edge is the loop closing: each outcome decays "
                 "into the next tick's signal.", klass="wide"),
        prose("""
The tour goes from the center out. We start with the pure types, move through
the loop logic and the seam to the outside world, then reach the durable spine
and the deployment. That is the direction the dependencies point.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="architecture", act="Orientation", num="1",
    title="The shape of the whole thing", technique="Map + table",
    files=["src/froot/__init__.py"],
    blocks=[
        prose("""
froot is a functional core wrapped in an imperative shell. The rule is one line:
imports point only inward. At the center, the pure core never imports Temporal,
npm, a GitHub client, or httpx, which keeps every business rule sealed off from
the machinery that runs it. The shell at the edge depends on all of them. It owns
no logic.
"""),
        diagram("architecture",
                 "Dependencies point inward. The pure core has no I/O and no "
                 "framework. The shell implements the ports and interprets the "
                 "core's effects. The seam is four typed Protocols."),
        table(
            ["Layer", "Modules", "Lines", "Its one job"],
            [
                ["🧊 domain", "`version` · `candidate` · `ci` · `state` · `events` · `effects` · `outcome` · …", "727", "frozen value objects; illegal states cannot be built"],
                ["🧮 policy", "`candidates` · `naming` · `compose` · `state_machine`", "363", "pure decisions: selection, idempotency keys, PR text, the loop's transitions"],
                ["📜 ports", "`protocols.py`", "114", "four `Protocol`s; the seam to the impure world"],
                ["🔌 adapters", "`npm` · `github` · `model_judge` · `changelog_http` · `telemetry` · …", "845", "real integrations: npm, git, GitHub, the model, OTEL"],
                ["⚙️ workflow", "`scan_workflow` · `bump_workflow` · `activities` · …", "521", "the durable Temporal spine: two workflows, six activities"],
                ["🚀 entry / config", "`worker` · `scan_starter` · `settings`", "284", "the runnable worker, the go-live trigger, all env config"],
            ],
            caption="The source tree by layer. The acts below follow these layers "
                    "from the inside out."),
        callout("why", """
**What this shape buys.** Start with testability. The core runs against in-memory
fakes, so no test needs npm, git, or a live GitHub. Replay-safety then comes for
free, because a pure core with all I/O pushed into activities is deterministic,
which is exactly what a Temporal workflow has to be. The last payoff is the
chassis/loop seam. A new loop changes three small pieces of config and reuses
everything else. It is never a fork of the engine.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="unrepresentable", act="The pure core", num="2",
    title="Illegal states you cannot build",
    technique="Three proofs",
    files=["src/froot/domain/version.py", "src/froot/domain/candidate.py",
           "src/froot/domain/ci.py"],
    blocks=[
        prose("""
The domain is a dozen modules of frozen, closed value objects. The governing
idea is that the states the loop must never reach cannot be constructed at all.
That is a strong claim, so here are three proofs a reviewer can check directly.

#### Proof one: a patch bump has a precise definition

The loop's signal is "a higher patch of a dependency exists." Everything turns on
what counts as a patch. One method defines it.
"""),
        src("src/froot/domain/version.py", peek=[(92, 112)]),
        prose("""
A version is a clean patch bump of another only when both are stable, the major
and minor match, and the patch strictly increases. Each clause closes one way a
"bump" could smuggle in risk: a prerelease, a minor change, a downgrade.

#### Proof two: a candidate enforces that definition at construction

`PatchCandidate` is the loop's unit of work. Its one invariant runs in a
validator, so a candidate that is not a clean patch bump simply cannot exist.
"""),
        src("src/froot/domain/candidate.py", peek=[(38, 46)]),
        callout("counter", """
**Delete those eight lines and the cost spreads everywhere.** Without the
validator, `PatchCandidate(..., 1.4.2, 2.0.0)` becomes constructible, and every
consumer downstream has to re-check it or risk opening a major-version "patch."
Today they trust the candidate because the type guarantees it. The invariant is
what lets the other 2,900 lines stop worrying.
"""),
        prose("""
#### Proof three: a pending CI is not assignable as an outcome

CI is froot's verification, and froot never re-runs a repo's tests. The risk is
that a still-running check gets mistaken for a verdict. The type system rules it
out. There are two unions, and the relationship between them is the point.
"""),
        diagram("ci-lattice",
                 "Five readings, but only four are terminal. `TerminalCIStatus` "
                 "is a strict subset of `CIStatus`, and the recorded outcome is "
                 "typed to the subset.", klass="wide"),
        src("src/froot/domain/ci.py", peek=[(52, 68)]),
        callout("insight", """
**`is_terminal` returns `TypeIs`, not `bool`.** So when the workflow writes
`if is_terminal(status): return status`, the type checker narrows `status` to the
terminal subset inside that branch. Because `LoopOutcome.ci` is typed
`TerminalCIStatus`, a pending reading is not even assignable as an outcome. The
"never record a half-finished CI" rule is checked by the compiler, not a runtime
assert.
"""),
        callout("note", """
This is the pattern, repeated across the domain: frozen and closed base models,
construction-time validators, discriminated unions, subset types, and
`assert_never` on every `match`. The §12 gallery collects all of them.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="state-machine", act="The pure core", num="3",
    title="The loop as a pure function",
    technique="State diagram + trace",
    files=["src/froot/policy/state_machine.py",
           "src/froot/domain/effects.py"],
    blocks=[
        prose("""
The loop's every move is decided here, by a pure function the Temporal spine only
drives. `advance` takes the current state and a decided event and returns a
`Transition`: the next state plus the effects the spine should run. There is no
I/O and no clock, so a transition replays deterministically and tests in
microseconds.
"""),
        diagram("state-machine",
                 "The bump lifecycle. Solid edges advance and emit one effect. "
                 "The self-loop is a still-pending CI being rejected so the spine "
                 "keeps waiting. The terminal acknowledgement is a no-op.",
                 klass="wide"),
        src("src/froot/policy/state_machine.py", peek=[(94, 113), (144, 159)]),
        prose("""
`advance` matches on the state, delegates to a per-state helper, and ends in
`assert_never`, so the checker proves every state is handled. Look at
`_from_awaiting_ci`. A `CiResolved` that is still pending returns a *rejected*
transition: the state does not change and nothing is raised. That is how the
"you cannot record an unresolved CI" rule reads in the pure layer. The machine
refuses to move, and the spine keeps polling.
"""),
        table(
            ["State", "Expected event", "Next state", "Effect emitted"],
            [
                ["`Discovered`", "`ChangelogJudged`", "`Judged`", "`OpenPullRequest`"],
                ["`Judged`", "`PullRequestReady`", "`AwaitingCi`", "`AwaitCi`"],
                ["`AwaitingCi`", "`CiResolved` (terminal)", "`Recorded`", "`RecordOutcome`"],
                ["`AwaitingCi`", "`CiResolved` (pending)", "*unchanged*", "**rejected**, no raise"],
                ["any", "any other event", "*unchanged*", "**rejected**, no raise"],
            ],
            caption="The whole transition table. Every legal path advances and "
                    "emits one effect. Everything else is a quiet rejection."),
        callout("principle", """
**Effects are data, and that is why the loop is testable.** A transition returns
values: the next state and an `Effect` that *names* what to do (judge, open a PR,
wait on CI, record) without doing it. So you can assert the entire decision flow
with no npm, GitHub, Temporal, or model in the test. The spine in §8 is little
more than a `while transition.effects:` loop around this function.
"""),
        src("src/froot/domain/effects.py", peek=[(24, 51)]),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="ports", act="The seam", num="4",
    title="Four typed promises", technique="Hexagon + table",
    files=["src/froot/ports/protocols.py"],
    blocks=[
        prose("""
This is the membrane. Inward of here everything is pure. Outward, everything is
I/O. The membrane itself is four `Protocol`s. The spine depends only on these,
never on a concrete client.
"""),
        diagram("hexagon",
                 "The spine talks to four Protocols. Production wires real "
                 "adapters behind them; tests wire in-memory fakes. Neither side "
                 "imports the other.", klass="wide"),
        src("src/froot/ports/protocols.py", peek=[(28, 51)]),
        table(
            ["Port", "Real adapter", "Fake (tests)"],
            [
                ["`PackageManager` — read upgrades, regen the lockfile", "`NpmPackageManager`", "`FakePackageManager`"],
                ["`Forge` — checkout, PR, CI status, labels", "`GitHubForge`", "`FakeForge`"],
                ["`ChangelogSource` — fetch release notes", "`HttpChangelogSource`", "`FakeChangelogSource`"],
                ["`ModelJudge` — judge a changelog", "`PydanticAiJudge`", "`FakeJudge`"],
            ],
            caption="Four ports, each with a real implementation and an in-memory "
                    "fake. The spine names only the left column."),
        callout("why", """
**Structural typing keeps the sides apart.** An adapter satisfies a port by shape,
not by inheritance, so it imports nothing from the port definition. That is what
lets the activities import an adapter lazily inside their bodies (§8) without
dragging a class hierarchy into the Temporal workflow sandbox. The fakes satisfy
the same shapes, so the whole loop runs in memory in the tests.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="adapters", act="The impure shell", num="5",
    title="Where the I/O lives, and where the safety is",
    technique="The two adapters that matter",
    files=["src/froot/adapters/npm.py", "src/froot/adapters/github.py"],
    blocks=[
        prose("""
The shell is seven modules of subprocess, git, HTTP, and a model. Two of them
carry froot's safety guarantees, so those are the two to read. The pure cores of
each (parsing npm output, mapping GitHub checks to a status) are module-level
functions, unit-tested with no network.

#### npm: regenerate the lockfile, run no code

The bump's action is a manifest and lockfile edit. One line makes it safe.
"""),
        src("src/froot/adapters/npm.py", peek=[(149, 162)]),
        callout("security", """
**The blast radius is tiny by construction.** `apply_patch_bump` runs
`npm install <pkg>@<target> --package-lock-only --ignore-scripts`. The first flag
rewrites the dependency tree without installing `node_modules`. The second means
no third-party install script ever runs inside the privileged, token-bearing
worker. The real install and the full test run happen later, in the target repo's
CI, which is already a sandbox. The worker carries package managers. It does not
carry test toolchains.
"""),
        prose("""
#### GitHub: read the oracle, open idempotently, fail safe on auth

The CI reading is a pure function over typed check rows, so it tests apart from
the network.
"""),
        src("src/froot/adapters/github.py", peek=[(69, 96)]),
        table(
            ["check runs", "combined status", "result"],
            [
                ["none", "none", "`CIAbsent` (nothing to verify)"],
                ["any not completed", "—", "`CIPending` (keep waiting)"],
                ["any bad conclusion", "—", "`CIFailed` (with failing names)"],
                ["all completed and good", "`success` / none", "`CIPassed`"],
            ],
            caption="The CI mapping unifies the modern Checks API with the legacy "
                    "combined status. Bad conclusions include failure, timed_out, "
                    "cancelled, action_required, startup_failure, stale."),
        callout("security", """
**Three more details a reviewer checks.** Opening a PR is idempotent. A 422
(the branch already has a PR) makes the adapter re-find and return the existing
one, and the activity checks for an existing PR before any checkout. A missing
token, or a 401 or 403, raises a *non-retryable* `ApplicationError`, so a
misconfiguration fails fast rather than retrying forever. One more. The subprocess
helper scrubs any `user:pass@` userinfo from captured output, so the token in the
git remote never reaches an error message or the workflow history.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="model", act="The impure shell", num="6",
    title="The one model call", technique="Spine-heavy, model-thin",
    files=["src/froot/adapters/model_judge.py"],
    blocks=[
        prose("""
Here is froot's entire use of an LLM. The deterministic spine decides when and
whether to act. The model answers one typed question: does this patch's changelog
read clean, or does it hint at hidden behavior change? Even that answer only
frames the PR for the human. It never gates the bump.
"""),
        src("src/froot/adapters/model_judge.py", peek=[(31, 43), (54, 66)]),
        prose("""
The agent's output type is a small Pydantic model, so Pydantic AI constrains the
model to return that exact shape. The pure `assessment_to_verdict` then maps it
to a domain verdict and ends in `assert_never`, so a fourth verdict kind would
fail to type-check until handled. The model is injected, so the test runs it
offline with a `TestModel`.
"""),
        callout("insight", """
**Read the system prompt.** It tells the model the bot proposes the bump either
way, and its job is only to frame the risk for the reviewer. It asks for clean,
risky, or unknown, and adds a rule: base "risky" concerns on what the text
actually says, do not speculate. The model is a triage aid on a tight, typed
leash, consulted once per bump, and only when a real changelog exists.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="spine", act="The durable spine", num="7",
    title="Driving the pure machine, durably",
    technique="Sequence + the durable wait",
    files=["src/froot/workflow/bump_workflow.py",
           "src/froot/workflow/scan_workflow.py"],
    blocks=[
        prose("""
This is why froot is on Temporal. The spine is thin, because the logic already
lives in the pure core. What the spine adds is durability: a self-triggering
schedule, a CI wait that survives an hour without holding a process open, and a
recorded outcome. The workflows use only pure state and Temporal's own APIs, so
they replay deterministically.

#### The bump workflow: a loop around the state machine
"""),
        diagram("bump-sequence",
                 "One bump. Each pure effect becomes an activity call whose result "
                 "becomes the next event fed back to advance(). The AwaitCi effect "
                 "expands into the durable poll-and-sleep loop.", klass="wide"),
        src("src/froot/workflow/bump_workflow.py", peek=[(63, 88), (123, 138)]),
        callout("insight", """
**Time comes from Temporal, not Python.** `_await_ci` reads `workflow.now()` and
sleeps with `workflow.sleep()`, never the wall clock or `asyncio.sleep`. Those
calls are replay-deterministic: on replay Temporal returns the recorded time and
fast-forwards the sleeps. That is what makes the hour-long wait free in
production, and what lets the test server fast-forward it to milliseconds (§9).
The `run` loop also guards its own invariants with non-retryable errors, since a
rejected or non-linear transition is a bug, not a transient fault.
"""),
        prose("""
#### The scan workflow: a self-rescheduling timer

One long-lived workflow per repo. Each tick scans, dispatches a bump loop per
candidate, sleeps, and restarts.
"""),
        src("src/froot/workflow/scan_workflow.py", peek=[(31, 56)]),
        callout("counter", """
**`continue_as_new`, not `while True`.** A plain infinite loop would grow the
workflow's event history without bound until replay degrades. `continue_as_new`
restarts the workflow with fresh parameters and an empty history, bounded to one
tick. It also raises, so nothing after it runs. There is no stored seen-set: each
tick re-derives the outstanding work from the repo, and the deterministic per-bump
workflow id makes re-dispatching an already-handled bump a no-op. froot keeps the
loop's memory in GitHub and Temporal, not in a database of its own.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="settings", act="Configuration", num="8",
    title="All the knobs, none of the secrets",
    technique="Secret handling",
    files=["src/froot/config/settings.py"],
    blocks=[
        prose("""
Every difference between a laptop and the cluster is one of five frozen
settings models, each reading a small slice of the environment. Nothing secret
lives in the repo. The token gets special handling.
"""),
        src("src/froot/config/settings.py", peek=[(84, 97)]),
        callout("security", """
**The token is a `SecretStr`.** It is masked in `repr`, logs, and tracebacks, so
printing the settings object or letting it into an exception shows `**********`.
The real value is reachable only through one `get_secret_value()` call, inside a
`_token()` helper, whose result feeds the two sinks that actually send it: the
auth remote URL and the API header. A test asserts the token cannot leak into
`repr`.
"""),
        prose("""
Two more touches: `FROOT_REPOS` is read as a comma-separated list of `owner/name`
slugs rather than JSON, each parsed through a boundary parser that raises on a bad
slug. And the settings models are frozen, so config is read once and cannot mutate
mid-run.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="tests", act="How it's proven", num="9",
    title="An hour-long wait, tested in milliseconds",
    technique="The cleverest test",
    files=["tests/test_bump_workflow.py"],
    blocks=[
        prose("""
Because the core is pure and the seams are ports, the suite is a clean pyramid: a
broad base of pure-unit and property tests, a middle of activities over fakes,
and a thin top of real-spine integration tests. The top tier is the interesting
one. It runs the actual workflows, with only the activities mocked, and it does
not wait real time.
"""),
        callout("note", """
**How do you test a workflow that waits up to an hour on CI? You skip the wait.**
`WorkflowEnvironment.start_time_skipping()` gives a Temporal test server that
fast-forwards workflow timers. When the bump workflow sleeps a minute between CI
polls, the server advances its virtual clock at once. A scenario of "pending,
pending, then pass," or "100 pendings until the deadline, then timeout," finishes
in milliseconds while running the genuine durable-wait code path.
"""),
        src("tests/test_bump_workflow.py", peek=[(44, 62), (95, 123)]),
        prose("""
A scripted `_ci_replies` queue drives each scenario. The four tests cover the
loop's four terminal shapes: green, red, pending-then-green, and timeout. The same
property that makes the production wait free, time read only through Temporal's
API, is what lets the test server lie about the clock without the workflow
noticing.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="deploy", act="Build &amp; deploy", num="10",
    title="The gate, the image, and one worker pointed outward",
    technique="Walkthrough + topology",
    files=["pyproject.toml", "Dockerfile",
           "infra/k8s/froot/manifests/10-worker.yaml"],
    blocks=[
        prose("""
The type guarantees in §2 are only real if a checker enforces them. `pyproject`
turns the screws: strict mypy with the Pydantic plugin, plus a ruff config that
knows the one trap.
"""),
        code("projects/froot/pyproject.toml", title="pyproject.toml",
             logical="pyproject.toml", peek=[(56, 75), (122, 137)]),
        callout("gotcha", """
**The subtlest config in the repo.** Ruff normally wants type-only imports moved
into an `if TYPE_CHECKING` block. But Pydantic evaluates field annotations at
runtime to build validators, and Temporal resolves workflow and activity type
hints at runtime to serialize payloads. Move those imports and you get a runtime
`NameError` the linter happily caused. So froot tells ruff exactly which base
classes and decorators are runtime-evaluated, and leaves their imports at module
scope.
"""),
        prose("""
The image is unusual for a Python service: it carries `git` and `npm`. That is
the loop's needs showing through, and the blast-radius story from §5 reappears as
a property of the image.
"""),
        code("projects/froot/Dockerfile", title="Dockerfile",
             logical="Dockerfile", peek=[(14, 28)]),
        prose("""
The deployment is one worker plus two one-shot Jobs. The worker connects out to
four things: Temporal, GitHub, the model proxy, and the telemetry collector. It
runs no database and accepts no inbound traffic of any kind.
"""),
        diagram("deploy",
                 "The worker connects out: long-polling Temporal, cloning and "
                 "PRing GitHub, calling the Ollama proxy over the tailnet, and "
                 "shipping telemetry to ClickStack. No inbound traffic.",
                 klass="wide"),
        infra("manifests/10-worker.yaml", peek=[(60, 67)]),
        callout("why", """
**Tiny requests, real-burst limits.** The node's request budget is nearly full,
though actual use sits around half. So the worker requests a small `cpu: 50m /
memory: 64Mi` just to schedule, while its limits leave headroom for the occasional
npm or git spike. The model runs externally, over the Ollama tunnel. That leaves
the worker brokering little more than Temporal, a shallow clone, and some HTTP.
"""),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="scorecard", act="The verdict", num="11",
    title="Does the code keep its promises?",
    technique="Evidence table",
    blocks=[
        prose("""
froot's spec lists principles that govern every decision. Below, each one is
scored against the actual code, with the file that proves it. The point is simple.
You should not have to take the README's word for any of it.
"""),
        table(
            ["Principle", "Upheld by", "Where"],
            [
                ["**Loops must close** — all six ingredients present", "durable schedule, bounded PR, CI wait, PR revert, the outcome log and labels, human-approves-every-PR", "`scan_workflow`, `bump_workflow`, `record_outcome`"],
                ["**Spine-heavy, model-thin**", "one model call per bump, framing not gating; ~90% of the loop is deterministic", "`model_judge.py`"],
                ["**CI is the oracle** — never re-run a repo's tests", "froot reads CI status; the worker carries no test toolchain", "`github.ci_status`, `Dockerfile`"],
                ["**Derive, never store** — no database of its own", "no seen-set; work re-derived each tick; outcome lives in GitHub and ClickStack", "`scan_workflow`, `record_outcome`"],
                ["**Chassis generalizes, loop specializes**", "the durable machinery imports no concrete adapter; signal plus lockfile-command plus prompt are the only loop-specific parts", "`ports`, `activities`"],
                ["**Earn autonomy; record first, gate later**", "every PR is human-approved; the track record is recorded but not yet acted on", "`compose.PR_LABELS`, `record_outcome`"],
            ],
            caption="Six principles, six pieces of code-level evidence."),
    ],
))

# ════════════════════════════════════════════════════════════════════════════
add(Section(
    id="vouch", act="The verdict", num="12",
    title="Two galleries, and a verdict",
    technique="Montage + checklist",
    blocks=[
        prose("""
Two patterns recur often enough to collect. First, the ways froot makes a wrong
state impossible. Second, the disciplines that keep the workflows replay-safe.
A reviewer can re-skim the sections above and confirm each row.
"""),
        table(
            ["Make illegal states unrepresentable", "Forbids", "Seen in"],
            [
                ["frozen, closed base model", "mutation; unknown or typo'd fields", "`domain/base.py`"],
                ["construction-time validator", "a candidate that is not a clean patch", "`candidate.py` §2"],
                ["discriminated unions", "an untagged variant; bad deserialization", "`changelog`, `ci`, `state`, `events`"],
                ["subset type (`TerminalCIStatus`)", "recording an outcome against a pending CI", "`ci.py` §2"],
                ["`TypeIs` narrowing", "treating a pending status as terminal", "`ci.py` §2"],
                ["`assert_never` on `match`", "forgetting a case when a union grows", "`ecosystem`, `state_machine`, `model_judge`"],
                ["rejected, not raised, transition", "an illegal event crashing the loop", "`state_machine.py` §3"],
                ["anchored field regex", "a slug or branch with a smuggled slash", "`repo.py`, `pull_request.py`"],
                ["`SecretStr`", "a token leaking into logs or tracebacks", "`settings.py` §8"],
            ],
            caption="Nine ways froot makes a wrong state fail to compile, fail to "
                    "construct, or fail safely."),
        table(
            ["Replay-safety discipline", "Mechanism"],
            [
                ["All I/O lives in activities, never workflows", "the six `@activity.defn` functions"],
                ["No wall clock or `asyncio.sleep` in a workflow", "`workflow.now()` and `workflow.sleep()` (§7)"],
                ["Adapter stacks never enter the sandbox", "lazy `import` inside activity bodies"],
                ["Bounded workflow history", "`continue_as_new` per scan tick (§7)"],
                ["Permanent vs transient faults distinguished", "non-retryable `ApplicationError` for misconfig and auth"],
            ],
            caption="Five disciplines, each checkable by eye, and exercised "
                    "end-to-end by the time-skipping tests."),
        callout("principle", """
**So, can you vouch for it?** From the code alone, not the marketing: the loop
closes from a durable schedule through a bounded PR, the CI oracle, a recorded
outcome, and the next tick. The model sits on a one-call typed leash. Illegal
states are unrepresentable by nine distinct mechanisms. The workflows are
replay-safe by five disciplines the tests exercise. Idempotency is structural at
two layers. Secrets are masked, and dependency code never runs in the worker. The
project is openly experimental and shaped for one author, and the README says so
first. Within that scope it is coherent, honest about its limits, and does what
it claims.
"""),
        diagram("roadmap",
                 "The staged path: close one loop, replicate it to prove it is a "
                 "template, let loops coordinate, and only then take on fixers that "
                 "write arbitrary code.", klass="wide"),
        prose("""
This was the reviewer's quarter. The [full edition](froot-explained-full.html)
walks every one of the 2,986 source lines, if you want to read the rest.
"""),
        raw('<div style="height:40px"></div>'),
    ],
))

# === MORE SECTIONS INSERTED ABOVE THIS LINE ===

if __name__ == "__main__":
    build(SECTIONS, [])
