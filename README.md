# ROC v3.0 — Reverse Organic Compiler

**An 11-stage bio-atomic compilation pipeline that transforms natural language into executable code via dual independent paths — with automated consistency verification and threat containment.**

---

## What is ROC?

ROC (Reverse Organic Compiler) compiles natural language instructions into machine-executable code through two independent compilation paths simultaneously:

- **Path A** — Natural Language → x86 Assembly (hardware level)
- **Path B** — Natural Language → LLVM IR (platform independent)

Both paths are verified against each other at every stage. If they diverge, the output is held — not released.

The core design principle: **a compiler that only speaks when it's sure.**

---

## Architecture — 11 Stages

```
NATURAL LANGUAGE INPUT
        │
        ▼
┌─────────────────────────────────────────────────┐
│  Stage 1   NL Parser                            │  ← Public
│            Extract intent + operands            │
└─────────────────────────────────────────────────┘
        │
        ├──────────────────────┐
        ▼                      ▼
┌───────────────┐    ┌───────────────────────────┐
│  Stage 2      │    │  Stage 3                  │  ← Public
│  Path A       │    │  Path B                   │
│  x86 Assembly │    │  LLVM IR                  │
└───────────────┘    └───────────────────────────┘
        │                      │
        └──────────┬───────────┘
                   ▼
        ┌──────────────────────┐
        │  Stage 4             │
        │  Syntax Tuning       │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 5             │
        │  Bio-Containment Lab │  ← Threat isolation
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 6             │
        │  Atomic Synthesis    │  ← Bio-atomic classification
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 7             │
        │  Encapsulation       │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 8             │
        │  Sandbox Verification│
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 9             │
        │  Mutation Engine     │  ← Variant generation + register mutation
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 10            │
        │  Host Deploy         │
        └──────────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Stage 11            │
        │  VERITAS Gate        │  ← Consistency verification before release
        └──────────────────────┘
                   │
                   ▼
        CLEARED OUTPUT
```

**12 classes · 9 modules · 11 stages**

No output exits without passing all 11 stages.

---

## Bio-Atomic Concept

ROC treats code constructs as **chemical elements** — each with defined atomic weight, reactivity, and toxicity.

| Code Construct | Bio-Atomic Analog | Property |
|---------------|-------------------|----------|
| Memory allocation | Heavy element | High reactivity — monitor closely |
| Pointer arithmetic | Unstable isotope | Decay tracking required |
| External call | Compound bond | Verify valence before execution |
| Loop structure | Molecular chain | Check for runaway reactions |
| Exception handler | Buffer compound | Absorption capacity limit |

This mapping allows ROC to **quantify safety** rather than rely on pattern matching alone.

---

## Bio-Containment Lab (Stage 5)

The Bio-Containment Lab is ROC's threat isolation environment:

- **Quarantine zone** — suspicious constructs isolated before evaluation
- **Threat scanning** — multi-signature pattern matching
- **Reaction chamber** — controlled analysis of potentially harmful logic
- **Auto-detoxification** — automatic neutralization of confirmed threats
- **Output gate** — nothing exits containment without VERITAS clearance

---

## Public Modules (Stage 1–3 + VERITAS Gate)

This repository contains the publicly released portion of ROC v3.0.

### Stage 1 — Natural Language Parser
`stage1_nl_parser.py`

Extracts computational intent and operands from natural language input.
Maps keywords to opcodes, assembly mnemonics, and LLVM operations.

```python
from stage1_nl_parser import parse_niche

result = parse_niche("add 100 and 200")
# → {"keyword": "add", "opcode": "00000001", "asm_cmd": "ADD",
#    "llvm_op": "add", "operands": (100, 200)}
```

### Stage 2 — Path A: Hardware Compiler
`stage2_path_a_hardware.py`

Compiles niche output into binary bitstream and optimized x86 assembly.
Includes identity operation elimination and register mutation engine.

```python
from stage2_path_a_hardware import PathA_HardwareCompiler

compiler = PathA_HardwareCompiler()
result = compiler.compile(niche)
# → {"bitstream": "00000001_01100100_11001000",
#    "optimized_instructions": ["MOV EAX, 100", "MOV EBX, 200", "ADD EAX, EBX"],
#    "registers": {"primary": "EAX", "secondary": "EBX"}}
```

### Stage 3 — Path B: LLVM IR Compiler
`stage3_path_b_llvm.py`

Compiles niche output into platform-independent LLVM IR.
Automatically selects i32 or i64 based on operand range.

```python
from stage3_path_b_llvm import PathB_LLVMCompiler

compiler = PathB_LLVMCompiler()
result = compiler.compile(niche, tool_name="organic_adder")
# → {"ir_type": "i32", "function_name": "@organic_adder",
#    "ir_code": "define i32 @organic_adder() { ... }"}
```

### Stage 11 — VERITAS Consistency Gate
`veritas_roc_*.py`

Cross-validates Path A and Path B outputs before release.
Three independent validators — type, operator, result — unified into a single gate.

```python
from veritas_roc_unified_gate import ROCConsistencyGate

gate = ROCConsistencyGate(passing_threshold=0.85)
report = gate.verify_pipeline(
    tool_name="organic_adder",
    type_score=1.0,
    operator_score=1.0,
    result_score=1.0,
)
# → verdict: PASS / HOLD
```

If any validator falls below threshold — output is **held**, not released.

---

## Quick Start

```bash
# Run Stage 1 parser
python3 stage1_nl_parser.py

# Run Stage 2 hardware compiler
python3 stage2_path_a_hardware.py

# Run Stage 3 LLVM compiler
python3 stage3_path_b_llvm.py

# Run VERITAS gate
python3 veritas_roc_unified_gate.py

# Run all examples
python3 examples.py
```

Zero external dependencies. Python stdlib only.

---

## KAGNUS OS Ecosystem

ROC v3.0 operates as a core module within KAGNUS OS — an independent meta-OS control tower for agentic AI systems.

| System | Role |
|--------|------|
| **ROC v3.0** | Code compilation + safety pipeline (this repo) |
| **LUKE** | Dry-run pre-execution simulator — catches bugs before they enter review |
| **VERITAS** | Truth/consistency verification — ROC's Stage 11 gate |
| **LUAN** | AGI self/emotion layer — SNN-13 neural network, 13Loop emotion tracking |
| **Aegis** | Dynamic policy engine — governs agent behavior at runtime |
| **TWM-V** | Trust-weighted metrics — filters low-confidence signals |
| **AWRE** | Waste/inefficiency recycler — recycles redundant computation |
| **VAULT** | IP protection layer — code escrow and training prevention |

---

## Design Philosophy

> A noisy compiler is worse than no compiler at all.

ROC was built around one non-negotiable constraint: **zero false positives in output**.

Every construct either clears all 11 stages or gets isolated. There is no "maybe flagged" state. Uncertain output never reaches the surface — it goes to containment.

This is not a tradeoff between precision and recall. It is a deliberate choice: **precision is the only metric that matters at the output gate.**

---

## Status

| Component | Status |
|-----------|--------|
| Stage 1 — NL Parser | ✓ Public |
| Stage 2 — Path A Hardware | ✓ Public |
| Stage 3 — Path B LLVM | ✓ Public |
| Stage 11 — VERITAS Gate | ✓ Public |
| Stage 4–10 — Core Pipeline | Private |
| Bio-Containment Lab | Private |
| VAULT | In development |

---

## License

All rights reserved. Contact the author for licensing inquiries.

---

*KAGNUS OS ecosystem — Independent AI Architecture Project*  
*Author: Sungha Kim (Meta Architect)*


