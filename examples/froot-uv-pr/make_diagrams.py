"""Authoring source for the Mermaid diagrams in the uv-ecosystem PR walkthrough.

Each entry is written to diagrams/<name>.mmd; ../../tools/render_diagrams.sh
rasterises them to svg/<name>.svg with mermaid-cli (system Chrome). Kept in one
file so the whole diagram set is reviewable and re-renderable at once.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "diagrams"
OUT.mkdir(exist_ok=True)

INIT = ("%%{init: {'theme':'base','themeVariables':{"
        "'fontFamily':'ui-sans-serif, system-ui, sans-serif',"
        "'edgeLabelBackground':'#ffffff','lineColor':'#9e9e9e',"
        "'primaryTextColor':'#263238','tertiaryTextColor':'#37474f'}}}%%\n")

# new = added by this PR; keep = pre-existing chassis; ext = external truth.
CLASSES = (
    "classDef new fill:#e8f5e9,stroke:#2e7d32,stroke-width:2.5px,color:#1b5e20;\n"
    "classDef keep fill:#eef2f7,stroke:#5b6b7b,stroke-width:2px,color:#1e293b;\n"
    "classDef port fill:#fdf3e7,stroke:#cc7a30,stroke-width:2px,color:#8a4b12;\n"
    "classDef ext fill:#eceff1,stroke:#78909c,stroke-width:2px,color:#37474f;\n"
    "classDef drop fill:#fdeaea,stroke:#c0392b,stroke-width:2px,color:#7b241c;\n"
)

D = {}

# ── 1. The seam: an additive change behind one unchanged port ────────────────
D["seam"] = INIT + r"""
flowchart TB
    Act["⚙️ scan_candidates · open_pull_request<br/>(activities — chassis)"]
    Reg["🧭 package_manager_for(ecosystem)<br/>(new dispatch)"]
    Port["📜 PackageManager<br/>(Protocol — the seam)"]
    Npm["🔌 NpmPackageManager<br/>(unchanged)"]
    Uv["🆕 UvPackageManager<br/>(this PR)"]
    Loop["♻️ state machine · bump &amp; scan workflows<br/>CI wait · record outcome<br/>(0 lines changed)"]

    Act -->|"target.ecosystem"| Reg
    Reg -->|"Ecosystem.NPM"| Npm
    Reg -->|"Ecosystem.UV"| Uv
    Npm -.->|"satisfies (structural)"| Port
    Uv -.->|"satisfies (structural)"| Port
    Act --> Loop

    class Reg,Uv new
    class Act,Npm,Loop keep
    class Port port
""" + CLASSES

# ── 2. The uv pipeline: facts in, one patch out ──────────────────────────────
D["uv-pipeline"] = INIT + r"""
flowchart LR
    Manifest[("pyproject.toml")]
    Lock[("uv.lock")]
    PyPI[("🐍 PyPI JSON API")]

    Direct["parse_direct_dependencies<br/>PEP 621 + PEP 735 names"]
    Locked["parse_locked_versions<br/>current version per dep"]
    Avail["parse_available_versions<br/>drop yanked + non-semver"]

    Up["AvailableUpgrade[]<br/>(raw facts)"]
    Policy["select_patch_candidates<br/>highest stable patch<br/>(pure, shared)"]
    Apply["uv lock --upgrade-package<br/>pkg==target (lockfile-only)"]

    Manifest --> Direct
    Lock --> Locked
    PyPI --> Avail
    Direct --> Up
    Locked --> Up
    Avail --> Up
    Up --> Policy
    Policy --> Apply

    class Direct,Locked,Avail,Apply new
    class Up,Policy keep
    class Manifest,Lock,PyPI ext
""" + CLASSES

# ── 3. The version funnel: reuse semver, drop the rest ───────────────────────
D["versions"] = INIT + r"""
flowchart TB
    All["every published release<br/>(~70 for httpx, ~1500 for hypothesis)"]
    Yank["drop fully-yanked / fileless"]
    Sem{"Version.parse<br/>strict semver?"}
    Drop["dropped, conservatively:<br/>1.3.0rc1 · 0.63b1 · 1!2.0<br/>2.0 · 1.2.3.4 · 1.2.post1"]
    Keep["kept: 1.2.3 · 1.2.4 · 2.0.1 …"]
    Patch{"is_patch_bump_of(current)<br/>same major.minor, higher, stable"}
    Target["highest stable patch<br/>= the proposed target"]
    None2["no candidate<br/>(propose nothing)"]

    All --> Yank --> Sem
    Sem -->|"not X.Y.Z"| Drop
    Sem -->|"clean semver"| Keep
    Keep --> Patch
    Patch -->|"yes"| Target
    Patch -->|"none"| None2

    class All,Yank,Sem,Keep,Patch keep
    class Drop drop
    class Target new
    class None2 ext
""" + CLASSES

for name, text in D.items():
    (OUT / f"{name}.mmd").write_text(text.lstrip("\n"))
print(f"wrote {len(D)} diagrams to {OUT}")
