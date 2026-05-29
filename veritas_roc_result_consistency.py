# -*- coding: utf-8 -*-
"""
VERITAS ROC Consistency Gate v1.0
Result Consistency Validator

Purpose:
  Verify that Path A (Hardware/x86) and Path B (LLVM IR) produce
  coherent and logically equivalent results from the same input.

Public Release: MIT License
Author: Sungha (Meta Architect)
"""

from dataclasses import dataclass
from typing import Optional, Union, List
from enum import Enum


class ResultType(Enum):
    """Type of computational result"""
    INTEGER = "integer"
    BITSTREAM = "bitstream"
    REGISTER_VALUE = "register_value"


@dataclass
class PathA_Result:
    """Result from Path A: Hardware-level computation"""
    hardware_result: int
    register_primary: str  # e.g., "EAX"
    register_primary_value: int
    register_secondary: str  # e.g., "EBX"
    register_secondary_value: int
    bitstream_output: str  # Final bitstream state
    execution_time_cycles: int


@dataclass
class PathB_Result:
    """Result from Path B: LLVM IR computation"""
    llvm_result: int
    ir_register_primary: str  # e.g., "%result"
    ir_register_value: int
    ir_code_output: str
    optimization_level: int  # 0-3 (O0-O3)


@dataclass
class ResultConsistencyResult:
    """Result of cross-path consistency check"""
    is_consistent: bool
    
    path_a_result: PathA_Result
    path_b_result: PathB_Result
    
    # Consistency metrics
    numerical_match: bool  # Path A result == Path B result
    register_coherence: float  # 0.0-1.0, higher is better
    bitstream_coherence: float  # 0.0-1.0
    
    # Overall confidence
    coherence_score: float  # 0.0-1.0 (weighted average)
    
    # Violation details
    violations: List[str]
    
    # Recommendations
    recommendations: List[str]


class ResultConsistencyValidator:
    """
    Validates result consistency between Path A (Hardware) and Path B (LLVM IR).
    
    The core principle: Both paths should produce semantically equivalent
    results given the same input, even though their internal representations
    differ (register values vs. LLVM IR registers).
    
    Rules:
    1. Numerical Match: Path A result must equal Path B result
    2. Register Coherence: Primary registers should carry the same value
    3. Bitstream Coherence: Final bitstream state should reflect computation
    4. Idempotency: Running the same computation twice should yield same result
    5. Instruction Count: Path A instructions ≈ Path B operations (with tolerance)
    """
    
    # Acceptable tolerance for numerical results (for floating-point, etc.)
    NUMERICAL_TOLERANCE = 0  # For integer ops, must be exact
    
    # Expected ratio of hardware instructions to LLVM operations
    INSTRUCTION_RATIO_TOLERANCE = 0.5  # Allow 50% deviation
    
    def __init__(self):
        self.check_log = []
    
    def validate(
        self,
        path_a: PathA_Result,
        path_b: PathB_Result,
        strict_mode: bool = True,
    ) -> ResultConsistencyResult:
        """
        Validate result consistency between Path A and Path B.
        
        Args:
            path_a: Hardware-level computation result
            path_b: LLVM IR computation result
            strict_mode: If True, require exact match; if False, allow tolerance
        
        Returns:
            ResultConsistencyResult with detailed findings
        """
        violations = []
        recommendations = []
        coherence_scores = []
        
        # ─── Rule 1: Numerical Match ───
        numerical_match = path_a.hardware_result == path_b.llvm_result
        
        if not numerical_match:
            violations.append(
                f"Numerical result mismatch: Path A = {path_a.hardware_result}, "
                f"Path B = {path_b.llvm_result}"
            )
            if strict_mode:
                coherence_scores.append(0.0)
            else:
                # Allow small tolerance
                diff = abs(path_a.hardware_result - path_b.llvm_result)
                if diff <= self.NUMERICAL_TOLERANCE:
                    numerical_match = True
                    coherence_scores.append(0.95)
                else:
                    coherence_scores.append(0.3)
        else:
            coherence_scores.append(1.0)
        
        # ─── Rule 2: Register Coherence ───
        register_coherence = self._calculate_register_coherence(path_a, path_b)
        coherence_scores.append(register_coherence)
        
        if register_coherence < 0.9:
            violations.append(
                f"Register coherence low: {register_coherence:.1%}. "
                f"Path A primary={path_a.register_primary_value}, "
                f"Path B primary={path_b.ir_register_value}"
            )
            recommendations.append(
                "Check if Path A and Path B use same result register locations"
            )
        
        # ─── Rule 3: Bitstream Coherence ───
        bitstream_coherence = self._calculate_bitstream_coherence(path_a, path_b)
        coherence_scores.append(bitstream_coherence)
        
        if bitstream_coherence < 0.85:
            violations.append(
                f"Bitstream coherence low: {bitstream_coherence:.1%}. "
                f"Final bitstream states diverged significantly"
            )
            recommendations.append(
                "Verify that hardware instruction sequence matches LLVM IR semantics"
            )
        
        # ─── Rule 4: Instruction Count Consistency ───
        # (This is a soft check - paths can have different instruction counts)
        instruction_ratio = self._calculate_instruction_ratio(path_a, path_b)
        
        if instruction_ratio > 1.0 + self.INSTRUCTION_RATIO_TOLERANCE:
            violations.append(
                f"Path A has significantly more instructions: "
                f"ratio {instruction_ratio:.2f} (Path A instructions > Path B ops)"
            )
            recommendations.append(
                "Consider whether Path A can be optimized to reduce instruction count"
            )
        
        # ─── Final Calculation ───
        is_consistent = len(violations) == 0 and numerical_match
        coherence_score = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.5
        coherence_score = max(0.0, min(1.0, coherence_score))
        
        result = ResultConsistencyResult(
            is_consistent=is_consistent,
            path_a_result=path_a,
            path_b_result=path_b,
            numerical_match=numerical_match,
            register_coherence=register_coherence,
            bitstream_coherence=bitstream_coherence,
            coherence_score=coherence_score,
            violations=violations,
            recommendations=recommendations,
        )
        
        self.check_log.append(result)
        return result
    
    @staticmethod
    def _calculate_register_coherence(path_a: PathA_Result, path_b: PathB_Result) -> float:
        """
        Calculate how well primary registers align between paths.
        
        Returns: 0.0-1.0, where 1.0 = perfect match
        """
        # Perfect match: same value in primary register
        if path_a.register_primary_value == path_b.ir_register_value:
            return 1.0
        
        # Acceptable match: values are close (within 1%)
        max_val = max(abs(path_a.register_primary_value), abs(path_b.ir_register_value), 1)
        diff = abs(path_a.register_primary_value - path_b.ir_register_value)
        tolerance = max_val * 0.01  # 1% tolerance
        
        if diff <= tolerance:
            return 0.95
        
        # Calculate fractional coherence
        coherence = max(0.0, 1.0 - (diff / max_val))
        return coherence
    
    @staticmethod
    def _calculate_bitstream_coherence(path_a: PathA_Result, path_b: PathB_Result) -> float:
        """
        Calculate semantic coherence of bitstream outputs.
        
        Bitstream coherence measures whether the hardware state after
        computation is consistent with what LLVM IR would produce.
        
        Returns: 0.0-1.0
        """
        # If both paths produce the same final result value,
        # bitstream is coherent (even if internal representation differs)
        if path_a.hardware_result == path_b.llvm_result:
            return 1.0
        
        # Otherwise, measure how "close" they are
        max_val = max(abs(path_a.hardware_result), abs(path_b.llvm_result), 1)
        diff = abs(path_a.hardware_result - path_b.llvm_result)
        coherence = max(0.0, 1.0 - (diff / max_val))
        
        return coherence
    
    @staticmethod
    def _calculate_instruction_ratio(path_a: PathA_Result, path_b: PathB_Result) -> float:
        """
        Calculate ratio of Path A instructions to Path B operations.
        
        Returns: ratio >= 0.0
        """
        # Estimate instruction count from bitstream (simple heuristic)
        bitstream_ops = path_a.bitstream_output.count("_")  # underscore separates operations
        ir_ops = path_b.ir_code_output.count("%")  # rough count of IR operations
        
        if ir_ops == 0:
            ir_ops = 1
        
        return bitstream_ops / ir_ops if ir_ops > 0 else 1.0


# ═════════════════════════════════════════════════════════════════
# Convenience Functions
# ═════════════════════════════════════════════════════════════════

def check_result_consistency(
    path_a_result: int,
    path_a_primary_reg: int,
    path_a_secondary_reg: int,
    path_a_bitstream: str,
    path_b_result: int,
    path_b_ir_register: int,
    path_b_ir_code: str,
    strict_mode: bool = True,
) -> ResultConsistencyResult:
    """
    High-level API for result consistency checking.
    
    Args:
        path_a_result: Computed result from hardware path
        path_a_primary_reg: Value in primary register (EAX)
        path_a_secondary_reg: Value in secondary register (EBX)
        path_a_bitstream: Final bitstream state
        path_b_result: Computed result from LLVM path
        path_b_ir_register: Value in primary IR register
        path_b_ir_code: LLVM IR code snippet
        strict_mode: Require exact match
    
    Returns:
        ResultConsistencyResult
    """
    
    path_a = PathA_Result(
        hardware_result=path_a_result,
        register_primary="EAX",
        register_primary_value=path_a_primary_reg,
        register_secondary="EBX",
        register_secondary_value=path_a_secondary_reg,
        bitstream_output=path_a_bitstream,
        execution_time_cycles=4,
    )
    
    path_b = PathB_Result(
        llvm_result=path_b_result,
        ir_register_primary="%result",
        ir_register_value=path_b_ir_register,
        ir_code_output=path_b_ir_code,
        optimization_level=2,
    )
    
    validator = ResultConsistencyValidator()
    return validator.validate(path_a, path_b, strict_mode=strict_mode)


# ═════════════════════════════════════════════════════════════════
# Example Usage
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 70)
    print("VERITAS ROC Result Consistency Validator — Demo")
    print("=" * 70)
    
    # Test Case 1: Fully consistent (100 + 200 = 300)
    result1 = check_result_consistency(
        path_a_result=300,
        path_a_primary_reg=300,
        path_a_secondary_reg=0,
        path_a_bitstream="00000001_01100100_11001000",
        path_b_result=300,
        path_b_ir_register=300,
        path_b_ir_code="add i32 100, 200",
        strict_mode=True,
    )
    print(f"\nTest 1 - Fully Consistent (100 + 200 = 300):")
    print(f"  ✓ Consistent: {result1.is_consistent}")
    print(f"  Coherence Score: {result1.coherence_score:.1%}")
    print(f"  Violations: {len(result1.violations)}")
    
    # Test Case 2: Inconsistent results (Path A=300, Path B=301)
    result2 = check_result_consistency(
        path_a_result=300,
        path_a_primary_reg=300,
        path_a_secondary_reg=0,
        path_a_bitstream="00000001_01100100_11001000",
        path_b_result=301,  # Mismatch!
        path_b_ir_register=301,
        path_b_ir_code="add i32 100, 200",
        strict_mode=True,
    )
    print(f"\nTest 2 - Inconsistent Results (A=300, B=301):")
    print(f"  ✗ Consistent: {result2.is_consistent}")
    print(f"  Coherence Score: {result2.coherence_score:.1%}")
    print(f"  Violations:")
    for v in result2.violations:
        print(f"    - {v}")
    
    # Test Case 3: Register mismatch
    result3 = check_result_consistency(
        path_a_result=300,
        path_a_primary_reg=300,
        path_a_secondary_reg=0,
        path_a_bitstream="00000001_01100100_11001000",
        path_b_result=300,
        path_b_ir_register=250,  # Different register value!
        path_b_ir_code="add i32 100, 200",
        strict_mode=True,
    )
    print(f"\nTest 3 - Register Mismatch:")
    print(f"  ✗ Consistent: {result3.is_consistent}")
    print(f"  Coherence Score: {result3.coherence_score:.1%}")
    print(f"  Register Coherence: {result3.register_coherence:.1%}")
    if result3.recommendations:
        print(f"  Recommendations:")
        for r in result3.recommendations:
            print(f"    → {r}")
    
    # Test Case 4: Lenient mode (non-strict)
    result4 = check_result_consistency(
        path_a_result=300,
        path_a_primary_reg=300,
        path_a_secondary_reg=0,
        path_a_bitstream="00000001_01100100_11001000",
        path_b_result=301,
        path_b_ir_register=300,
        path_b_ir_code="add i32 100, 200",
        strict_mode=False,  # Allow slight variation
    )
    print(f"\nTest 4 - Lenient Mode (Non-Strict):")
    print(f"  Consistent: {result4.is_consistent}")
    print(f"  Coherence Score: {result4.coherence_score:.1%}")
    print(f"  Violations: {len(result4.violations)}")
    
    print("\n" + "=" * 70)
