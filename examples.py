# -*- coding: utf-8 -*-
"""
VERITAS ROC Consistency Gate — Comprehensive Examples

This file demonstrates all three validators in realistic scenarios
based on actual ROC v3 compilation pipeline outputs.
"""

from veritas_roc_type_consistency import check_hardware_to_llvm_type_consistency
from veritas_roc_operator_consistency import check_operator_consistency
from veritas_roc_result_consistency import check_result_consistency
from veritas_roc_unified_gate import ROCConsistencyGate


def example_1_simple_addition():
    """
    Example 1: Simple Addition (100 + 200 = 300)
    
    Scenario: Compile "100과 200을 더하기" (Add 100 and 200)
    
    - Stage 1: Extract opcode ADD from NL
    - Stage 2: Generate x86 assembly
    - Stage 3: Generate LLVM IR
    - Validate all three stages for consistency
    """
    print("\n" + "=" * 70)
    print("Example 1: Simple Addition (100 + 200)")
    print("=" * 70)
    
    # ─── Type Consistency ───
    type_result = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=16,  # 100, 200 fit in 16 bits
        operand_1_value=100,
        operand_2_value=200,
        register_size=32,      # EAX (32-bit register)
        llvm_ir_type="i32",
    )
    
    print(f"\n[Type Consistency]")
    print(f"  ✓ Consistent: {type_result.is_consistent}")
    print(f"  Confidence: {type_result.confidence:.1%}")
    if not type_result.is_consistent:
        for v in type_result.violations:
            print(f"  ✗ {v}")
    
    # ─── Operator Consistency ───
    operator_result = check_operator_consistency(
        nl_keyword="더하기",
        nl_confidence=0.98,
        asm_mnemonic="ADD",
        bitstream="00000001_01100100_11001000",  # 0x01_0x64_0xC8
        llvm_op_name="add",
    )
    
    print(f"\n[Operator Consistency]")
    print(f"  ✓ Consistent: {operator_result.is_consistent}")
    print(f"  Score: {operator_result.consistency_score:.1%}")
    if not operator_result.is_consistent:
        for v in operator_result.violations:
            print(f"  ✗ {v}")
    
    # ─── Result Consistency ───
    result_result = check_result_consistency(
        path_a_result=300,
        path_a_primary_reg=300,
        path_a_secondary_reg=0,
        path_a_bitstream="00000001_01100100_11001000_100101100",
        path_b_result=300,
        path_b_ir_register=300,
        path_b_ir_code="add i32 100, 200",
        strict_mode=True,
    )
    
    print(f"\n[Result Consistency]")
    print(f"  ✓ Consistent: {result_result.is_consistent}")
    print(f"  Coherence: {result_result.coherence_score:.1%}")
    if not result_result.is_consistent:
        for v in result_result.violations:
            print(f"  ✗ {v}")
    
    # ─── Unified Gate ───
    gate = ROCConsistencyGate()
    unified_report = gate.verify_pipeline(
        tool_name="organic_adder",
        type_score=type_result.confidence,
        operator_score=operator_result.consistency_score,
        result_score=result_result.coherence_score,
    )
    
    print(f"\n[Unified Gate Verdict]")
    print(f"  Weighted Score: {unified_report.weighted_score:.1%}")
    print(f"  Overall Status: {'✓ PASS' if unified_report.overall_consistent else '✗ FAIL'}")


def example_2_bitwise_operation():
    """
    Example 2: Bitwise AND (0xFF & 0x0F = 0x0F)
    
    Scenario: Compile "255와 15를 비트AND" (Bitwise AND 255 and 15)
    
    Tests bitwise operation consistency across dual paths.
    """
    print("\n" + "=" * 70)
    print("Example 2: Bitwise AND (0xFF & 0x0F = 0x0F)")
    print("=" * 70)
    
    # ─── Type Consistency ───
    type_result = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=8,
        operand_1_value=0xFF,
        operand_2_value=0x0F,
        register_size=32,
        llvm_ir_type="i32",
    )
    
    print(f"\n[Type Consistency] {type_result.confidence:.1%}")
    
    # ─── Operator Consistency ───
    operator_result = check_operator_consistency(
        nl_keyword="비트AND",
        nl_confidence=0.92,
        asm_mnemonic="AND",
        bitstream="00000101_11111111_00001111",
        llvm_op_name="and",
    )
    
    print(f"[Operator Consistency] {operator_result.consistency_score:.1%}")
    
    # ─── Result Consistency ───
    result_result = check_result_consistency(
        path_a_result=0x0F,     # 15
        path_a_primary_reg=0x0F,
        path_a_secondary_reg=0x00,
        path_a_bitstream="00000101_11111111_00001111_00001111",
        path_b_result=0x0F,
        path_b_ir_register=0x0F,
        path_b_ir_code="and i32 255, 15",
        strict_mode=True,
    )
    
    print(f"[Result Consistency] {result_result.coherence_score:.1%}")
    
    # ─── Unified Gate ───
    gate = ROCConsistencyGate()
    unified_report = gate.verify_pipeline(
        tool_name="organic_bitwise_and",
        type_score=type_result.confidence,
        operator_score=operator_result.consistency_score,
        result_score=result_result.coherence_score,
    )
    
    print(f"[Unified Gate] {'✓ PASS' if unified_report.overall_consistent else '✗ FAIL'} ({unified_report.weighted_score:.1%})")


def example_3_type_mismatch_detection():
    """
    Example 3: Type Mismatch Detection
    
    Scenario: Hardware compiled for 32-bit, but LLVM type is i64
    
    This demonstrates how the validator catches inconsistencies.
    """
    print("\n" + "=" * 70)
    print("Example 3: Type Mismatch Detection")
    print("=" * 70)
    
    # ─── Type Consistency (will FAIL) ───
    type_result = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=32,
        operand_1_value=1000,
        operand_2_value=2000,
        register_size=32,      # 32-bit register
        llvm_ir_type="i64",    # But LLVM type is 64-bit → MISMATCH
    )
    
    print(f"\n[Type Consistency] {type_result.confidence:.1%}")
    if not type_result.is_consistent:
        print(f"  ✗ Violations:")
        for v in type_result.violations:
            print(f"    - {v}")
    
    # ─── Operator Consistency (still OK) ───
    operator_result = check_operator_consistency(
        nl_keyword="곱하기",
        nl_confidence=0.90,
        asm_mnemonic="MUL",
        bitstream="00000011_...",
        llvm_op_name="mul",
    )
    
    print(f"\n[Operator Consistency] {operator_result.consistency_score:.1%}")
    
    # ─── Result Consistency (affected by type mismatch) ───
    result_result = check_result_consistency(
        path_a_result=2000000,
        path_a_primary_reg=2000000,
        path_a_secondary_reg=0,
        path_a_bitstream="...",
        path_b_result=2000000,
        path_b_ir_register=2000000,
        path_b_ir_code="mul i64 1000, 2000",
        strict_mode=True,
    )
    
    print(f"[Result Consistency] {result_result.coherence_score:.1%}")
    
    # ─── Unified Gate (will FAIL due to type issue) ───
    gate = ROCConsistencyGate()
    unified_report = gate.verify_pipeline(
        tool_name="problematic_multiplier",
        type_score=type_result.confidence,
        operator_score=operator_result.consistency_score,
        result_score=result_result.coherence_score,
    )
    
    print(f"\n[Unified Gate]")
    print(f"  Status: {'✓ PASS' if unified_report.overall_consistent else '✗ FAIL'}")
    print(f"  Weighted Score: {unified_report.weighted_score:.1%}")
    print(f"  Type: {'✓' if unified_report.type_consistency_passed else '✗'}")
    print(f"  Operator: {'✓' if unified_report.operator_consistency_passed else '✗'}")
    print(f"  Result: {'✓' if unified_report.result_consistency_passed else '✗'}")


def example_4_operator_mismatch_detection():
    """
    Example 4: Operator Mismatch Detection
    
    Scenario: NL says "더하기" (add) but ASM is SUB
    
    Classic opcode extraction error.
    """
    print("\n" + "=" * 70)
    print("Example 4: Operator Mismatch Detection")
    print("=" * 70)
    
    # ─── Type Consistency (OK) ───
    type_result = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=32,
        operand_1_value=500,
        operand_2_value=300,
        register_size=32,
        llvm_ir_type="i32",
    )
    
    print(f"\n[Type Consistency] ✓ {type_result.confidence:.1%}")
    
    # ─── Operator Consistency (will FAIL) ───
    operator_result = check_operator_consistency(
        nl_keyword="더하기",    # Says "ADD"
        nl_confidence=0.95,
        asm_mnemonic="SUB",    # But ASM is "SUB" → MISMATCH!
        bitstream="00000001_01111110_100101100",  # Bitstream says "ADD" (opcode 0x01)
        llvm_op_name="add",    # LLVM says "add"
    )
    
    print(f"\n[Operator Consistency] {operator_result.consistency_score:.1%}")
    if not operator_result.is_consistent:
        print(f"  ✗ Violations:")
        for v in operator_result.violations:
            print(f"    - {v}")
    
    # ─── Result Consistency (affected) ───
    # Path A would compute 500 - 300 = 200 (SUB, wrong!)
    # Path B would compute 500 + 300 = 800 (ADD, correct)
    result_result = check_result_consistency(
        path_a_result=200,     # Wrong: 500 - 300
        path_a_primary_reg=200,
        path_a_secondary_reg=0,
        path_a_bitstream="...",
        path_b_result=800,     # Correct: 500 + 300
        path_b_ir_register=800,
        path_b_ir_code="add i32 500, 300",
        strict_mode=True,
    )
    
    print(f"\n[Result Consistency] {result_result.coherence_score:.1%}")
    if not result_result.is_consistent:
        print(f"  ✗ Violations:")
        for v in result_result.violations:
            print(f"    - {v}")
    
    # ─── Unified Gate (will FAIL) ───
    gate = ROCConsistencyGate()
    unified_report = gate.verify_pipeline(
        tool_name="buggy_calculator",
        type_score=type_result.confidence,
        operator_score=operator_result.consistency_score,
        result_score=result_result.coherence_score,
        operator_violations=[
            "Opcode→ASM mismatch: ADD should map to ADD, but got SUB",
            "ASM↔LLVM equivalence broken: ADD and SUB are not semantically equivalent",
        ],
        result_violations=[
            "Numerical result mismatch: Path A = 200, Path B = 800",
        ],
    )
    
    print(f"\n[Unified Gate Report]")
    print(gate.format_report(unified_report))


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  VERITAS ROC Consistency Gate — Comprehensive Examples".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")
    
    example_1_simple_addition()
    example_2_bitwise_operation()
    example_3_type_mismatch_detection()
    example_4_operator_mismatch_detection()
    
    print("\n" + "=" * 70)
    print("Examples Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
