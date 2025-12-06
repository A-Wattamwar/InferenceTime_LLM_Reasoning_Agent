#!/usr/bin/env python3
"""
Demo script: tests each of the 4 inference-time techniques directly, then
shows the full agent (solve) routing a question end to end.

Run:
    export OPENAI_API_KEY='sk-...'
    cd agent
    python3 demo.py
"""

from technique1_self_consistency import self_consistency
from technique2_cot_verify import cot_with_verification
from technique3_refinement import iterative_refinement
from technique4_pal import pal_solve
from agent import solve

# (label, function, question, kwargs) -- each call exercises one technique.
DEMOS = [
    (
        "Technique 4 - PAL (Program-Aided Language)",
        pal_solve,
        "A bakery sells muffins for $3 each and cookies for $2 each. "
        "If I buy 7 muffins and 5 cookies, how much do I spend in total?",
        {},
    ),
    (
        "Technique 1 - Self-Consistency (majority vote over 3 samples)",
        self_consistency,
        "Which planet in our solar system is known as the Red Planet?",
        {"q_type": "general"},
    ),
    (
        "Technique 3 - Iterative Refinement (draft -> critique -> improve)",
        iterative_refinement,
        "What is the capital city of Australia?",
        {"q_type": "general"},
    ),
    (
        "Technique 2 - Chain-of-Thought + Verification",
        cot_with_verification,
        "Tom is older than Jane. Jane is older than Sam. "
        "Who is the youngest of the three?",
        {"q_type": "general"},
    ),
]


def main():
    print("#" * 72)
    print("# Inference-Time Techniques - tested individually")
    print("#" * 72)
    for label, fn, question, kwargs in DEMOS:
        print("=" * 72)
        print(label)
        print("-" * 72)
        print(f"Question:   {question}")
        result = fn(question, **kwargs)
        print(f"Answer:     {result['answer']!r}")
        print(f"Confidence: {result['confidence']}")
        print()

    print("#" * 72)
    print("# Full agent - solve() classifies and routes automatically")
    print("#" * 72)
    for q in [
        "What is 25 * 4?",
        "Write a function body that returns the sum of all even numbers "
        "in a given list of integers called nums.",
    ]:
        print("-" * 72)
        print(f"Question: {q}")
        print(f"solve():  {solve(q)!r}")
        print()


if __name__ == "__main__":
    main()
