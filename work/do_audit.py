import json, re, sys
sys.path.insert(0, '.')

with open('work/audit_segments.json', encoding='utf-8') as f:
    data = json.load(f)
style = data.get('style_instruction', '')
segs = data['segments']

fixes = [
    (r'\blocalmaximum\b', 'local maximum'),
    (r'\blocalminimum\b', 'local minimum'),
    (r'\brelativemaximum\b', 'relative maximum'),
    (r'\brelativeminimum\b', 'relative minimum'),
    (r'\babsolutemaximum\b', 'absolute maximum'),
    (r'\babsoluteminimum\b', 'absolute minimum'),
    (r'\bfamouslimits\b', 'famous limits'),
    (r'\blinearapproximation\b', 'linear approximation'),
    (r'\bwithoutproof\b', 'without proof'),
    (r'\bnotclosed\b', 'not closed'),
    (r'\bfindthe\b', 'find the'),
    (r'\bsatis fying\b', 'satisfying'),
    (r'\bex ists\b', 'exists'),
    (r'\bex ist\b', 'exist'),
    (r'\borthe\b', 'or the'),
    (r'\bisthe\b', 'is the'),
    (r'\bchas\b', 'c has'),
    (r'from  this', 'from this'),
    (r'\bfunc where\b', 'functions'),
    (r'\bincreasingor\b', 'increasing or'),
    (r'\borlocal\b', 'or local'),
    (r'\bmini ma\b', 'minima'),
    (r'\bpeakswould\b', 'peaks would'),
    (r'\bcand\b', 'c and'),
    (r"L'Hospital, sRule", "L'Hospital's Rule"),
    (r'\bspentconsiderable\b', 'spent considerable'),
    (r'\bax  in the\b', 'ax with'),
    (r'\bcBeing\b', 'c being'),
]

SPECIFIC = {
    'audit_00001': 'In the first two chapters, the central concept of limits in calculus was clarified, and the notion of slope introduced in secondary school was generalized to produce the derivative.',
    'audit_00002': 'Considerable effort was also devoted to understanding the methods for computing derivatives of various functions. The utility of the derivative must therefore be substantial to justify such extensive study.',
    'audit_00003': 'Indeed, derivatives have numerous important applications.',
    'audit_00005': 'Limit problems are central to calculus. Two particularly difficult indeterminate forms arise frequently:',
    'audit_00007': 'Comparing two expressions of the form \u221e/\u221e offers no obvious starting point \u2014 and this observation is correct.',
    'audit_00008': 'Consider two quantities, each so large as to be practically incomparable to a third party. Determining which will ultimately be greater requires further analysis.',
    'audit_00009': 'To determine which of two competing quantities will dominate in the long run, the relevant factor is not the current magnitude but the rate of growth. If Party A holds 1 billion units growing at 7% per year while Party B holds 5 billion units growing at 10% per year, then Party B will ultimately surpass Party A.',
    'audit_00010': "Party B prevails because its growth rate of 10% exceeds Party A's rate of 7%. Rate of growth is precisely rate of change \u2014 that is, the derivative.",
    'audit_00011': 'This suggests that when two \u221e quantities yield no conclusion upon direct comparison, the ratio of their derivatives may nevertheless be determinate. This idea was proved rigorously by the French mathematician L\u2019H\u00f4pital more than 300 years ago.',
    'audit_00012': "L\u2019H\u00f4pital\u2019s Rule (L\u2019Hospital\u2019s Rule)",
    'audit_00013': 'Suppose f(x) and g(x) are differentiable in a region containing a (though not necessarily at a itself), and g(x) \u2260 0. If:',
    'audit_00016': "L\u2019H\u00f4pital\u2019s Rule resolves both indeterminate forms simultaneously. Several remarks are in order.",
    'audit_00021': 'This result may be accepted without proof. Attention should be directed toward correct application of the rule.',
    'audit_00027': 'Consider the following two limits:',
    'audit_00030': 'The solution process shows that even if the numerator is a higher power, the result of the limit is unchanged. Similarly, for any numerator of the form ax with a > 1, the limit is \u221e.',
    'audit_00031': 'This confirms that exponential growth (ax type, a > 1) dominates polynomial growth (xn type), which in turn dominates logarithmic growth (ln x type). The following example examines polynomial against logarithmic growth:',
    'audit_00032': 'Even with a fractional power in the numerator and a squared logarithm in the denominator, the result remains \u221e.',
    'audit_00033': 'When evaluating limits of the \u221e/\u221e type, retaining only the highest-order term in each of the numerator and denominator yields the correct result.',
    'audit_00034': "Applying L\u2019H\u00f4pital\u2019s Rule to the two standard limits yields the following intuitive results:",
    'audit_00035': 'Mathematical proficiency increases with practice. Further applications of the derivative are examined in the sections that follow.',
    'audit_00036': 'Further applications of the derivative are examined below.',
    'audit_00038': 'Extreme values arise naturally as subjects of study. Optimization problems are of broad practical importance.',
    'audit_00039': 'For the functions under study, maximum and minimum value problems are of considerable practical relevance, since resource optimization is a fundamental objective.',
    'audit_00040': 'Derivatives are instrumental in solving extreme value problems. The relevant concepts are introduced below.',
    'audit_00041': 'Definition (Local Maximum): If there exists an open interval containing c such that f(x) \u2264 f(c) for all x in that interval, then f(c) is a local maximum of f(x). A local maximum is equivalently referred to as a relative maximum.',
    'audit_00042': 'The concept of a global maximum follows naturally.',
    'audit_00043': 'Definition (Global Maximum): If f(x) \u2264 f(c) holds for all x in the domain, then f(c) is the global maximum of f(x). The global maximum is sometimes',
    'audit_00045': 'equivalently termed the absolute maximum.',
    'audit_00046': "To clarify the distinction: the term 'local' indicates that the inequality f(x) \u2264 f(c) need only hold within an arbitrarily small open interval containing c.",
    'audit_00047': "For example, if elevation is regarded as a function defined on Earth's surface, then the summits of the Five Sacred Mountains are each local maxima. Any local high point, regardless of scale, constitutes a local maximum. Mount Everest is the unique global maximum of this function.",
    'audit_00048': 'Consider official rank as a function. A provincial governor and a village chief are both local maximum officials within their respective jurisdictions. Only the head of state constitutes the global maximum.',
    'audit_00049': 'A clear distinction must be maintained between local and global extrema. Numerous errors in judgment arise from treating a local optimum as a global one. Maintaining appropriate perspective regarding position within a broader context is therefore advisable.',
    'audit_00050': 'The concept of minimum follows from the concept of maximum.',
    'audit_00051': 'Definition (Local Minimum): If there exists an open interval containing c such that f(x) \u2265 f(c) for all x in that interval, then f(c) is the local minimum of f(x). A local minimum is equivalently referred to as a relative minimum.',
    'audit_00052': 'Definition (Global Minimum): If f(x) \u2265 f(c) holds for all x in the domain, then f(c) is the global minimum of f(x). The global minimum is sometimes also called the absolute minimum.',
    'audit_00053': 'The concepts of extreme values having been established, the methods for finding them are now examined.',
    'audit_00055': 'The Extreme Value Theorem: If f(x) is continuous on the closed interval [a, b], then there exist two',
    'audit_00056': 'points c and d such that f(c) is the absolute maximum and f(d) is the absolute minimum. The figure below illustrates the Extreme Value Theorem.',
    'audit_00057': 'The geometric interpretation is illustrated in the figure below.',
    'audit_00059': 'Two conditions of the theorem \u2014 continuity and a closed interval \u2014 are both necessary. The figures below show cases in which each condition is violated, causing the Extreme Value Theorem to fail.',
    'audit_00060': "As shown: the function on the left attains no maximum value, and the function on the right attains neither a maximum nor a minimum. The left function is discontinuous; the right function's domain is not a closed interval.",
    'audit_00061': 'The existence of extreme values having been established, attention turns to methods for locating them based on the properties of extreme points.',
    'audit_00062': 'For a continuous function on a closed interval, global extreme points exist. In general, global extreme points are selected from among the local extreme points; identifying local extreme points is therefore the primary task.',
    'audit_00063': "Fermat's Theorem: If c is a local extreme point of f(x) and f'(c) exists, then f'(c) = 0.",
    'audit_00064': 'Proof: Assume c is a local maximum of f(x); the case of a local minimum is proved analogously. The local maximum condition states that within some open interval containing c, the following inequality holds:',
    'audit_00067': "In the expression above, since the numerator is non-negative and the denominator is negative: f'(c-) >= 0. Similarly:",
    'audit_00069': "It has thus been established that f at c has one-sided derivatives that are non-negative on one side and non-positive on the other. Since f'(c) exists, the left-hand and right-hand derivatives must be equal. The only value satisfying both inequalities is zero; hence f'(c) = 0.",
    'audit_00070': "Remark: Fermat's Theorem asserts only that a local extreme point at which the derivative exists must have derivative equal to zero. It does not assert that every local extreme point has derivative zero, since some local extreme points have no derivative.",
    'audit_00071': 'Points at which the derivative does not exist and points at which the derivative equals zero are collectively called critical points of the function.',
    'audit_00072': 'A systematic method for locating extreme values is now available. Step 1: identify the critical points -- those at which the derivative either does not exist or equals zero. Step 2: compare the function values at the critical points and at the interval endpoints to determine the global and local extreme values.',
    'audit_00073': 'The function values at the interval endpoints must be examined separately because, although endpoints do not satisfy the definition of local extreme points, they may nonetheless be global extreme points. A strictly monotonic function attains its global extreme values exclusively at the endpoints.',
    'audit_00074': 'It remains to determine whether a given critical point corresponds to a local maximum or a local minimum.',
    'audit_00075': 'This determination relies on the sign of the derivative in the vicinity of the critical point. The sign of the derivative on an interval determines whether the function is increasing or decreasing: a positive derivative implies an increasing function; a negative derivative implies a decreasing function.',
    'audit_00078': "It has thus been established that f at c has one-sided derivatives that are non-negative on one side and non-positive on the other. Since f'(c) exists, the left-hand and right-hand derivatives must be equal, and the only admissible value is zero. Hence f'(c) = 0.",
    'audit_00079': "Remark: Fermat's Theorem asserts only that a local extreme point at which the derivative exists must have derivative equal to zero. It does not assert that every local extreme point has derivative zero, since some local extreme points have no derivative.",
    'audit_00080': 'Points at which the derivative does not exist and points at which the derivative equals zero are collectively called critical points of the function.',
    'audit_00081': 'A systematic method for locating extreme values is now available. Step 1: identify the critical points -- those at which the derivative does not exist or equals zero. Step 2: compare the function values at the critical points and at the interval endpoints to determine the global and local extreme values.',
    'audit_00082': 'The function values at the interval endpoints must be examined separately because, although endpoints do not satisfy the definition of local extreme points, they may nonetheless be global extreme points. A strictly monotonic function attains its global extreme values exclusively at the endpoints.',
    'audit_00083': 'It remains to determine whether a given critical point is a local maximum or a local minimum.',
    'audit_00084': 'This determination relies on the sign of the derivative in the vicinity of the critical point. A positive derivative on an interval implies an increasing function; a negative derivative implies a decreasing function.',
    'audit_00108': '4.3   Linear Approximation (linear approximation)',
    'audit_00172': 'Since x3 and x4 agree to four decimal places, the root is r = 0.4566.',
}


def auto_fix(text):
    for pat, repl in fixes:
        text = re.sub(pat, repl, text, flags=re.IGNORECASE)
    text = re.sub(r'(?<=[a-zA-Z,;:]) {2,}(?=[a-zA-Z])', ' ', text)
    return text


results = []
fixed_count = 0
for seg in segs:
    original = seg['text']
    sid = seg['id']
    fixed = SPECIFIC.get(sid, auto_fix(original)).strip()
    if fixed != original:
        fixed_count += 1
    results.append({'id': sid, 'original': original, 'fixed': fixed})

with open('work/audited_segments.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'AI audit complete: {fixed_count}/{len(segs)} paragraphs modified')
print(f'Style: {style[:70]}')
