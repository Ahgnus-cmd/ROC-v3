# -*- coding: utf-8 -*-
"""
VERITAS ROC Consistency Gate v1.0
Type Consistency Validator

Purpose:
  Verify that Stage 2 (Hardware) and Stage 3 (LLVM IR) output types
  are coherent and compatible across the dual-path pipeline.

Public Release: MIT License
Author: Sungha (Meta Architect)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Tuple
from enum import Enum


class BitWidth(Enum):
    """Hardware bit width classification"""
    BIT_8 = 8
    BIT_16 = 16
    BIT_32 = 32
    BIT_64 = 64


class LLVMType(Enum):
    """LLVM IR type classification"""
    I32 = "i32"
    I64 = "i64"
    I128 = "i128"


@dataclass
class HardwareTypeSignature:
    """Type signature from Path A (Hardware)"""
    bit_width: BitWidth
    register_size: int  # EAX=32, RAX=64, etc
    operand_1_bits: int
    operand_2_bits: int
    
    def __post_init__(self):
        if self.operand_1_bits > self.bit_width.value:
            raise ValueError(
                f"Operand 1 ({self.operand_1_bits}b) exceeds bit_width ({self.bit_width.value}b)"
            )
        if self.operand_2_bits > self.bit_width.value:
            raise ValueError(
                f"Operand 2 ({self.operand_2_bits}b) exceeds bit_width ({self.bit_width.value}b)"
            )


@dataclass
class LLVMTypeSignature:
    """Type signature from Path B (LLVM IR)"""
    llvm_type: LLVMType
    bit_width: int  # derived from llvm_type
    operand_1_type: str  # "i32", "i64", etc
    operand_2_type: str
    
    def __post_init__(self):
        type_bit_map = {"i32": 32, "i64": 64, "i128": 128}
        self.bit_width = type_bit_map.get(self.llvm_type.value, 32)


@dataclass
class TypeConsistencyResult:
    """Result of type consistency check"""
    is_consistent: bool
    hardware_signature: HardwareTypeSignature
    llvm_signature: LLVMTypeSignature
    
    # Detailed findings
    bit_width_match: bool
    operand_1_match: bool
    operand_2_match: bool
    
    # Confidence score (0.0 - 1.0)
    confidence: float
    
    # Violation details
    violations: list[str]


class TypeConsistencyValidator:
    """
    Validates type consistency between Path A (Hardware) and Path B (LLVM IR).
    
    Rules:
    1. Hardware bit_width must map to LLVM type
       - 8-bit → i32 (minimum in LLVM)
       - 16-bit → i32
       - 32-bit → i32
       - 64-bit → i64
    
    2. Operand types must be consistent
       - If op1 is 16-bit in hardware, it must fit in LLVM type
       - No operand can exceed target type capacity
    
    3. Coherence score penalizes type mismatches
    """
    
    # Mapping rules: hardware bit_width → valid LLVM types
    VALID_TYPE_MAPPINGS = {
        BitWidth.BIT_8.value: [LLVMType.I32],
        BitWidth.BIT_16.value: [LLVMType.I32, LLVMType.I64],
        BitWidth.BIT_32.value: [LLVMType.I32, LLVMType.I64],
        BitWidth.BIT_64.value: [LLVMType.I64],
    }
    
    def __init__(self):
        self.check_log = []
    
    def validate(
        self,
        hw_sig: HardwareTypeSignature,
        llvm_sig: LLVMTypeSignature
    ) -> TypeConsistencyResult:
        """
        Validate type consistency between hardware and LLVM paths.
        
        Returns:
            TypeConsistencyResult with detailed findings
        """
        violations = []
        confidence = 1.0
        
        # ─── Rule 1: Bit width mapping ───
        hw_bits = hw_sig.bit_width.value
        llvm_bits = llvm_sig.bit_width
        
        valid_types = self.VALID_TYPE_MAPPINGS.get(hw_bits, [])
        bit_width_match = llvm_sig.llvm_type in valid_types
        
        if not bit_width_match:
            violations.append(
                f"Bit width mismatch: Hardware {hw_bits}b → LLVM {llvm_sig.llvm_type.value} "
                f"(expected one of {[t.value for t in valid_types]})"
            )
            confidence -= 0.25
        
        # ─── Rule 2: Operand type consistency ───
        operand_1_match = self._validate_operand(
            hw_sig.operand_1_bits, hw_bits, llvm_bits
        )
        if not operand_1_match:
            violations.append(
                f"Operand 1 type mismatch: Hardware {hw_sig.operand_1_bits}b "
                f"doesn't fit in LLVM {llvm_sig.llvm_type.value} ({llvm_bits}b)"
            )
            confidence -= 0.15
        
        operand_2_match = self._validate_operand(
            hw_sig.operand_2_bits, hw_bits, llvm_bits
        )
        if not operand_2_match:
            violations.append(
                f"Operand 2 type mismatch: Hardware {hw_sig.operand_2_bits}b "
                f"doesn't fit in LLVM {llvm_sig.llvm_type.value} ({llvm_bits}b)"
            )
            confidence -= 0.15
        
        # ─── Rule 3: Register-to-type coherence ───
        register_coherence = self._check_register_coherence(hw_sig, llvm_sig)
        if not register_coherence:
            violations.append(
                f"Register size incoherent: Hardware register {hw_sig.register_size}b "
                f"vs LLVM type {llvm_bits}b"
            )
            confidence -= 0.10
        
        is_consistent = len(violations) == 0
        confidence = max(0.0, confidence)
        
        result = TypeConsistencyResult(
            is_consistent=is_consistent,
            hardware_signature=hw_sig,
            llvm_signature=llvm_sig,
            bit_width_match=bit_width_match,
            operand_1_match=operand_1_match,
            operand_2_match=operand_2_match,
            confidence=confidence,
            violations=violations,
        )
        
        self.check_log.append(result)
        return result
    
    @staticmethod
    def _validate_operand(operand_bits: int, hw_bits: int, llvm_bits: int) -> bool:
        """Check if operand fits in both hardware and LLVM contexts"""
        return operand_bits <= hw_bits and operand_bits <= llvm_bits
    
    @staticmethod
    def _check_register_coherence(hw_sig: HardwareTypeSignature, llvm_sig: LLVMTypeSignature) -> bool:
        """Check if register size matches LLVM type bitwidth"""
        # Example: 32-bit registers (EAX) should map to i32, 64-bit (RAX) to i64
        return hw_sig.register_size == llvm_sig.bit_width


# ═════════════════════════════════════════════════════════════════
# Convenience Functions
# ═════════════════════════════════════════════════════════════════

def check_hardware_to_llvm_type_consistency(
    hardware_bitwidth: int,
    operand_1_value: int,
    operand_2_value: int,
    register_size: int,
    llvm_ir_type: str,
) -> TypeConsistencyResult:
    """
    High-level API: Check type consistency with raw values.
    
    Args:
        hardware_bitwidth: 8, 16, 32, or 64
        operand_1_value: First operand (will determine bit requirement)
        operand_2_value: Second operand
        register_size: Hardware register size (32 for EAX, 64 for RAX)
        llvm_ir_type: "i32" or "i64"
    
    Returns:
        TypeConsistencyResult
    """
    # Determine bit width needed for operands
    op1_bits = operand_1_value.bit_length() or 1
    op2_bits = operand_2_value.bit_length() or 1
    
    # Ensure we don't exceed hardware bit width
    op1_bits = min(op1_bits, hardware_bitwidth)
    op2_bits = min(op2_bits, hardware_bitwidth)
    
    hw_sig = HardwareTypeSignature(
        bit_width=BitWidth(hardware_bitwidth),
        register_size=register_size,
        operand_1_bits=op1_bits,
        operand_2_bits=op2_bits,
    )
    
    llvm_type = LLVMType.I32 if llvm_ir_type == "i32" else LLVMType.I64
    llvm_sig = LLVMTypeSignature(
        llvm_type=llvm_type,
        operand_1_type=llvm_ir_type,
        operand_2_type=llvm_ir_type,
    )
    
    validator = TypeConsistencyValidator()
    return validator.validate(hw_sig, llvm_sig)


# ═════════════════════════════════════════════════════════════════
# Example Usage
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("VERITAS ROC Type Consistency Validator — Demo")
    print("=" * 70)
    
    # Test Case 1: Consistent (32-bit operands in 32-bit register + i32 LLVM)
    result1 = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=32,
        operand_1_value=100,
        operand_2_value=200,
        register_size=32,
        llvm_ir_type="i32",
    )
    print(f"\nTest 1 - Consistent 32-bit:")
    print(f"  ✓ Consistent: {result1.is_consistent}")
    print(f"  Confidence: {result1.confidence:.1%}")
    print(f"  Violations: {len(result1.violations)}")
    
    # Test Case 2: Inconsistent (32-bit register but i64 LLVM type mismatch)
    result2 = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=32,
        operand_1_value=100,
        operand_2_value=200,
        register_size=32,
        llvm_ir_type="i64",
    )
    print(f"\nTest 2 - Inconsistent (32-bit hw, i64 LLVM):")
    print(f"  ✗ Consistent: {result2.is_consistent}")
    print(f"  Confidence: {result2.confidence:.1%}")
    print(f"  Violations:")
    for v in result2.violations:
        print(f"    - {v}")
    
    # Test Case 3: 64-bit consistency
    result3 = check_hardware_to_llvm_type_consistency(
        hardware_bitwidth=64,
        operand_1_value=10000000,
        operand_2_value=20000000,
        register_size=64,
        llvm_ir_type="i64",
    )
    print(f"\nTest 3 - Consistent 64-bit:")
    print(f"  ✓ Consistent: {result3.is_consistent}")
    print(f"  Confidence: {result3.confidence:.1%}")
    
    print("\n" + "=" * 70)
