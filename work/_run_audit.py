import json, re

with open('work/audit_segments.json', encoding='utf-8') as f:
    data = json.load(f)

style = data.get('style_instruction', '')
segs = data['segments']

def fix(text):
    text = re.sub(r'(?<!\d) {2,}(?!\d)', ' ', text)
    text = re.sub(r'\.([A-Z])', r'. \1', text)
    text = re.sub(r' +([,.:;!?])', r'\1', text)
    text = re.sub(r'([,;:])([a-zA-Z0-9])', r'\1 \2', text)
    return text

SPECIFIC = {
    "audit_00002": "Considerable effort was also devoted to understanding the methods for computing derivatives of various functions. The utility of derivatives must therefore be substantial, to warrant such extensive study.",
    "audit_00007": "Comparing two expressions of the form ∞/∞ appears to offer no obvious starting point — and this observation is correct.",
    "audit_00009": "Consider which of the two competing parties will prevail in a long-term rivalry. Although the initial magnitude is relevant, the determining factor is the rate of increase. If Person A has 1 billion and grows at 7% annually while Person B has 5 billion and grows at 10% annually, it follows that Person B will surpass Person A in the long run.",
    "audit_00012": "L'Hôpital's Rule (L'Hospital's Rule)",
    "audit_00021": "This result may be accepted as an axiom without proof. The focus should be on the correct application of the rule.",
    "audit_00034": "Applying L'Hôpital's Rule to the two standard limits yields the following intuitive results:",
    "audit_00035": "As with any mathematical skill, proficiency increases with practice. Additional applications of the derivative are examined in the sections that follow.",
    "audit_00041": "Definition (Local Maximum): If there exists an open interval containing c such that f(x) ≤ f(c) for all x in that interval, then f(c) is a local maximum of f(x). A local maximum is equivalently referred to as a relative maximum.",
    "audit_00045": "equivalently termed the absolute maximum.",
    "audit_00046": "To clarify the distinction between local and global extrema: the term 'local' indicates that the inequality f(x) ≤ f(c) need only hold within an arbitrarily small open interval containing c.",
    "audit_00047": "For example, if elevation is regarded as a function defined on Earth's surface, then the summits of the Five Sacred Mountains are each local maxima. Similarly, any local high point — regardless of scale — constitutes a local maximum. Mount Everest, however, is the unique global maximum of this function.",
    "audit_00048": "Consider official rank as a function. Although a provincial governor holds a high position, both a governor and a village chief are local maximum officials within their respective domains. Only the head of state constitutes the global maximum.",
    "audit_00049": "It is important to maintain a clear distinction between local and global extrema and to avoid conflating the two. Numerous historical errors in judgment have resulted from treating a local optimum as though it were a global one. Maintaining appropriate perspective on one's position within a larger context is therefore advisable.",
    "audit_00051": "Definition (Local Minimum): If there exists an open interval containing c such that f(x) ≥ f(c) for all x in that interval, then f(c) is the local minimum of f(x). A local minimum is equivalently referred to as a relative minimum.",
    "audit_00056": "points c and d such that f(c) is the absolute maximum and f(d) is the absolute minimum. The figure below illustrates the Extreme Value Theorem.",
    "audit_00060": "As shown in the figure: the function on the left attains no maximum value, and the function on the right attains neither a maximum nor a minimum. This occurs because the left function is discontinuous and the right function's domain is not a closed interval.",
    "audit_00063": "Fermat's Theorem: If f(x) has a local extreme value at c and f'(c) exists, then f'(c) = 0.",
    "audit_00064": "Proof: Assume c is a local maximum of f(x); the argument for a local minimum is analogous. The local maximum condition requires that within some open interval containing c, the following inequality holds:",
    "audit_00069": "It has thus been established that the one-sided derivatives of f at c are non-negative on one side and non-positive on the other. Since f'(c) exists, the left-hand and right-hand derivatives must be equal. The only value satisfying both conditions is zero; hence f'(c) = 0.",
    "audit_00070": "Remark: Fermat's Theorem asserts only that a local extreme point with an existing derivative must have derivative equal to zero. It does not assert that every local extreme point has a derivative equal to zero, since some local extreme points have no derivative.",
    "audit_00072": "A systematic method for locating extreme values is now available. Step 1: identify the critical points of the function — points at which the derivative either does not exist or equals zero. Step 2: compare the function values at the critical points and at the interval endpoints to determine the global and local extreme values.",
    "audit_00073": "The function values at the interval endpoints must be examined separately because, although endpoints do not satisfy the definition of local extreme points, they may nonetheless be global extreme points. For instance, a strictly monotonic function attains its global extreme values exclusively at the endpoints.",
    "audit_00074": "It remains to determine whether a given critical point corresponds to a local maximum or a local minimum.",
    "audit_00075": "This determination relies on the sign of the derivative in the vicinity of the critical point. As established previously, the sign of the derivative on an interval determines whether the function is increasing or decreasing on that interval: a positive derivative implies an increasing function; a negative derivative implies a decreasing function.",
    "audit_00078": "It has thus been established that the one-sided derivatives of f at c are non-negative on one side and non-positive on the other. Since f'(c) exists, the left-hand and right-hand derivatives must be equal, and the only admissible value is zero. Hence f'(c) = 0.",
    "audit_00079": "Remark: Fermat's Theorem asserts only that a local extreme point with an existing derivative must have derivative equal to zero. It does not assert that every local extreme point has a derivative equal to zero, since some local extreme points have no derivative.",
    "audit_00081": "A systematic method for locating extreme values is now available. Step 1: identify the critical points — points at which the derivative does not exist or equals zero. Step 2: compare the function values at the critical points and at the interval endpoints to determine the global and local extreme values.",
    "audit_00082": "The function values at the interval endpoints must be examined separately because endpoints, although not satisfying the definition of local extreme points, may be global extreme points. A strictly monotonic function, for example, attains its global extreme values exclusively at the endpoints.",
    "audit_00083": "It remains to determine whether a given critical point is a local maximum or a local minimum.",
    "audit_00084": "This determination relies on the sign of the derivative in the vicinity of the critical point. A positive derivative on an interval implies the function is increasing on that interval; a negative derivative implies the function is decreasing.",
}

results = []
fixed_count = 0
for seg in segs:
    original = seg['text']
    if seg['id'] in SPECIFIC:
        fixed = SPECIFIC[seg['id']]
    else:
        fixed = fix(original)
    if fixed != original:
        fixed_count += 1
    results.append({'id': seg['id'], 'original': original, 'fixed': fixed})

with open('work/audited_segments.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"AI audit complete ({style[:40]}...): {fixed_count}/{len(segs)} paragraphs rewritten/fixed")
