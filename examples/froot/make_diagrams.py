"""Authoring source for every Mermaid diagram in the froot reading doc.

Each entry is written to diagrams/<name>.mmd; render.sh rasterises them to
svg/<name>.svg with mermaid-cli (system Chrome). Kept in one file so the whole
diagram set is reviewable and re-renderable at once.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "diagrams"
OUT.mkdir(exist_ok=True)

INIT = ("%%{init: {'theme':'base','themeVariables':{"
        "'fontFamily':'ui-sans-serif, system-ui, sans-serif',"
        "'edgeLabelBackground':'#ffffff','lineColor':'#9e9e9e',"
        "'primaryTextColor':'#263238','tertiaryTextColor':'#37474f'}}}%%\n")

# Shared ownership classDefs (chassis/model/terrain/steward) + layer palette.
OWNER = (
    "classDef chassis fill:#e1f5ff,stroke:#0288d1,stroke-width:2px,color:#01579b;\n"
    "classDef model fill:#ede7f6,stroke:#5e35b1,stroke-width:2px,color:#311b92;\n"
    "classDef terrain fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;\n"
    "classDef steward fill:#fff3e0,stroke:#ef6c00,stroke-width:2px,color:#e65100;\n"
)
LAYER = (
    "classDef domain fill:#eef2f7,stroke:#5b6b7b,stroke-width:2px,color:#1e293b;\n"
    "classDef policy fill:#f1ecfb,stroke:#7e57c2,stroke-width:2px,color:#4527a0;\n"
    "classDef port fill:#fdf3e7,stroke:#cc7a30,stroke-width:2px,color:#8a4b12;\n"
    "classDef adapter fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;\n"
    "classDef spine fill:#e1f5ff,stroke:#0288d1,stroke-width:2px,color:#01579b;\n"
    "classDef ext fill:#eceff1,stroke:#78909c,stroke-width:2px,color:#37474f;\n"
)

D = {}

# ── 1. The dependency-patch loop (hero) ──────────────────────────────────────
D["loop"] = INIT + r"""
flowchart LR
    %% froot — the dependency-patch loop, closing through external truth
    Schedule["⏰ Durable schedule<br/>(Temporal timer)"]
    Scan["🔍 Scan candidates<br/>(checkout · npm · deterministic)"]
    Judge["🤖 Judge changelog<br/>(thin pydantic-ai)"]
    PR["🔀 One PR per bump<br/>(manifest + lockfile)"]
    CI{"✅ Repo's own CI<br/>green?"}
    Merge["👤 Human merges<br/>(approval gate)"]
    Closed["⚑ Leave PR open<br/>(flagged red)"]
    Record["📊 Record outcome"]
    GitHub[("🐙 GitHub<br/>outcome ledger")]
    Click[("📈 ClickStack<br/>run telemetry")]

    Schedule -->|"&nbsp;① signal&nbsp;"| Scan
    Scan -->|"&nbsp;② action&nbsp;"| Judge
    Judge --> PR
    PR -->|"&nbsp;③ durably wait on CI (mins–hrs)&nbsp;"| CI
    CI -->|"&nbsp;green&nbsp;"| Merge
    CI -->|"&nbsp;red / timeout&nbsp;"| Closed
    Merge -->|"&nbsp;④ commit&nbsp;"| Record
    Closed --> Record
    Record -->|"&nbsp;⑤ update&nbsp;"| GitHub
    Record --> Click
    Record -.->|"&nbsp;decays into the next tick's signal&nbsp;"| Schedule

    class Schedule,Scan,PR,Record,Closed chassis
    class Judge model
    class CI,GitHub,Click terrain
    class Merge steward
    linkStyle 4 stroke:#2e7d32,stroke-width:2px
    linkStyle 5 stroke:#ef6c00,stroke-width:2px
    linkStyle 10 stroke:#9e9e9e,stroke-width:1.5px,stroke-dasharray:5
""" + OWNER

# ── 2. Layered architecture ──────────────────────────────────────────────────
D["architecture"] = INIT + r"""
flowchart TB
    %% Strictly inward-depending layers; arrows point the way imports may go.
    subgraph Shell["🌍 Impure shell"]
      direction LR
      Entry["🚀 worker / scan_starter<br/>(entrypoints)"]
      Spine["⚙️ workflow spine<br/>(Temporal workflows + activities)"]
      Adapters["🔌 adapters<br/>(npm · github · model · http · otel)"]
    end
    subgraph Seam["🪡 The seam"]
      Ports["📜 ports<br/>(typed Protocols)"]
    end
    subgraph Core["💎 Pure core (no I/O, no framework)"]
      direction LR
      Policy["🧮 policy<br/>(candidates · naming · compose · state-machine)"]
      Domain["🧊 domain<br/>(frozen, closed value objects)"]
    end

    Entry --> Spine
    Spine --> Ports
    Spine --> Policy
    Adapters -. implements .-> Ports
    Spine -. interprets effects via .-> Adapters
    Policy --> Domain
    Adapters --> Domain

    class Entry,Spine spine
    class Adapters adapter
    class Ports port
    class Policy policy
    class Domain domain
    linkStyle 3 stroke:#cc7a30,stroke-width:2px,stroke-dasharray:5
    linkStyle 4 stroke:#0288d1,stroke-width:2px,stroke-dasharray:5
""" + LAYER

# ── 3. ChangelogVerdict union (class) ────────────────────────────────────────
D["verdict-union"] = INIT + r"""
classDiagram
    direction LR
    class ChangelogVerdict {
      «discriminated union»
      +kind
    }
    class CleanVerdict {
      kind = "clean"
      +str rationale
    }
    class RiskyVerdict {
      kind = "risky"
      +str rationale
      +tuple concerns
    }
    class UnknownVerdict {
      kind = "unknown"
      +str rationale
    }
    ChangelogVerdict <|-- CleanVerdict
    ChangelogVerdict <|-- RiskyVerdict
    ChangelogVerdict <|-- UnknownVerdict
    note for UnknownVerdict "reached without spending\na model call"
"""

# ── 4. CI status lattice ─────────────────────────────────────────────────────
D["ci-lattice"] = INIT + r"""
flowchart TB
    Read(["📡 ci_status reading"])
    Read --> Pending["⏳ CIPending<br/>(non-terminal — keep waiting)"]
    Read --> Passed["✅ CIPassed"]
    Read --> Failed["❌ CIFailed<br/>(+ failing names)"]
    Read --> Absent["⊘ CIAbsent<br/>(no checks)"]
    Read --> Timed["⌛ CITimedOut<br/>(deadline elapsed)"]

    subgraph Terminal["TerminalCIStatus — the only readings recordable as an outcome"]
      direction LR
      Passed
      Failed
      Absent
      Timed
    end

    Pending -. "is_terminal() ⇒ false<br/>(spine must keep polling)" .-> Terminal

    class Pending steward
    class Passed,Absent terrain
    class Failed,Timed model
    style Terminal fill:#f7faf7,stroke:#2e7d32,stroke-width:1.5px,color:#1b5e20
    linkStyle 5 stroke:#ef6c00,stroke-width:1.5px,stroke-dasharray:4
""" + OWNER

# ── 5. State / Event / Effect algebra ────────────────────────────────────────
D["algebra"] = INIT + r"""
flowchart LR
    %% Three parallel discriminated unions kept in lock-step by the state machine.
    subgraph S["🧊 BumpState (where we are)"]
      direction TB
      s1["Discovered"] --> s2["Judged"] --> s3["AwaitingCi"] --> s4["Recorded ∎"]
    end
    subgraph EV["📨 LoopEvent (what just happened)"]
      direction TB
      e1["ChangelogJudged"]
      e2["PullRequestReady"]
      e3["CiResolved"]
      e4["OutcomeRecorded"]
    end
    subgraph EF["⚡ Effect (what to do next)"]
      direction TB
      f1["JudgeChangelog"]
      f2["OpenPullRequest"]
      f3["AwaitCi"]
      f4["RecordOutcome"]
    end
    s1 -. emits .-> f1
    f1 -. yields .-> e1
    e1 ==> s2
    s2 -. emits .-> f2
    f2 -. yields .-> e2
    e2 ==> s3
    s3 -. emits .-> f3
    f3 -. yields .-> e3
    e3 ==> s4

    class s1,s2,s3,s4 domain
    class e1,e2,e3,e4 policy
    class f1,f2,f3,f4 spine
""" + LAYER

# ── 6. Bump state machine ────────────────────────────────────────────────────
D["state-machine"] = INIT + r"""
stateDiagram-v2
    direction LR
    [*] --> Discovered : start(candidate)
    Discovered --> Judged : ChangelogJudged / emit OpenPullRequest
    Judged --> AwaitingCi : PullRequestReady / emit AwaitCi
    AwaitingCi --> Recorded : CiResolved(terminal) / emit RecordOutcome
    AwaitingCi --> AwaitingCi : CiResolved(pending) ⇒ REJECTED (no move)
    Recorded --> [*] : OutcomeRecorded ⇒ IGNORED (loop complete)

    note right of Discovered
      Any unexpected event in any
      state ⇒ REJECTED transition,
      never an exception.
    end note
"""

# ── 7. Ports & adapters hexagon ──────────────────────────────────────────────
D["hexagon"] = INIT + r"""
flowchart LR
    subgraph spine["⚙️ Spine (activities)"]
      A1["scan / open_pr / check_ci / record"]
    end
    subgraph ports["📜 ports.protocols"]
      direction TB
      P1["PackageManager"]
      P2["Forge"]
      P3["ChangelogSource"]
      P4["ModelJudge"]
    end
    subgraph real["🔌 Real adapters (production)"]
      direction TB
      R1["NpmPackageManager"]
      R2["GitHubForge"]
      R3["HttpChangelogSource"]
      R4["PydanticAiJudge"]
    end
    subgraph fake["🧪 Fakes (tests)"]
      direction TB
      F1["FakePackageManager"]
      F2["FakeForge"]
      F3["FakeChangelogSource"]
      F4["FakeJudge"]
    end

    A1 --> P1 & P2 & P3 & P4
    P1 -. implemented by .-> R1
    P2 -. implemented by .-> R2
    P3 -. implemented by .-> R3
    P4 -. implemented by .-> R4
    P1 -. swapped for .-> F1
    P2 -. swapped for .-> F2
    P3 -. swapped for .-> F3
    P4 -. swapped for .-> F4

    class A1 spine
    class P1,P2,P3,P4 port
    class R1,R2,R3,R4 adapter
    class F1,F2,F3,F4 model
""" + LAYER

# ── 8. npm list_upgrades pipeline ────────────────────────────────────────────
D["npm-pipeline"] = INIT + r"""
flowchart TB
    PJ["📄 package.json"] --> Direct["parse_direct_dependencies<br/>(deps + devDeps)"]
    PL["🔒 package-lock.json"] --> Locked["parse_locked_versions<br/>(v2/3 packages → v1 fallback)"]
    Direct --> Loop{"for each direct dep<br/>with a locked version"}
    Locked --> Loop
    Loop -->|"npm view &lt;pkg&gt; versions --json"| Versions["parse_versions<br/>(drop unparseable)"]
    Versions --> AU["📦 AvailableUpgrade<br/>(current + available[])"]
    AU --> Policy["🧮 select_patch_candidates<br/>(pure policy, not the adapter)"]
    Policy --> PC["✅ PatchCandidate[]"]

    class PJ,PL ext
    class Direct,Locked,Versions,Loop adapter
    class AU domain
    class Policy policy
    class PC domain
""" + LAYER

# ── 9. Idempotent PR open (sequence) ─────────────────────────────────────────
D["pr-idempotent"] = INIT + r"""
sequenceDiagram
    autonumber
    participant W as 🔁 BumpWorkflow
    participant A as ⚙️ open_pull_request
    participant F as 🔌 GitHubForge
    participant GH as 🐙 GitHub
    W->>A: OpenPullRequest(candidate, verdict)
    A->>F: find_open_pull_request(branch)
    F->>GH: GET /pulls?head=owner:branch&state=open
    alt PR already exists
      GH-->>F: [ existing PR ]
      F-->>A: PullRequestRef
      Note over A: short-circuit — no checkout/apply/push
    else none yet
      GH-->>F: [ ]
      A->>F: checkout + apply_patch_bump + push_branch
      A->>F: open_pull_request(draft)
      F->>GH: POST /pulls
      alt 422 (branch race)
        F->>GH: re-find open PR
        GH-->>F: existing PR
      end
      F-->>A: PullRequestRef
    end
    A-->>W: PullRequestReady(pr)
"""

# ── 10. Best-effort changelog fetch ──────────────────────────────────────────
D["changelog-fetch"] = INIT + r"""
flowchart TB
    Start(["judge_changelog(candidate)"]) --> Reg{"GET registry/&lt;pkg&gt;<br/>200?"}
    Reg -->|no| None1["∅ None"]
    Reg -->|yes| RepoP{"github_repo_from_registry<br/>repo found?"}
    RepoP -->|no| None2["∅ None"]
    RepoP -->|yes| Notes{"release notes for<br/>v&lt;tag&gt; or &lt;tag&gt;?"}
    Notes -->|no| None3["∅ None"]
    Notes -->|yes| CL["📝 Changelog(text, source_url)"]
    None1 --> Unk["UnknownVerdict<br/>(no model call)"]
    None2 --> Unk
    None3 --> Unk
    CL --> Model["🤖 PydanticAiJudge.judge<br/>(the one model call)"]
    Model --> V["Clean / Risky / Unknown verdict"]

    class Start,Notes,Reg,RepoP adapter
    class None1,None2,None3,Unk steward
    class CL domain
    class Model model
    class V policy
    linkStyle 1,3,5 stroke:#ef6c00,stroke-width:1.5px,stroke-dasharray:4
""" + LAYER

# ── 11. Scan tick / continue-as-new ──────────────────────────────────────────
D["scan-tick"] = INIT + r"""
flowchart LR
    Start(["▶️ ScanWorkflow.run(params)"]) --> Scan["scan_candidates<br/>(activity)"]
    Scan --> Disp["for each candidate:<br/>dispatch_bump (idempotent)"]
    Disp --> Cont{"continuous?"}
    Cont -->|no| Ret["return ScanResult ∎"]
    Cont -->|yes| Sleep["⏰ workflow.sleep(interval)<br/>(durable timer — free while idle)"]
    Sleep --> CAN["♻️ continue_as_new<br/>(fresh history, one tick)"]
    CAN -.->|"next tick re-derives work<br/>(no stored cursor)"| Start

    class Start,Scan,Disp,Sleep,CAN,Ret spine
    class Cont steward
    linkStyle 6 stroke:#0288d1,stroke-width:1.5px,stroke-dasharray:5
""" + LAYER

# ── 12. Bump workflow effect interpretation (sequence) ───────────────────────
D["bump-sequence"] = INIT + r"""
sequenceDiagram
    autonumber
    participant SM as 🧮 state_machine (pure)
    participant WF as 🔁 BumpWorkflow._execute
    participant ACT as ⚙️ activities
    participant CI as 🐙 repo CI

    Note over SM,WF: transition = start(candidate)
    SM->>WF: effect JudgeChangelog
    WF->>ACT: judge_changelog(candidate)
    ACT-->>WF: ChangelogVerdict
    WF->>SM: advance(Discovered, ChangelogJudged)
    SM->>WF: effect OpenPullRequest
    WF->>ACT: open_pull_request(...)
    ACT-->>WF: PullRequestRef
    WF->>SM: advance(Judged, PullRequestReady)
    SM->>WF: effect AwaitCi
    loop durable poll until terminal or 1h deadline
      WF->>ACT: check_ci(head_sha)
      ACT->>CI: read combined status
      CI-->>WF: CIPending → sleep(1m) ⏰
    end
    CI-->>WF: CIPassed / CIFailed
    WF->>SM: advance(AwaitingCi, CiResolved)
    SM->>WF: effect RecordOutcome
    WF->>ACT: record_outcome(...)  ✅ label + log
    WF-->>SM: advance → Recorded ∎
"""

# ── 13. Test pyramid ─────────────────────────────────────────────────────────
D["test-pyramid"] = INIT + r"""
flowchart TB
    subgraph L3["🔺 Integration — Temporal time-skipping server"]
      I1["test_bump_workflow · test_scan_workflow<br/>(real spine, mocked activities, fast-forwarded CI wait)"]
    end
    subgraph L2["🟦 Seam — activities over in-memory fakes"]
      M1["test_activities<br/>(FakeForge · FakePackageManager · FakeJudge)"]
    end
    subgraph L1["🟩 Pure unit + property — no I/O at all"]
      U1["domain · policy · adapter parsers · settings<br/>(+ Hypothesis laws on Version)"]
    end
    L3 --> L2 --> L1

    class I1 spine
    class M1 port
    class U1 domain
    style L3 fill:#eef7fc,stroke:#0288d1
    style L2 fill:#fdf3e7,stroke:#cc7a30
    style L1 fill:#eef7ef,stroke:#2e7d32
""" + LAYER

# ── 14. Cluster deployment topology ──────────────────────────────────────────
D["deploy"] = INIT + r"""
flowchart TB
    subgraph cluster["🐳 zo-k8s (DOKS · single node)"]
      direction TB
      subgraph fns["namespace: froot"]
        Worker["📦 froot-worker<br/>(1 replica · git + npm)"]
        StartJob["⏯️ start-scan Job<br/>(scan_starter)"]
      end
      subgraph tns["namespace: temporal"]
        Front["⚙️ temporal-frontend:7233"]
        Otel["📡 temporal-otel-collector"]
      end
      Ollama["🔀 ollama.llm proxy<br/>(nginx → tailnet)"]
    end
    Mac["💻 Mac Studio<br/>Ollama · Gemma 4 e4b"]
    GH[("🐙 GitHub<br/>clone · PR · CI · labels")]
    Click[("📈 ClickStack / HyperDX")]

    Worker <-->|"long-poll tasks"| Front
    StartJob -->|"start ScanWorkflow"| Front
    Worker <-->|"https (token)"| GH
    Worker -->|"OpenAI /v1 (only when changelog exists)"| Ollama
    Ollama -.->|"tailscale serve"| Mac
    Worker -->|"OTLP/HTTP traces + SDK metrics"| Otel
    Otel --> Click

    class Worker,StartJob,Front,Otel,Ollama spine
    class Mac,GH,Click ext
    linkStyle 2 stroke:#2e7d32,stroke-width:2px
    linkStyle 4 stroke:#78909c,stroke-width:1.5px,stroke-dasharray:5
""" + LAYER

# ── 15. Roadmap ──────────────────────────────────────────────────────────────
D["roadmap"] = INIT + r"""
flowchart LR
    S1["1 · Close one loop<br/>dependency-patch, end-to-end<br/><b>(you are here)</b>"]
    S2["2 · Replicate<br/>security-patch<br/>(same chassis, sharper signal)"]
    S3["3 · Coordinate<br/>notifier loops guard<br/>a running durable app"]
    S4["4 · Fixers<br/>flaky-test / refactor<br/>(needs an agentic harness)"]
    S1 ==>|"proves the template"| S2 ==>|"loops read each other"| S3 ==>|"decided on terrain that works"| S4

    class S1 terrain
    class S2 chassis
    class S3 model
    class S4 steward
""" + OWNER

for name, src in D.items():
    (OUT / f"{name}.mmd").write_text(src.lstrip("\n"))
print(f"wrote {len(D)} diagram sources to {OUT}")
