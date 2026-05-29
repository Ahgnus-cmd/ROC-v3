# -*- coding: utf-8 -*-
"""
KAGNUS OS — ROC v3.0
Stage 3: Path B — LLVM IR Compiler
Natural language → platform-independent LLVM IR intermediate representation

Author: Sungha (Meta Architect)
"""

import re
from stage1_nl_parser import parse_niche


# ═══════════════════════════════════════════════════════════════
# Path B — LLVM IR Compiler
# ═══════════════════════════════════════════════════════════════

class PathB_LLVMCompiler:
    """
    Compiles a structured niche (from Stage 1) into LLVM IR.

    Selects IR type automatically:
      - i32 for operands within 32-bit signed range
      - i64 for larger values
    """

    def compile(self, niche: dict, tool_name: str = "roc_compute") -> dict:
        """
        Run Path B compilation.

        Args:
            niche: structured output from Stage 1 parse_niche()
            tool_name: name of the generated LLVM function

        Returns:
            dict with IR code, type, virtual registers, and operation metadata.
        """
        v1, v2  = niche["operands"]
        llvm_op = niche["llvm_op"]

        # IR type — promote to i64 for values exceeding i32 range
        ir_type = "i64" if max(v1, v2) > 2**31 else "i32"

        ir_code = f"""define {ir_type} @{tool_name}() {{
entry:
    %val_a  = add {ir_type} {v1}, 0
    %val_b  = add {ir_type} {v2}, 0
    %result = {llvm_op} {ir_type} %val_a, %val_b
    ret {ir_type} %result
}}"""

        # Extract virtual registers (deduplicated, order preserved)
        ir_registers = list(dict.fromkeys(re.findall(r'%[a-zA-Z0-9_]+', ir_code)))

        return {
            "ir_code":        ir_code,
            "ir_type":        ir_type,
            "ir_registers":   ir_registers,
            "llvm_operation": llvm_op,
            "function_name":  f"@{tool_name}",
        }


# ═══════════════════════════════════════════════════════════════
# Standalone test
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    compiler = PathB_LLVMCompiler()

    test_cases = [
        ("add 2 and 3",          "adder_tool"),
        ("subtract 50 from 100", "subtractor_tool"),
        ("multiply 7 and 8",     "multiplier_tool"),
    ]

    for prompt, name in test_cases:
        niche  = parse_niche(prompt)
        result = compiler.compile(niche, tool_name=name)
        print(f"Input:     {prompt}")
        print(f"Function:  {result['function_name']}")
        print(f"IR type:   {result['ir_type']}")
        print(f"Registers: {result['ir_registers']}")
        print(f"IR code:\n{result['ir_code']}")
        print()
