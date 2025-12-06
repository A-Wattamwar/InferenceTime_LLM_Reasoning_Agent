from answer_parser import classify_question, normalize_answer
from technique1_self_consistency import self_consistency
from technique2_cot_verify import cot_with_verification
from technique3_refinement import iterative_refinement
from technique4_pal import pal_solve

def solve(problem):
    q_type = classify_question(problem)
    results = []

    if q_type == "math":
        # PAL drives math: generate Python and execute it for exact arithmetic.
        r_pal = pal_solve(problem)
        if r_pal["answer"]:
            results.append(r_pal)
        # Self-Consistency as a backup / tie-breaker.
        r_sc = self_consistency(problem, q_type)
        if r_sc["answer"]:
            results.append(r_sc)

    elif q_type == "coding":
        # Iterative Refinement drives coding: draft -> critique -> improve.
        r_ref = iterative_refinement(problem, q_type)
        if r_ref["answer"]:
            results.append(r_ref)
        r_cot = cot_with_verification(problem, q_type)
        if r_cot["answer"]:
            results.append(r_cot)

    elif q_type == "planning":
        # Iterative Refinement drives multi-step action plans.
        r_ref = iterative_refinement(problem, q_type)
        if r_ref["answer"]:
            results.append(r_ref)
        r_sc = self_consistency(problem, q_type)
        if r_sc["answer"]:
            results.append(r_sc)

    elif q_type == "future":
        # CoT + Verification drives predictions, with Self-Consistency as backup.
        r_cot = cot_with_verification(problem, q_type)
        if r_cot["answer"]:
            results.append(r_cot)
        r_sc = self_consistency(problem, q_type)
        if r_sc["answer"]:
            results.append(r_sc)

    else:  # general / common_sense
        # Self-Consistency drives factual questions, with CoT verification as backup.
        r_sc = self_consistency(problem, q_type)
        if r_sc["answer"]:
            results.append(r_sc)
        r_cot = cot_with_verification(problem, q_type)
        if r_cot["answer"]:
            results.append(r_cot)

    if not results:
        return ""

    if q_type in ["coding", "planning"]:
        best_result = max(results, key=lambda x: x["confidence"])
        return best_result["answer"]

    # Confidence-weighted vote. Keep the original-cased answer as the
    # representative for each vote bucket so we don't return a lowercased string.
    weights = {}
    representatives = {}
    for r in results:
        key = normalize_answer(r["answer"]) if q_type != "future" else r["answer"]
        weights[key] = weights.get(key, 0) + r["confidence"]
        if key not in representatives:
            representatives[key] = r["answer"]

    best_key = max(weights, key=weights.get)
    return representatives[best_key]
