# -*- coding: utf-8 -*-
"""
VERITAS ROC Consistency Gate v1.0
Unified Gate — Integrated Consistency Verification

Purpose:
  Orchestrate Type, Operator, and Result validators into a single
  pipeline consistency gate for ROC v3.

Public Release: MIT License
Author: Sungha (Meta Architect)
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List
from enum import Enum

# Import the three validators
# (Normally would: from veritas_roc_* import ...)
# For this demo, they're treated as separate modules


@dataclass
class ROCPipelineConsistencyReport:
    """Comprehensive consistency report for entire ROC pipeline"""
    
    # Stage identity
    tool_name: str
    pipeline_version: str = "3.0"
    
    # Individual validator results
    type_consistency_passed: bool = False
    operator_consistency_passed: bool = False
    result_consistency_passed: bool = False
    
    # Unified verdict
    overall_consistent: bool = False
    
    # Scores
    type_score: float = 0.0
    operator_score: float = 0.0
    result_score: float = 0.0
    weighted_score: float = 0.0
    
    # Weights for each validator (can be tuned)
    type_weight: float = 0.33
    operator_weight: float = 0.33
    result_weight: float = 0.34
    
    # Detailed findings
    all_violations: List[str] = field(default_factory=list)
    all_recommendations: List[str] = field(default_factory=list)
    
    # Per-stage details (for debugging)
    type_details: Dict = field(default_factory=dict)
    operator_details: Dict = field(default_factory=dict)
    result_details: Dict = field(default_factory=dict)
    
    # Timestamp
    timestamp: Optional[str] = None


class ROCConsistencyGate:
    """
    Unified consistency gate for ROC v3.
    
    Flow:
    1. Type consistency (Stage 2/3 type alignment)
    2. Operator consistency (Stage 1/2/3 opcode alignment)
    3. Result consistency (Path A ↔ Path B result alignment)
    4. Aggregate scores and generate final verdict
    
    Passing Criteria:
    - All three validators must pass (or reach threshold)
    - Weighted score must be ≥ 0.85 (default)
    """
    
    def __init__(
        self,
        type_weight: float = 0.33,
        operator_weight: float = 0.33,
        result_weight: float = 0.34,
        passing_threshold: float = 0.85,
    ):
        """
        Initialize the unified consistency gate.
        
        Args:
            type_weight: Weight for type consistency score
            operator_weight: Weight for operator consistency score
            result_weight: Weight for result consistency score
            passing_threshold: Minimum weighted score to pass
        """
        self.type_weight = type_weight
        self.operator_weight = operator_weight
        self.result_weight = result_weight
        self.passing_threshold = passing_threshold
        
        # Validate weights sum to 1.0
        total_weight = type_weight + operator_weight + result_weight
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to ~1.0, got {total_weight}")
    
    def verify_pipeline(
        self,
        tool_name: str,
        type_score: float,
        operator_score: float,
        result_score: float,
        type_violations: List[str] = None,
        operator_violations: List[str] = None,
        result_violations: List[str] = None,
        type_recommendations: List[str] = None,
        operator_recommendations: List[str] = None,
        result_recommendations: List[str] = None,
    ) -> ROCPipelineConsistencyReport:
        """
        Unified verification of ROC pipeline consistency.
        
        Args:
            tool_name: Name of the tool being compiled
            type_score: Type consistency score (0.0-1.0)
            operator_score: Operator consistency score (0.0-1.0)
            result_score: Result consistency score (0.0-1.0)
            *_violations: Lists of violations from each validator
            *_recommendations: Lists of recommendations from each validator
        
        Returns:
            ROCPipelineConsistencyReport
        """
        
        violations = []
        recommendations = []
        
        # Collect violations
        if type_violations:
            violations.extend(type_violations)
        if operator_violations:
            violations.extend(operator_violations)
        if result_violations:
            violations.extend(result_violations)
        
        # Collect recommendations
        if type_recommendations:
            recommendations.extend(type_recommendations)
        if operator_recommendations:
            recommendations.extend(operator_recommendations)
        if result_recommendations:
            recommendations.extend(result_recommendations)
        
        # Clamp scores to [0.0, 1.0]
        type_score = max(0.0, min(1.0, type_score))
        operator_score = max(0.0, min(1.0, operator_score))
        result_score = max(0.0, min(1.0, result_score))
        
        # Calculate weighted score
        weighted_score = (
            type_score * self.type_weight +
            operator_score * self.operator_weight +
            result_score * self.result_weight
        )
        
        # Determine pass/fail for each validator
        type_passed = type_score >= 0.85
        operator_passed = operator_score >= 0.85
        result_passed = result_score >= 0.85
        
        # Overall verdict
        overall_consistent = weighted_score >= self.passing_threshold
        
        # Create report
        report = ROCPipelineConsistencyReport(
            tool_name=tool_name,
            type_consistency_passed=type_passed,
            operator_consistency_passed=operator_passed,
            result_consistency_passed=result_passed,
            overall_consistent=overall_consistent,
            type_score=type_score,
            operator_score=operator_score,
            result_score=result_score,
            weighted_score=weighted_score,
            type_weight=self.type_weight,
            operator_weight=self.operator_weight,
            result_weight=self.result_weight,
            all_violations=violations,
            all_recommendations=recommendations,
            type_details={
                "score": type_score,
                "passed": type_passed,
                "violations_count": len(type_violations or []),
            },
            operator_details={
                "score": operator_score,
                "passed": operator_passed,
                "violations_count": len(operator_violations or []),
            },
            result_details={
                "score": result_score,
                "passed": result_passed,
                "violations_count": len(result_violations or []),
            },
        )
        
        return report
    
    def format_report(self, report: ROCPipelineConsistencyReport) -> str:
        """Format report as human-readable string"""
        lines = [
            "=" * 70,
            "VERITAS ROC Consistency Gate Report",
            "=" * 70,
            f"Tool: {report.tool_name}",
            f"Version: {report.pipeline_version}",
            "",
            "Validator Status:",
            f"  [{'✓' if report.type_consistency_passed else '✗'}] Type Consistency      {report.type_score:.1%}",
            f"  [{'✓' if report.operator_consistency_passed else '✗'}] Operator Consistency  {report.operator_score:.1%}",
            f"  [{'✓' if report.result_consistency_passed else '✗'}] Result Consistency    {report.result_score:.1%}",
            "",
            f"Weighted Score: {report.weighted_score:.1%}",
            f"Passing Threshold: {self.passing_threshold:.1%}",
            f"Overall Status: {'✓ PASS' if report.overall_consistent else '✗ FAIL'}",
            "",
        ]
        
        if report.all_violations:
            lines.extend([
                "Violations:",
                *[f"  • {v}" for v in report.all_violations],
                "",
            ])
        
        if report.all_recommendations:
            lines.extend([
                "Recommendations:",
                *[f"  → {r}" for r in report.all_recommendations],
                "",
            ])
        
        lines.append("=" * 70)
        
        return "\n".join(lines)


# ═════════════════════════════════════════════════════════════════
# Example Usage
# ═════════════════════════════════════════════════════════════════

def main():
    """Demo: Complete ROC pipeline consistency verification"""
    
    print("=" * 70)
    print("VERITAS ROC Consistency Gate — Unified Demo")
    print("=" * 70)
    
    gate = ROCConsistencyGate(
        type_weight=0.33,
        operator_weight=0.33,
        result_weight=0.34,
        passing_threshold=0.85,
    )
    
    # ─── Scenario 1: Fully Consistent Pipeline ───
    print("\n[Scenario 1] Fully Consistent Pipeline")
    report1 = gate.verify_pipeline(
        tool_name="bio_organic_adder_v1",
        type_score=1.0,
        operator_score=1.0,
        result_score=1.0,
        type_violations=[],
        operator_violations=[],
        result_violations=[],
        type_recommendations=[],
        operator_recommendations=[],
        result_recommendations=[],
    )
    print(gate.format_report(report1))
    
    # ─── Scenario 2: Type Consistency Issue ───
    print("\n[Scenario 2] Type Mismatch (32-bit hardware vs i64 LLVM)")
    report2 = gate.verify_pipeline(
        tool_name="bio_organic_multiplier_v1",
        type_score=0.70,
        operator_score=1.0,
        result_score=0.95,
        type_violations=[
            "Bit width mismatch: Hardware 32b → LLVM i64",
            "Register size incoherent: Hardware register 32b vs LLVM type 64b",
        ],
        operator_violations=[],
        result_violations=[],
        operator_recommendations=[],
        type_recommendations=[
            "Use i32 LLVM type for 32-bit hardware",
            "Verify register allocation matches type width",
        ],
        result_recommendations=[],
    )
    print(gate.format_report(report2))
    
    # ─── Scenario 3: Operator Consistency Issue ───
    print("\n[Scenario 3] Opcode Mismatch (NL→ASM inconsistency)")
    report3 = gate.verify_pipeline(
        tool_name="bio_organic_calculator_v1",
        type_score=1.0,
        operator_score=0.50,
        result_score=0.85,
        type_violations=[],
        operator_violations=[
            "Opcode→ASM mismatch: ADD should map to ADD, but got SUB",
            "ASM↔LLVM equivalence broken: ADD and SUB are not semantically equivalent",
        ],
        result_violations=[],
        type_recommendations=[],
        operator_recommendations=[
            "Verify NL keyword extraction (stage 1)",
            "Check opcode registry mapping",
            "Ensure ASM matches opcode",
        ],
        result_recommendations=[],
    )
    print(gate.format_report(report3))
    
    # ─── Scenario 4: Result Consistency Issue ───
    print("\n[Scenario 4] Path A/B Result Mismatch")
    report4 = gate.verify_pipeline(
        tool_name="bio_organic_divider_v1",
        type_score=1.0,
        operator_score=1.0,
        result_score=0.30,
        type_violations=[],
        operator_violations=[],
        result_violations=[
            "Numerical result mismatch: Path A = 300, Path B = 301",
            "Register coherence low: 30.0%. Path A primary=300, Path B primary=250",
        ],
        type_recommendations=[],
        operator_recommendations=[],
        result_recommendations=[
            "Verify arithmetic operation implementation in both paths",
            "Check for rounding differences in LLVM IR",
            "Validate register allocation consistency",
        ],
    )
    print(gate.format_report(report4))
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
