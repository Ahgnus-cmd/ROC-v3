# ROC v3.0 — Package Manifest

## Overview

ROC (Reverse Organic Compiler) is an 11-stage bio-atomic compilation pipeline that transforms natural language into executable code via two independent paths — x86 Assembly (Path A) and LLVM IR (Path B) — with automated consistency verification and threat containment.

This repository contains the publicly released portion of ROC v3.0, including Stage 1–3 and the VERITAS Stage 11 consistency gate.

**Author**: Sungha (Meta Architect)
**Release Date**: 2026-05-30
**Version**: 3.0 (Public Release)

---

## File Structure

```
README.md                              # Main documentation
MANIFEST.md                            # This file

# Core Pipeline (Public)
stage1_nl_parser.py                    # Stage 1: NL → structured niche
stage2_path_a_hardware.py              # Stage 2: Path A — x86 Assembly
stage3_path_b_llvm.py                  # Stage 3: Path B — LLVM IR

# VERITAS Consistency Gate (Stage 11)
veritas_roc_type_consistency.py        # Type consistency validator
veritas_roc_operator_consistency.py    # Operator consistency validator
veritas_roc_result_consistency.py      # Result consistency validator
veritas_roc_unified_gate.py            # Unified gate orchestrator

# Examples
examples.py                            # Comprehensive usage examples
```

---

## Core Pipeline Modules

### Stage 1 — Natural Language Parser
**File**: `stage1_nl_parser.py`

Extracts computational intent and operands from natural language input.
Maps keywords to opcodes, ASM mnemonics, and LLVM operations.

**Public API**:
```python
def parse_niche(prompt: str) -> dict
```

**Example**:
```python
result = parse_niche("add 100 and 200")
# → {"keyword": "add", "opcode": "00000001",
#    "asm_cmd": "ADD", "llvm_op": "add", "operands": (100, 200)}
```

---

### Stage 2 — Path A: Hardware Compiler
**File**: `stage2_path_a_hardware.py`

Compiles Stage 1 niche output into binary bitstream and optimized x86 assembly.
Includes identity operation elimination and register mutation engine.

**Public API**:
```python
class PathA_HardwareCompiler:
    def compile(self, niche: dict, mutate_registers: bool = False) -> dict
```

**Example**:
```python
compiler = PathA_HardwareCompiler()
result = compiler.compile(niche)
# → {"bitstream": "00000001_01100100_11001000",
#    "optimized_instructions": ["MOV EAX, 100", "MOV EBX, 200", "ADD EAX, EBX"],
#    "registers": {"primary": "EAX", "secondary": "EBX"}}
```

---

### Stage 3 — Path B: LLVM IR Compiler
**File**: `stage3_path_b_llvm.py`

Compiles Stage 1 niche output into platform-independent LLVM IR.
Automatically selects i32 or i64 based on operand range.

**Public API**:
```python
class PathB_LLVMCompiler:
    def compile(self, niche: dict, tool_name: str = "roc_compute") -> dict
```

**Example**:
```python
compiler = PathB_LLVMCompiler()
result = compiler.compile(niche, tool_name="organic_adder")
# → {"ir_type": "i32", "function_name": "@organic_adder",
#    "ir_registers": ["%val_a", "%val_b", "%result"]}
```

---

## VERITAS Consistency Gate (Stage 11)

Stage 11 cross-validates Path A and Path B outputs before any result is released.
Three independent validators — unified into a single gate.

### Type Consistency Validator
**File**: `veritas_roc_type_consistency.py`

Validates that Stage 2 (Hardware) and Stage 3 (LLVM IR) type signatures align.

```python
def check_hardware_to_llvm_type_consistency(
    hardware_bitwidth: int,
    operand_1_value: int,
    operand_2_value: int,
    register_size: int,
    llvm_ir_type: str,
) -> TypeConsistencyResult
```

### Operator Consistency Validator
**File**: `veritas_roc_operator_consistency.py`

Validates that Stage 1 opcode extraction aligns with Stages 2 and 3.

```python
def check_operator_consistency(
    nl_keyword: str,
    nl_confidence: float,
    asm_mnemonic: str,
    bitstream: str,
    llvm_op_name: str,
) -> OperatorConsistencyResult
```

### Result Consistency Validator
**File**: `veritas_roc_result_consistency.py`

Validates that Path A and Path B produce equivalent results.

```python
def check_result_consistency(
    path_a_result: int,
    path_a_primary_reg: int,
    path_a_secondary_reg: int,
    path_a_bitstream: str,
    path_b_result: int,
    path_b_ir_register: int,
    path_b_ir_code: str,
    strict_mode: bool = True,
) -> ResultConsistencyResult
```

### Unified Gate
**File**: `veritas_roc_unified_gate.py`

Orchestrates all three validators. Weighted score must reach threshold — or output is held.

```python
gate = ROCConsistencyGate(passing_threshold=0.85)
report = gate.verify_pipeline(
    tool_name="organic_adder",
    type_score=1.0,
    operator_score=1.0,
    result_score=1.0,
)
# → verdict: PASS / HOLD
```

---

## Scoring

```
Weighted Score = (Type × 0.33) + (Operator × 0.33) + (Result × 0.34)

Pass threshold: ≥ 0.85 (default, configurable)
```

If weighted score falls below threshold — output is **held**, not released.

---

## Running the Modules

```bash
# Individual stages
python3 stage1_nl_parser.py
python3 stage2_path_a_hardware.py
python3 stage3_path_b_llvm.py

# VERITAS validators
python3 veritas_roc_type_consistency.py
python3 veritas_roc_operator_consistency.py
python3 veritas_roc_result_consistency.py
python3 veritas_roc_unified_gate.py

# All examples
python3 examples.py
```

Zero external dependencies. Python stdlib only.

---

## Performance

All modules are deterministic and real-time:

| Module | Latency |
|--------|---------|
| Stage 1 — NL Parser | < 1ms |
| Stage 2 — Path A | < 1ms |
| Stage 3 — Path B | < 1ms |
| VERITAS Type | < 1ms |
| VERITAS Operator | < 1ms |
| VERITAS Result | < 2ms |
| Unified Gate | < 5ms |

---

## What's Not in This Repository

Stages 4–10 of the ROC v3.0 pipeline remain private:

- Stage 4 — Syntax Tuning
- Stage 5 — Bio-Containment Lab
- Stage 6 — Atomic Synthesis
- Stage 7 — Encapsulation
- Stage 8 — Sandbox Verification
- Stage 9 — Mutation Engine
- Stage 10 — Host Deploy
- VAULT — IP protection layer (in development)

---

## KAGNUS OS Ecosystem

ROC v3.0 is a core module of KAGNUS OS — an independent meta-OS control tower for agentic AI systems.

| System | Role |
|--------|------|
| **ROC v3.0** | Code compilation + safety pipeline |
| **LUKE** | Dry-run pre-execution simulator |
| **VERITAS** | Truth/consistency verification |
| **LUAN** | AGI self/emotion layer |
| **Aegis** | Dynamic policy engine |
| **TWM-V** | Trust-weighted metrics |
| **AWRE** | Waste/inefficiency recycler |
| **VAULT** | IP protection layer |

---

*KAGNUS OS ecosystem — Independent AI Architecture Project*
*Author: Sungha Kim (Meta Architect)*
