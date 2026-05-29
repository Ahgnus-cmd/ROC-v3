# -*- coding: utf-8 -*-
"""
KAGNUS OS — ROC v3.0
Stage 2: Path A — Hardware Level Compiler
Natural language → machine code bitstream → x86 assembly instructions

Author: Sungha (Meta Architect)
"""

import random
from stage1_nl_parser import parse_niche


# ═══════════════════════════════════════════════════════════════
# Path A — Hardware Level Compiler
# ═══════════════════════════════════════════════════════════════

class PathA_HardwareCompiler:
    """
    Compiles a structured niche (from Stage 1) into:
      - A binary bitstream representing the operation
      - Optimized x86 assembly instructions
      - Register allocation (standard or mutated)
    """

    # Available register pool — mutation engine selects from this list
    REGISTER_POOL = ["EAX", "EBX", "ECX", "EDX", "ESI", "EDI"]

    def __init__(self):
        self.allocated_registers = {}

    def compile(self, niche: dict, mutate_registers: bool = False) -> dict:
        """
        Run Path A compilation.

        Args:
            niche: structured output from Stage 1 parse_niche()
            mutate_registers: if True, randomize register selection
                              (used by the mutation engine for variant generation)

        Returns:
            dict with bitstream, raw/optimized assembly, register allocation,
            and binary representations of both operands.
        """
        v1, v2  = niche["operands"]
        opcode  = niche["opcode"]
        asm_cmd = niche["asm_cmd"]

        # Bitstream — 8-bit operands for values ≤ 255, 16-bit otherwise
        bit_width    = 16 if max(v1, v2) > 255 else 8
        fmt          = f'0{bit_width}b'
        operand1_bin = format(v1, fmt)
        operand2_bin = format(v2, fmt)
        bitstream    = f"{opcode}_{operand1_bin}_{operand2_bin}"

        # Register allocation
        if mutate_registers:
            pool = list(self.REGISTER_POOL)
            random.shuffle(pool)
            reg1, reg2 = pool[0], pool[1]
        else:
            reg1, reg2 = "EAX", "EBX"

        self.allocated_registers = {"primary": reg1, "secondary": reg2}

        # Raw assembly instructions
        instructions = [
            f"MOV {reg1}, {v1}",
            f"MOV {reg2}, {v2}",
            f"{asm_cmd} {reg1}, {reg2}",
        ]

        # Optimization pass — eliminate identity operations
        optimized = []
        for ins in instructions:
            parts = ins.replace(",", "").split()
            if len(parts) == 3:
                if parts[0] == "ADD" and parts[2] == "0":
                    continue
                if parts[0] == "MUL" and parts[2] == "1":
                    continue
                if parts[0] == "MOV" and parts[2] == "0" and asm_cmd in ("ADD", "SUB"):
                    continue
            optimized.append(ins)

        return {
            "bitstream":              bitstream,
            "bit_width":              bit_width,
            "raw_instructions":       instructions,
            "optimized_instructions": optimized,
            "registers":              self.allocated_registers,
            "operand_1":              {"decimal": v1, "binary": operand1_bin},
            "operand_2":              {"decimal": v2, "binary": operand2_bin},
        }


# ═══════════════════════════════════════════════════════════════
# Standalone test
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    compiler = PathA_HardwareCompiler()

    test_cases = [
        "add 2 and 3",
        "subtract 300 from 500",
        "add 0 and 10",
    ]

    for prompt in test_cases:
        niche  = parse_niche(prompt)
        result = compiler.compile(niche)
        print(f"Input:     {prompt}")
        print(f"Bitstream: {result['bitstream']}")
        print(f"Assembly:  {result['optimized_instructions']}")
        print(f"Registers: {result['registers']}")
        print()

    # Mutation test
    niche   = parse_niche("add 2 and 3")
    mutated = compiler.compile(niche, mutate_registers=True)
    print(f"[Mutated registers] {mutated['registers']}")
    print(f"[Mutated assembly]  {mutated['optimized_instructions']}")
