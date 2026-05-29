# -*- coding: utf-8 -*-
"""
KAGNUS OS — ROC v3.0
Stage 1: Natural Language Parser
Extracts computational intent and operands from natural language input.

Author: Sungha (Meta Architect)
"""

# ═══════════════════════════════════════════════════════════════
# Opcode Registry — operation keywords → machine code / ASM / LLVM mapping
# ═══════════════════════════════════════════════════════════════

OPCODE_REGISTRY = {
    "add":      {"opcode": "00000001", "asm": "ADD",  "llvm_op": "add",  "symbol": "+"},
    "plus":     {"opcode": "00000001", "asm": "ADD",  "llvm_op": "add",  "symbol": "+"},
    "subtract": {"opcode": "00000010", "asm": "SUB",  "llvm_op": "sub",  "symbol": "-"},
    "minus":    {"opcode": "00000010", "asm": "SUB",  "llvm_op": "sub",  "symbol": "-"},
    "multiply": {"opcode": "00000011", "asm": "MUL",  "llvm_op": "mul",  "symbol": "×"},
    "divide":   {"opcode": "00000100", "asm": "DIV",  "llvm_op": "sdiv", "symbol": "÷"},
    "bitand":   {"opcode": "00000101", "asm": "AND",  "llvm_op": "and",  "symbol": "&"},
    "bitor":    {"opcode": "00000110", "asm": "OR",   "llvm_op": "or",   "symbol": "|"},
    "shift":    {"opcode": "00000111", "asm": "SHL",  "llvm_op": "shl",  "symbol": "<<"},
}

WORD_NUM_MAP = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "hundred": 100, "thousand": 1000,
}


# ═══════════════════════════════════════════════════════════════
# NL Parser — natural language → structured niche data
# ═══════════════════════════════════════════════════════════════

def parse_niche(prompt: str) -> dict:
    """
    Extract computational intent and operands from a natural language prompt.

    Returns a structured niche dict consumed by Stage 2 (Path A) and Stage 3 (Path B).
    Defaults to ADD if no operation keyword is detected.
    Defaults to operands (2, 3) if fewer than two numeric values are found.
    """
    prompt_lower = prompt.lower()

    detected = None
    for kw, spec in OPCODE_REGISTRY.items():
        if kw in prompt_lower:
            detected = (kw, spec)
            break
    if not detected:
        detected = ("add", OPCODE_REGISTRY["add"])

    nums = []
    for token in prompt_lower.replace(",", " ").split():
        try:
            n = int(token)
            if 0 <= n <= 0xFFFF:
                nums.append(n)
        except ValueError:
            if token in WORD_NUM_MAP:
                nums.append(WORD_NUM_MAP[token])

    if len(nums) < 2:
        nums = [2, 3]

    keyword, spec = detected
    return {
        "keyword":  keyword,
        "opcode":   spec["opcode"],
        "asm_cmd":  spec["asm"],
        "llvm_op":  spec["llvm_op"],
        "symbol":   spec["symbol"],
        "operands": (nums[0], nums[1]),
    }


# ═══════════════════════════════════════════════════════════════
# Standalone test
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import json

    test_cases = [
        "add 2 and 3",
        "subtract 100 from 200",
        "multiply 50 and 8",
        "three plus five",
    ]

    for prompt in test_cases:
        result = parse_niche(prompt)
        print(f"Input:  {prompt}")
        print(f"Output: {json.dumps(result, ensure_ascii=False)}")
        print()
