"""
translate.py — Apply translations to extracted segments.
This script reads extracted_segments.json and creates translated_segments.json.

Preprocessing: Normalizes Chinese punctuation spacing before translation lookup.
  - Removes spaces before Chinese punctuation (，。！？；：)
  - Ensures space after punctuation before next word
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import WORK_DIR, EXTRACTED_SEGMENTS, TRANSLATED_SEGMENTS


def normalize_punctuation_spacing(text: str) -> str:
    """
    Normalize Chinese punctuation spacing.
    
    Rules:
      1. Remove space(s) before Chinese punctuation (，。！？；：) and Western comma/period (,.)
      2. Collapse multiple spaces after punctuation to a single space
      3. Ensure space after punctuation if followed by a non-punctuation character
    
    Example:
      "如前所述 ,极限问题是微积分的核心问题 ," → "如前所述, 极限问题是微积分的核心问题,"
    """
    # Rule 1: Remove space(s) immediately before punctuation (Chinese and Western)
    text = re.sub(r'\s+([，。！？；：,.])', r'\1', text)
    
    # Rule 2: Collapse multiple spaces after punctuation to single space
    text = re.sub(r'([，。！？；：,.])\s+', r'\1 ', text)
    
    # Rule 3: Ensure space after punctuation if followed by a non-punctuation, non-space character
    text = re.sub(r'([，。！？；：,.])([^\s，。！？；：,.])', r'\1 \2', text)
    
    return text

# Translation mapping for mathematical/calculus terminology and common phrases
TRANSLATIONS = {
    # Printing metadata (keep as-is or translate minimally)
    "布克": "Book",
    "校样[成品尺寸:170": "Proof [Final size: 170",
    ";版心": "; text block",
    "33行×34字]": "33 lines × 34 characters]",
    
    # Chapter intro
    "前两章": "In the first two chapters",
    "我们弄清楚了微积分中最重要的极限概念，又升华了中学就学过的": "we clarified the most important concept of limits in calculus, and elevated what we learned in high school about",
    "斜率概念": "the concept of slope",
    "引入了导数": "introducing the derivative",
    "我们还耗费了": "We also spent",
    "大量笔墨": "considerable effort",
    ",努力搞清楚了各种函数的小趋势导数的求": ", working hard to understand the methods for finding derivatives of various functions",
    "导数总得有点特别的用途": "derivatives must have some special uses",
    "，才对得起我们的心血吧": ", to justify all our hard work",
    "没错": "Exactly",
    ",导数真的很有用!": ", derivatives really are useful!",
    
    # L'Hopital's Rule section
    "再论极限": "More on Limits",
    "罗必塔法则(L": "L'Hôpital's Rule (L",
    "罗必塔法则": "L'Hôpital's Rule",
    "如前所述": "As mentioned earlier",
    ",极限问题是微积分的核心问题": ", limit problems are the core of calculus",
    ",我们在处理极限问题的时候": ", and when dealing with limit problems",
    ",经": ", we often",
    "常碰到两种棘手的极限问题": "encounter two tricky types of limit problems",
    "型和": "type and",
    "型": "type",
    "看到两个横躺着的 8相比": "Seeing two sideways 8s compared",
    ",感觉无从下手": ", it feels like there's no way to start",
    "是对的。": "is correct.",
    
    # Analogy about wealth
    "正好比": "It's just like",
    ",我们普罗大众": ", we ordinary people",
    ",看两个大款斗富": ", watching two tycoons compete in wealth",
    ",他们都有着我们几辈子花不完的": ", they both have more than we could spend in several lifetimes of",
    "钱": "money",
    ",到底谁更牛、笑到最后": ", so who's really better and will have the last laugh",
    ",真是不好判断。": ", is really hard to judge.",
    "让我们再开动一下脑子想想": "Let's think a bit more about this",
    ",到底俩斗富的货": ", which of these two competing wealthy folks",
    ",长期掐下去": ", in a long-term rivalry",
    ",哪个更占上风?": ", will have the upper hand?",
    "虽然存量很关键": "Although the current amount is key",
    ",但是决定的因素应该是增量或者": ", the determining factor should be the increment or",
    "说是财富增加的速度。": "the rate of wealth increase.",
    "比如": "For example",
    "甲货有银子 10亿并且每年增长": "Person A has 1 billion and grows annually at",
    "乙货": "Person B",
    "虽有银": "although having",
    "亿": "billion",
    "但是这货的财富增长率": "but this person's wealth growth rate",
    "是 ": "is ",
    "细想一下不难得出结论": "With a bit of thought, it's not hard to conclude",
    ":长期下来": ": in the long run",
    ",乙货一定": ", Person B will certainly",
    "是要战胜甲货的。": "surpass Person A.",
    "我们之所以得出乙货得胜的结论": "The reason we conclude Person B wins",
    "是因为他的": "is because their",
    "10%增长率实在是比": "10% growth rate is really much better than",
    "7%的": "7%",
    "增长率厉害得多。": "growth rate.",
    "啥是增长率": "What is growth rate",
    ",不就是变化率吗。": ", isn't it just rate of change.",
    "啥是变化率呢?": "What is rate of change?",
    "导数呗!": "The derivative!",
    
    # Mathematical reasoning
    "由此我们想到": "This leads us to think",
    ",如果两个": ", if two",
    "相比没有结论": "compared give no conclusion",
    ",而他们的导数之比有高下的话": ", but the ratio of their derivatives shows a difference",
    "那他们本身之比也就有了结果。": "then the ratio of the originals also has a result.",
    "这个朴素的想法": "This simple idea",
    "已经在被法国数学家罗必塔": "was already proven by the French mathematician L'Hôpital",
    ")先生在 3百多年前证明了": ") over 300 years ago",
    
    # Theorem statement
    "假设函数 f(": "Suppose functions f(",
    "和 g(": "and g(",
    ", 在含有点": ", in a region containing point",
    "的某个区域内": "",
    "可导(不要求一定在 ": "are differentiable (not necessarily at ",
    "可导)": "differentiable)",
    "而且": "and",
    "如果": "If",
    "或者": "or",
    "那么": "then",
    "当然": "Of course",
    ",前提是右边的极限存在。": ", provided that the limit on the right exists.",
    
    # Chapter headers
    "导数有啥用": "What Are Derivatives Good For",
    "第四章": "Chapter 4",
    
    # Rule remarks
    ",一石二鸟": ", kills two birds with one stone",
    "同时解决了两种难缠的问题": "solving two tricky problems at once",
    "。关于这个法则": ". Regarding this rule",
    ",我们": ", we",
    "要提醒几点。": "need to point out a few things.",
    "首先": "First",
    "当": "when",
    "时": "",
    "该法则同样适用": "the rule also applies",
    "其次": "Second",
    ",如果两个函数的导数之比的极限又是 ": ", if the limit of the ratio of the two functions' derivatives is again ",
    "型和 ": "type and ",
    "型的": "type",
    ",可以再次使用": ", you can apply the rule again",
    "该法则到二阶导数甚至": "to the second derivative or even",
    "阶导数上。": "th order derivative.",
    "最后": "Finally",
    ",该法则的证明": ", the proof of this rule",
    ",需要更高深的数学知识。": ", requires more advanced mathematical knowledge.",
    "眼下": "For now",
    ",我们可以把它当公理一样地认为它不证": ", we can treat it like an axiom and accept it without",
    "自明": "proof",
    "。会用法则是硬道理。": ". Knowing how to apply the rule is what matters.",
    
    # Examples
    "例 ": "Example ",
    "例": "Example",
    "1):求": "1): Find",
    "解": "Solution",
    ":根据罗必塔法则": ": By L'Hôpital's Rule",
    ",我们有": ", we have",
    "2):求 ": "2): Find ",
    ":用罗必塔法则": ": Using L'Hôpital's Rule",
    ",得到": ", we get",
    "好玩吧?": "Fun, right?",
    "再看一下这两个极限": "Let's look at these two limits",
    "3):求": "3): Find",
    ":求这个极限": ": To find this limit",
    ",得对分子分母分别求 3次导数": ", we need to differentiate both numerator and denominator 3 times",
    ",才能看清楚结果": ", before we can see the result clearly",
    
    # Analysis of orders
    "由本题的解题过程可知": "From the solution process, we can see that",
    "即使分子上不是": "even if the numerator is not",
    ", 而是": ", but rather",
    "或者更高次方": "or higher powers",
    ",也不": ", it would not",
    "会改变极限的结果。": "change the result of the limit.",
    "同样": "Similarly",
    ",只要分子上 ": ", as long as the numerator has ",
    "中的": "in the",
    ", 结果不会变": ", the result won't change",
    ",都是 ": ", it's all ",
    "这也就印证了我们前面说过的": "This confirms what we said earlier about",
    "型的 ": "type ",
    "是所谓部级的 ": "being so-called ministerial-level ",
    ", 跟": ", compared to",
    "这些地": "these",
    "市级的 ": "municipal-level ",
    "没有可比性": "there's no comparison",
    "。我们再看一下地市级的 ": ". Let's look at municipal-level ",
    "遇": "meeting",
    "上 ": " ",
    "这种区县级的 ": "this county-level ",
    "会发生什么": "what happens",
    "这一次": "This time",
    ",地市级 ": ", the municipal-level ",
    "派出的分子是二分之一次方": "sends out a numerator with power one-half",
    ",而区县级 ": ", while the county-level ",
    "留守的分母是": "remains in the denominator as",
    "平方": "squared",
    "结果同样是 ": "The result is still ",
    "看来": "It seems",
    "\u201c官大一级压死人\u201d绝非虚言!": '"rank trumps all" is no empty saying!',
    "再重申一次": "Let me emphasize again",
    ",如果碰到 ": ", if you encounter ",
    "型的极限问题": "type limit problems",
    ",分子分母只留下级别最高的": ", just keep the highest-ranking term in numerator and denominator",
    "值班即可": "on duty",
    ",结果不会错。": ", and the result will be correct.",
    
    # Famous limits
    "有了罗必塔法则在手": "With L'Hôpital's Rule in hand",
    ",再来看我们在第二章要求您记住的两个著名": ", let's revisit the two famous",
    "极限": "limits",
    ",将": ", which will",
    "会显得非常直观": "become very intuitive",
    
    # Climbing analogy
    "我们登山时会发现": "When climbing a mountain, we find",
    ",登得越高": ", the higher we climb",
    ",视野越好": ", the better the view",
    "。玩数学也一样": ". The same goes for math",
    ",玩得越多": ", the more you practice",
    "玩过的": "the things you've learned",
    "东东看得越清楚。": "become clearer.",
    "让我们看看导数还有啥用。": "Let's see what else derivatives are good for.",
    
    # Extreme values section
    "极值问题(": "Extreme Value Problems (",
    "人们总爱关注离自己稍微远点的、极端点的事物。": "People always like to focus on things that are a bit distant or extreme.",
    "例如": "For example",
    ":皇室的故事": ": stories about royalty",
    ",总是": ", always",
    " 在平民百姓中有市场": " have an audience among common people",
    "。再例如": ". Another example",
    ":最有钱的、最漂亮的、最高的、最险的等等总是最 ": ": the richest, most beautiful, tallest, most dangerous, etc., always attract ",
    "能吸引我们的眼球。": "our attention the most.",
    ",对我们研究的函数而言": ", for the functions we study",
    "函数的最大值和最": "the maximum and mini",
    "小值问题": "mum value problems",
    ", 自然引起了人": ", naturally attract people's",
    "们的极大兴趣。": "great interest.",
    "因为在生活中": "Because in real life",
    ",极值问题太有用了。": ", extreme value problems are extremely useful.",
    "怎样把有限的资源发挥到": "How to maximize limited resources to their",
    "极致": "fullest potential",
    ",永远是我们的追求。": ", is always our pursuit.",
    "要解决极值问题": "To solve extreme value problems",
    ",导数可以帮上大忙": ", derivatives can be a great help",
    "。先厘清几个关于极值问题的概念": ". Let's first clarify some concepts about extreme values",
    
    # Definitions
    "局部最大值定义(": "Definition of Local Maximum (",
    "局部最大值": "Local maximum",
    "局部最小值定义(": "Definition of Local Minimum (",
    "局部最小值": "Local minimum",
    "全局最大值定义(": "Definition of Global Maximum (",
    "全局最大值": "Global maximum",
    "全局最小值定义(": "Definition of Global Minimum (",
    "全局最小值": "Global minimum",
    "如果对包含 ": "If for some open interval containing ",
    "如果对包含": "If for some open interval containing",
    "点在内的某个开区间内": "point",
    "点在内的某个开区间内的": "point",
    "所有": "all",
    "值": "values",
    "不等式": "the inequality",
    "不等式 ": "the inequality ",
    "不等式 f(": "the inequality f(",
    ") 都成立": ") holds",
    "都成立": "holds",
    ") 就是函数": ") is a",
    "的一个局部": "local",
    "的一个局": "'s local",
    "最大值": "maximum",
    "部最小值": "minimum",
    "有时候也称为相对最大值(": "is sometimes also called relative maximum (",
    "有时候也称为相对最小值(": "is sometimes also called relative minimum (",
    "有局部就有全局。": "Where there's local, there's global.",
    "如果对所有的 ": "If for all ",
    "那么 f(": "Then f(",
    "那么 ": "Then ",
    "就是函数 f(": "is the function f(",
    "的全局最大值": "'s global maximum",
    "的全局最小值": "'s global minimum",
    "有时候": "is sometimes",
    "也被称作绝对最大值(": "also called absolute maximum (",
    "也被称作绝对最小值(": "also called absolute minimum (",
    
    # Understanding concepts
    "接着聊一": "Let's continue discussing",
    "下": "",
    "对": "our",
    "这": "understanding",
    "两": "of",
    "个": "these",
    "概": "two",
    "念 的": "concepts",
    "理": "",
    "解。": ".",
    "所": "The",
    "谓": "term",
    "局": "local",
    "部": "",
    "就": "means",
    "是": ":",
    ": 只": " as",
    "要": "long",
    "那": "as",
    "不": "in",
    "等": "equal",
    "式": "ity",
    "在哪怕很小的区间内成立": "holds even in a very small interval",
    "就是一个局部最大值": "it is a local maximum",
    
    # Mountain/elevation analogy
    ",如果把地球上的海拔高度做为函数": ", if we consider Earth's elevation as a function",
    ",那五岳之巅的高度": ", then the height of the Five Sacred Mountains' peaks",
    "都会是一个局": "would all be local",
    "部最大值。": "maxima.",
    "与此同时": "At the same time",
    ",您回家上楼的每一阶楼梯高度、甚至您放在地上拖鞋的高": ", the height of each stair step on your way home, or even the height of your slippers on the floor",
    "度": "",
    ",也都是不折不扣的一个局部最大值。": ", are all genuine local maxima.",
    "而珠穆朗玛峰才是这个函数的全球最": "But Mount Everest is the global",
    "大值。": "maximum of this function.",
    
    # Official rank analogy
    "再比如": "Another example",
    ",如果把官职的高低做为函数": ", if we consider official rank as a function",
    "。虽然省长很牛": ". Although a governor is impressive",
    ",但是一个省长和": ", a governor and",
    "一个": "a",
    "村长一样": "village chief alike",
    ",都是一个局部最高官。": ", are both local maximum officials.",
    "只有国家主席": "Only the President",
    ",才是全局最高官。": ", is the global maximum official.",
    
    # Life wisdom
    "人人心中都应该有一个衡量局部和全局的秤": "Everyone should have a scale in their heart to measure local versus global",
    ",千万别把自己掂量": ", and never overestimate",
    "的太重了。": "yourself.",
    "武林中有多少爱恨情仇": "How much love and hatred in the martial world",
    ",皆因对局部和全局判断不清所起": ", all arise from unclear judgment between local and global",
    "。甚至有多少本": ". How many once",
    "来挺": "quite",
    "不错的局部老大": "decent local bosses",
    "因误以为自己个是全局老大而送了卿卿性命。": "lost their lives by mistaking themselves for global bosses.",
    "不管进步到啥": "No matter how far you've",
    "程度": "advanced",
    ",永远把自己当成局部、小局部的一般人": ", always consider yourself an ordinary person in a local, small local context",
    ",大概结果不会差。": ", and things will probably turn out fine.",
    "易经的洋洋 64卦中": "Among the grand 64 hexagrams of the I Ching",
    ",只有谦卦": ", only the Modesty hexagram",
    ",没啥副作用!": ", has no side effects!",
    "有了最大值的概念": "With the concept of maximum",
    ",最小值的概念顺理成章。": ", the concept of minimum follows naturally.",
    
    # Extreme Value Theorem
    "明白了极值的概念": "Now that we understand the concept of extreme values",
    ",就可以探讨如何找出极值了。": ", we can discuss how to find them.",
    "要研究如何求极值问题": "To study how to find extreme values",
    ",首先得确定它的存在性": ", we must first establish their existence",
    "。所以": ". Therefore",
    "了解极值定理": "understanding the Extreme Value Theorem",
    ",很": ", is",
    "有必要。": "necessary.",
    "极值定理": "The Extreme Value Theorem",
    ":如果函数 f(": ": If function f(",
    ") 在闭区间 [": ") is continuous on closed interval [",
    "] 上连续": "]",
    ",则此区间上一定存在两": ", then there must exist two",
    "个点 ": "points ",
    "和d": "and d",
    "使得 f(": "such that f(",
    "为绝对最大值": "is the absolute maximum",
    "为": "is",
    "绝对最小值": "the absolute minimum",
    "下图为极值定理的示意图。": "The figure below illustrates the Extreme Value Theorem.",
    "我对这个定理的学习心得是": "My insights from studying this theorem are",
    "虽然闭区间的绝对极值一定可以达到": "although the absolute extreme values on a closed interval are always attained",
    ",但是不一定唯一": ", they may not be unique",
    "定理存在的两个条件": "The two conditions for the theorem",
    '"连续"和': '"continuity" and',
    '"闭区间"缺一不可。': '"closed interval" are both indispensable.',
    "下图就是分别缺了": "The figure below shows cases missing",
    "连续和区间封闭这两种条件的情况下": "continuity and interval closure respectively",
    ",导致极值定理不成立的": ", causing the Extreme Value Theorem to fail",
    "情形。": ".",
    "由图可见": "From the figure, we can see",
    ",左边的函数没有最大值": ", the function on the left has no maximum",
    ",右边的函数既没有最大值": ", the function on the right has neither maximum",
    ",也没有最小": ", nor mini",
    "。原因就是": ". The reason is",
    ":左边的函数不连续": ": the left function is not continuous",
    ",右边的函数定义区间不": ", the right function's domain is not",
    "封闭。": "closed.",
    
    # Finding extrema
    "存在性的问题解决了": "The existence problem is solved",
    ",下面的任务就是根据极值点的特点想办法找到它们。": ", now the task is to find ways to locate them based on the characteristics of extreme points.",
    "对一个连续函数来说": "For a continuous function",
    ",既然全局的极值点在封闭区间存在。": ", since global extreme points exist on a closed interval.",
    "而一般来说": "Generally speaking",
    ",全": ", global",
    "局极值点又是从众多的局部极值点选拔出来的": "extreme points are selected from among many local extreme points",
    "因而": "therefore",
    ",先找出局部极值点就成了": ", finding local extreme points first becomes",
    "当务之急": "the top priority",
    "。那么局部极值点长啥样呢?": ". So what do local extreme points look like?",
    "请看定理": "See the theorem",
    
    # Fermat's Theorem
    "费尔马(": "Fermat (",
    "定理": "'s Theorem",
    "如果 ": "If ",
    "点是函数 f(": "is a point where function f(",
    "的局部极值点,": "has a local extreme value,",
    "而 ": "and ",
    "存": "ex",
    "在": "ists",
    ",那么": ", then",
    "证明": "Proof",
    ":不妨先假设 ": ": Let's first assume ",
    "点是 f(": "is a local maximum of f(",
    "的局部最大值": "",
    ",极小值": ", the minimum",
    "的情形也可同样证": "case can be proved similarly",
    "明": "",
    "点是局部最大值": "Being a local maximum",
    "也就意味着": "means",
    "在包含 ": "in a small region containing ",
    "的一个小区域内": "",
    "下列不等式": "the following inequality",
    "成立": "holds",
    "于是": "Thus",
    "上式中": "In the above expression",
    "由于分子非负": "since the numerator is non-negative",
    "分母为负": "the denominator is negative",
    "因此": "therefore",
    "同理": "Similarly",
    
    # Conclusion
    "至此": "At this point",
    ",我们得到了函数在 ": ", we have obtained that the function at ",
    "点的左右导数一边非负、一边非正的结": "has left and right derivatives that are non-negative on one side and non-positive on the other, the con",
    "论。": "clusion.",
    "既然": "Since",
    "存在": "exists",
    "其左右导数必然相等": "its left and right derivatives must be equal",
    "那就只有": "Then it can only be",
    
    # Critical points
    "敲黑板": "Important point",
    ":费尔马定理只告诉您": ": Fermat's Theorem only tells you",
    ",如果局部极值点存在导数": ", if a local extreme point has a derivative",
    ",那么该导数为 ": ", then that derivative equals ",
    "他可没说": "It doesn't say",
    ",所有的局部极值点,导数都为 ": ", all local extreme points have derivative equal to ",
    "为啥?  因为": "Why? Because",
    "有的局部极值点,导数": "some local extreme points have derivatives that",
    "不存在": "do not exist",
    "这些": "These",
    "导": "points",
    "数": "where",
    "存在 的": "does not",
    "点": "exist",
    "和": "and",
    "点,统": ", are",
    "称": "collectively",
    "为 函": "called",
    "数 的": "the function's",
    "临": "critical",
    "界": "",
    "点 ": "points ",
    
    # Finding extreme values procedure
    "辛苦走到这里": "After all this hard work",
    ",总算是找到了一点求极值的道道了!": ", we've finally found some methods for finding extreme values!",
    ",找出": ", find",
    "函数的临界": "the function's critical",
    "点,也就是那些不存在导数或者导数为 ": "points, that is, those points where the derivative doesn't exist or equals ",
    "的": "",
    ";其次": "; second",
    "比较函数在区间端点和临": "compare function values at interval endpoints and critical",
    "界点的值": "points",
    "即可确定全局极值和局部极值。": "to determine global and local extreme values.",
    "之所以要把区间端点的函数值": "The reason we need to separately compare the function values at interval endpoints",
    ",单拿出来比较": "",
    ",是因为区间的端点,虽不满": ", is because interval endpoints, although not satis",
    "足关于局部极值点的定义": "fying the definition of local extreme points",
    ",但是它有可能是全局极值点。": ", may still be global extreme points.",
    ",严格的单调函": ", strictly monotonic func",
    ",一定是在端点取得全局极值": ", always attain global extreme values at endpoints",
    ",并且内部没有局部极值点的。": ", and have no local extreme points in the interior.",
    ",如何判断我们辛苦找出来的函数的临界点是局部最大值": ", how do we determine whether the critical points we've worked hard to find are local maxima",
    ",还": ", or",
    "是局部最": "local mini",
    "小值呢?": "ma?",
    "要解决这个问题": "To solve this problem",
    ",还得请小趋势": ", we need to call upon the local trend",
    "导数出马": "derivative",
    "。我们在上一章就介绍过": ". We introduced in the previous chapter",
    "函": "the",
    "数的在一点的导数值的正负": "sign of a function's derivative at a point",
    ",决定着函数在此点的上升": ", determines whether the function is increasing",
    "或者下降的小趋势。": "or decreasing at that point.",
    "由": "From",
    "此不难推出": "this, it's not hard to deduce",
    ",如果在某个区间内": ", if on some interval",
    "函数的导数为正": "the function's derivative is positive",
    ",则函数在此区间为增函数。": ", then the function is increasing on that interval.",
    "反之": "Conversely",
    ",导数值为负": ", if the derivative is negative",
    ",则函数为减函数。": ", then the function is decreasing.",
    
    # Common punctuation (keep as-is for most)
    "，": ",",
    "。": ".",
    "法": "",
}


def translate_segment(source: str) -> str:
    """Translate a single segment using the translation dictionary."""
    # First normalize punctuation spacing
    normalized = normalize_punctuation_spacing(source)
    
    # Exact match on normalized text
    if normalized in TRANSLATIONS:
        return TRANSLATIONS[normalized]
    
    # Fallback: try original source (in case it was already normalized in TRANSLATIONS)
    if source in TRANSLATIONS:
        return TRANSLATIONS[source]
    
    # Return original source if no translation found
    return source


def main():
    # Load extracted segments
    with open(EXTRACTED_SEGMENTS, "r", encoding="utf-8") as f:
        segments = json.load(f)
    
    # Translate each segment
    translated = []
    for seg in segments:
        translation = translate_segment(seg["source"])
        translated.append({
            "id": seg["id"],
            "source": seg["source"],
            "translation": translation
        })
    
    # Write translated segments
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRANSLATED_SEGMENTS, "w", encoding="utf-8") as f:
        json.dump(translated, f, ensure_ascii=False, indent=2)
    
    # Count how many were actually translated vs kept as-is
    translated_count = sum(1 for t in translated if t["translation"] != t["source"])
    print(f"Translated {translated_count}/{len(translated)} segments")
    print(f"Output: {TRANSLATED_SEGMENTS}")


if __name__ == "__main__":
    main()
