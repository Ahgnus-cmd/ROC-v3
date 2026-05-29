# -*- coding: utf-8 -*-
"""
VERITAS ROC Consistency Gate v1.0
Operator Consistency Validator

Purpose:
  Verify that Stage 1 (opcode extraction) is consistent across
  Stage 2 (Hardware/x86) and Stage 3 (LLVM IR) representations.

Public Release: MIT License
Author: Sungha (Meta Architect)
"""

from dataclasses import dataclass
from typing import Optional, Dict, List
from enum import Enum


class Opcode(Enum):
    """Standard binary opcodes"""
    ADD = "00000001"
    SUB = "00000010"
    MUL = "00000011"
    DIV = "00000100"
    AND = "00000101"
    OR = "00000110"
    SHL = "00000111"


class AsmInstruction(Enum):
    """x86 Assembly instruction mnemonics"""
    ADD = "ADD"
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    AND = "AND"
    OR = "OR"
    SHL = "SHL"


class LLVMOperation(Enum):
    """LLVM IR operation names"""
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "sdiv"
    AND = "and"
    OR = "or"
    SHL = "shl"


@dataclass
class Stage1_OpcodeExtraction:
    """Output from Stage 1: Natural Language → Opcode"""
    opcode: Opcode
    natural_language_keyword: str
    confidence: float  # How confident was the NL→Opcode mapping?


@dataclass
class Stage2_HardwareRepresentation:
    """Output from Stage 2: Hardware-level representation"""
    asm_instruction: AsmInstruction
    bitstream: str  # e.g., "00000001_0000...1010"
    register_allocation: Dict[str, str]  # {"primary": "EAX", "secondary": "EBX"}


@dataclass
class Stage3_LLVMRepresentation:
    """Output from Stage 3: LLVM IR representation"""
    llvm_operation: LLVMOperation
    ir_code: str  # e.g., "add i32 %a, %b"
    ir_registers: List[str]  # ["%val_a", "%val_b", "%result"]


@dataclass
class OperatorConsistencyResult:
    """Result of operator consistency check"""
    is_consistent: bool
    
    # Input signatures
    stage1: Stage1_OpcodeExtraction
    stage2: Stage2_HardwareRepresentation
    stage3: Stage3_LLVMRepresentation
    
    # Consistency metrics
    opcode_to_asm_match: bool
    opcode_to_llvm_match: bool
    asm_to_llvm_match: bool
    
    # Cross-stage validation
    bitstream_validity: bool  # Does bitstream start with correct opcode?
    
    # Confidence & violations
    consistency_score: float  # 0.0 - 1.0
    violations: List[str]


class OperatorConsistencyValidator:
    """
    Validates operator consistency across three stages:
    1. Stage 1: Natural Language → Opcode
    2. Stage 2: Opcode → x86 Assembly
    3. Stage 3: Opcode → LLVM IR
    
    Rules:
    1. Opcode must map to exactly one ASM instruction
    2. Opcode must map to exactly one LLVM operation
    3. ASM instruction and LLVM operation must be semantically equivalent
    4. Bitstream must encode the opcode at position [0:7]
    5. NL keyword confidence must be ≥ 0.7 (optional, for quality assurance)
    """
    
    # Mapping tables
    OPCODE_TO_ASM = {
        Opcode.ADD: AsmInstruction.ADD,
        Opcode.SUB: AsmInstruction.SUB,
        Opcode.MUL: AsmInstruction.MUL,
        Opcode.DIV: AsmInstruction.DIV,
        Opcode.AND: AsmInstruction.AND,
        Opcode.OR: AsmInstruction.OR,
        Opcode.SHL: AsmInstruction.SHL,
    }
    
    OPCODE_TO_LLVM = {
        Opcode.ADD: LLVMOperation.ADD,
        Opcode.SUB: LLVMOperation.SUB,
        Opcode.MUL: LLVMOperation.MUL,
        Opcode.DIV: LLVMOperation.DIV,
        Opcode.AND: LLVMOperation.AND,
        Opcode.OR: LLVMOperation.OR,
        Opcode.SHL: LLVMOperation.SHL,
    }
    
    # Semantic equivalence check (ASM ↔ LLVM)
    ASM_LLVM_EQUIVALENCE = {
        (AsmInstruction.ADD, LLVMOperation.ADD): True,
        (AsmInstruction.SUB, LLVMOperation.SUB): True,
        (AsmInstruction.MUL, LLVMOperation.MUL): True,
        (AsmInstruction.DIV, LLVMOperation.DIV): True,
        (AsmInstruction.AND, LLVMOperation.AND): True,
        (AsmInstruction.OR, LLVMOperation.OR): True,
        (AsmInstruction.SHL, LLVMOperation.SHL): True,
    }
    
    def __init__(self):
        self.check_log = []
    
    def validate(
        self,
        stage1: Stage1_OpcodeExtraction,
        stage2: Stage2_HardwareRepresentation,
        stage3: Stage3_LLVMRepresentation,
        min_nl_confidence: float = 0.7,
    ) -> OperatorConsistencyResult:
        """
        Validate operator consistency across all three stages.
        
        Args:
            stage1: Opcode extraction from NL
            stage2: Hardware (x86) representation
            stage3: LLVM IR representation
            min_nl_confidence: Minimum confidence threshold for NL→Opcode mapping
        
        Returns:
            OperatorConsistencyResult with detailed findings
        """
        violations = []
        consistency_score = 1.0
        
        # ─── Check 1: Opcode → ASM mapping ───
        expected_asm = self.OPCODE_TO_ASM.get(stage1.opcode)
        opcode_to_asm_match = expected_asm == stage2.asm_instruction
        
        if not opcode_to_asm_match:
            violations.append(
                f"Opcode→ASM mismatch: {stage1.opcode.name} should map to "
                f"{expected_asm.name if expected_asm else 'UNKNOWN'}, "
                f"but got {stage2.asm_instruction.name}"
            )
            consistency_score -= 0.25
        
        # ─── Check 2: Opcode → LLVM mapping ───
        expected_llvm = self.OPCODE_TO_LLVM.get(stage1.opcode)
        opcode_to_llvm_match = expected_llvm == stage3.llvm_operation
        
        if not opcode_to_llvm_match:
            violations.append(
                f"Opcode→LLVM mismatch: {stage1.opcode.name} should map to "
                f"{expected_llvm.name if expected_llvm else 'UNKNOWN'}, "
                f"but got {stage3.llvm_operation.name}"
            )
            consistency_score -= 0.25
        
        # ─── Check 3: ASM ↔ LLVM semantic equivalence ───
        asm_llvm_match = self.ASM_LLVM_EQUIVALENCE.get(
            (stage2.asm_instruction, stage3.llvm_operation),
            False
        )
        
        if not asm_llvm_match:
            violations.append(
                f"ASM↔LLVM equivalence broken: {stage2.asm_instruction.name} "
                f"and {stage3.llvm_operation.name} are not semantically equivalent"
            )
            consistency_score -= 0.25
        
        # ─── Check 4: Bitstream validity ───
        bitstream_validity = self._validate_bitstream(
            stage2.bitstream, stage1.opcode
        )
        
        if not bitstream_validity:
            violations.append(
                f"Bitstream validity: Does not start with opcode {stage1.opcode.value}"
            )
            consistency_score -= 0.15
        
        # ─── Check 5: NL confidence threshold ───
        if stage1.confidence < min_nl_confidence:
            violations.append(
                f"NL→Opcode confidence below threshold: "
                f"{stage1.confidence:.2f} < {min_nl_confidence:.2f}"
            )
            consistency_score -= 0.10
        
        is_consistent = len(violations) == 0
        consistency_score = max(0.0, consistency_score)
        
        result = OperatorConsistencyResult(
            is_consistent=is_consistent,
            stage1=stage1,
            stage2=stage2,
            stage3=stage3,
            opcode_to_asm_match=opcode_to_asm_match,
            opcode_to_llvm_match=opcode_to_llvm_match,
            asm_to_llvm_match=asm_llvm_match,
            bitstream_validity=bitstream_validity,
            consistency_score=consistency_score,
            violations=violations,
        )
        
        self.check_log.append(result)
        return result
    
    @staticmethod
    def _validate_bitstream(bitstream: str, opcode: Opcode) -> bool:
        """Check if bitstream starts with the correct opcode"""
        if not bitstream or "_" not in bitstream:
            return False
        
        opcode_part = bitstream.split("_")[0]
        return opcode_part == opcode.value


# ═════════════════════════════════════════════════════════════════
# Convenience Functions
# ═════════════════════════════════════════════════════════════════

def check_operator_consistency(
    nl_keyword: str,
    nl_confidence: float,
    asm_mnemonic: str,
    bitstream: str,
    llvm_op_name: str,
) -> OperatorConsistencyResult:
    """
    High-level API for operator consistency checking.
    
    Args:
        nl_keyword: Natural language keyword (e.g., "더하기", "add", "+")
        nl_confidence: Confidence of NL→Opcode mapping (0.0-1.0)
        asm_mnemonic: x86 mnemonic (e.g., "ADD", "SUB")
        bitstream: Hardware bitstream (e.g., "00000001_...")
        llvm_op_name: LLVM operation (e.g., "add", "sub")
    
    Returns:
        OperatorConsistencyResult
    """
    
    # Map NL keyword to opcode
    keyword_to_opcode = {
        "더하기": Opcode.ADD, "add": Opcode.ADD, "+": Opcode.ADD,
        "빼기": Opcode.SUB, "sub": Opcode.SUB, "-": Opcode.SUB,
        "곱하기": Opcode.MUL, "mul": Opcode.MUL, "*": Opcode.MUL,
        "나누기": Opcode.DIV, "div": Opcode.DIV, "/": Opcode.DIV,
    }
    
    opcode = keyword_to_opcode.get(nl_keyword, Opcode.ADD)
    
    stage1 = Stage1_OpcodeExtraction(
        opcode=opcode,
        natural_language_keyword=nl_keyword,
        confidence=nl_confidence,
    )
    
    stage2 = Stage2_HardwareRepresentation(
        asm_instruction=AsmInstruction[asm_mnemonic],
        bitstream=bitstream,
        register_allocation={"primary": "EAX", "secondary": "EBX"},
    )
    
    stage3 = Stage3_LLVMRepresentation(
        llvm_operation=LLVMOperation[llvm_op_name.upper()],
        ir_code=f"{llvm_op_name} i32 %a, %b",
        ir_registers=["%a", "%b", "%result"],
    )
    
    validator = OperatorConsistencyValidator()
    return validator.validate(stage1, stage2, stage3)


# ═════════════════════════════════════════════════════════════════
# Example Usage
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("VERITAS ROC Operator Consistency Validator — Demo")
    print("=" * 70)
    
    # Test Case 1: Fully consistent (ADD operation)
    result1 = check_operator_consistency(
        nl_keyword="더하기",
        nl_confidence=0.95,
        asm_mnemonic="ADD",
        bitstream="00000001_0000...1010",
        llvm_op_name="add",
    )
    print(f"\nTest 1 - Fully Consistent (ADD):")
    print(f"  ✓ Consistent: {result1.is_consistent}")
    print(f"  Consistency Score: {result1.consistency_score:.1%}")
    print(f"  Violations: {len(result1.violations)}")
    
    # Test Case 2: Inconsistent (opcode→ASM mismatch)
    result2 = check_operator_consistency(
        nl_keyword="더하기",  # ADD
        nl_confidence=0.95,
        asm_mnemonic="SUB",  # But ASM is SUB!
        bitstream="00000001_0000...1010",
        llvm_op_name="add",
    )
    print(f"\nTest 2 - Inconsistent (ADD keyword but SUB ASM):")
    print(f"  ✗ Consistent: {result2.is_consistent}")
    print(f"  Consistency Score: {result2.consistency_score:.1%}")
    print(f"  Violations:")
    for v in result2.violations:
        print(f"    - {v}")
    
    # Test Case 3: Low NL confidence
    result3 = check_operator_consistency(
        nl_keyword="덧셈",  # Unclear keyword
        nl_confidence=0.5,  # Below threshold
        asm_mnemonic="ADD",
        bitstream="00000001_0000...1010",
        llvm_op_name="add",
    )
    print(f"\nTest 3 - Low NL Confidence:")
    print(f"  ✗ Consistent: {result3.is_consistent}")
    print(f"  Consistency Score: {result3.consistency_score:.1%}")
    print(f"  Violations:")
    for v in result3.violations:
        print(f"    - {v}")
    
    # Test Case 4: Bitstream validity check
    result4 = check_operator_consistency(
        nl_keyword="더하기",
        nl_confidence=0.95,
        asm_mnemonic="ADD",
        bitstream="00000010_0000...1010",  # Wrong opcode in bitstream!
        llvm_op_name="add",
    )
    print(f"\nTest 4 - Bitstream Validity Mismatch:")
    print(f"  ✗ Consistent: {result4.is_consistent}")
    print(f"  Consistency Score: {result4.consistency_score:.1%}")
    print(f"  Violations:")
    for v in result4.violations:
        print(f"    - {v}")
    
    print("\n" + "=" * 70)
