"""Fix remaining issues in audited_segments.json that do_audit.py missed or got wrong."""
import json
from pathlib import Path

MANUAL_FIXES = {
    # Double-comma fixes and spacing
    "audit_00076": "Equivalently, the sign of the slope of the tangent line determines whether the function is increasing or decreasing.",
    "audit_00085": "Equivalently, the sign of the slope of the tangent line determines whether the function is increasing or decreasing.",
    "audit_00087": "As shown in the figure above, the function on the AB and CD intervals is increasing, and its tangent slope, i.e., the derivative, is positive.",
    "audit_00088": "Clearly, the function at B and C has derivative equal to 0. That is, B and C are both relative extreme value points.",
    "audit_00093": "The function changes from increasing to decreasing. Therefore, B is a relative maximum point.",
    "audit_00095": "Conclusion: if the derivative changes from positive to negative on either side of a critical point, then that critical point is a local maximum. Conversely, if the derivative changes from negative to positive, then that critical point is a local minimum.",
    "audit_00096": "At this point, the general procedure for finding extreme values is clear. The newly acquired techniques are now applied to concrete examples.",
    "audit_00097": "Example 5): Find the absolute extreme values of f(x) = 2x\u00b3 \u2212 3x\u00b2 \u2212 12x on the interval [\u22122, 3]. Solution: Following the standard procedure, we first find the critical points.",
    # audit_00108 was wrongly replaced with section header - restore original
    "audit_00108": "The figure below illustrates this example.",
    # audit_00133 double comma
    "audit_00133": "Consider a linear equation: most elementary school students can solve it easily. For a quadratic equation, nearly every high school student can write out the quadratic formula. But what about something more complex?",
    # audit_00142-143 broken sentence
    "audit_00142": "The method Newton employed is the standard calculus approach: use linear methods to solve non-linear problems.",
    "audit_00143": "The idea is as follows.",
    # Double comma fixes
    "audit_00144": "1) As shown in the figure, suppose the task is to find the root r of f(x) = 0. Without a starting point, one can only guess an initial approximation x\u2081. It is almost certain that x\u2081 is not the root.",
    "audit_00146": "3) Naturally, x\u2082 is also almost certainly not r. However, since the tangent direction represents the local behavior of f, x\u2082 should be closer to r than x\u2081 was.",
    "audit_00164": "Just as in the master's original example, he chose x\u2081 = 2. Why not 0, 1, or \u22121? A brief comparison makes it clear. Clearly, f(\u22121) = \u22124, while f(2) is close to 0. The value whose function value is closest to 0 is the natural choice.",
    "audit_00170": "From the figure, the two curves intersect at approximately x \u2248 0.75. We therefore choose x\u2081 = 0.75 to find the root of h(x) = 0.",
    # audit_00172 was an invented fix - restore original formula context
    "audit_00172": "therefore: x\u2099\u208a\u2081 = x\u2099 +",
    # audit_00175 is garbled formula output - leave as math context
    "audit_00175": "After four iterations, x\u2084 and x\u2085 agree to four decimal places. The answer is: r \u2248 0.4566.",
}

def main():
    path = Path("work/audited_segments.json")
    with open(path) as f:
        segs = json.load(f)

    fixed = 0
    for seg in segs:
        if seg["id"] in MANUAL_FIXES:
            seg["fixed"] = MANUAL_FIXES[seg["id"]]
            fixed += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(segs, f, ensure_ascii=False, indent=2)

    print(f"Applied {fixed} manual corrections to audited_segments.json.")

if __name__ == "__main__":
    main()
