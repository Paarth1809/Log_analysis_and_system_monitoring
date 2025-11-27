"""
Version comparison and range-matching utility.

Features:
- parse_version(v): returns a tuple (numeric_parts:list[int], pre_release:str or "")
- compare_versions(a, b): returns -1 if a<b, 0 if equal, 1 if a>b
- satisfies(version, range_expr): returns True/False
  Supports operators: =, ==, !=, >, >=, <, <=
  Supports hyphen ranges: "1.2.0 - 1.4.5"
  Supports caret ^ (compatible with), tilde ~ (patch compatible),
  wildcards "1.2.x", "1.*"
  Supports OR via "||" and AND via "," or space (interpreted as AND)
Notes:
- Works with semantic versions and non-semver dotted versions (Windows style).
- Pre-release tags (e.g., 1.2.3-beta) are considered lower than the release.
- This implementation is intentionally opinionated and robust for SOC/CVE matching.
"""

import re
from functools import cmp_to_key

# -------------------------
# Parsing & normalization
# -------------------------
NUM_RE = re.compile(r'(\d+)')

def parse_version(v: str):
    """
    Parse a version string into (numeric_parts, prerelease_str).
    numeric_parts: list of ints
    prerelease_str: remaining suffix after '-' or non-numeric suffix (lowercase)
    Examples:
      "1.2.3" -> ([1,2,3], "")
      "10.0.19044" -> ([10,0,19044], "")
      "1.2.3-beta1" -> ([1,2,3], "beta1")
      "1.2.x" -> ([1,2], "x")  (x treated as prerelease placeholder)
    """
    if v is None:
        return ([], "")

    s = str(v).strip()
    if s == "":
        return ([], "")

    # split off pre-release after '-' (common semver)
    if "-" in s:
        head, tail = s.split("-", 1)
        prerelease = tail.strip()
    else:
        head = s
        prerelease = ""

    # Replace common non-digit separators with dots, keep letters after last dot as suffix
    # Extract numeric tokens
    tokens = []
    for part in re.split(r'[._+]', head):
        m = NUM_RE.search(part)
        if m:
            try:
                tokens.append(int(m.group(1)))
            except:
                # fallback ignore
                pass
        else:
            # if 'x' or '*' or non-numeric we stop numeric capture for that token
            if part.lower() in ("x", "*"):
                # indicate wildcard by leaving tokens as-is and set prerelease to 'x'
                prerelease = ("x" if prerelease == "" else prerelease)
            # else ignore

    return (tokens, prerelease.lower())


def _cmp_numeric_lists(a_list, b_list):
    """
    Compare numeric lists element-wise.
    Return -1,0,1
    """
    la = len(a_list)
    lb = len(b_list)
    L = max(la, lb)
    for i in range(L):
        ai = a_list[i] if i < la else 0
        bi = b_list[i] if i < lb else 0
        if ai < bi:
            return -1
        if ai > bi:
            return 1
    return 0


# -------------------------
# Core comparison
# -------------------------
def compare_versions(a: str, b: str) -> int:
    """
    Compare two version strings.
    Returns -1 if a < b, 0 if equal, 1 if a > b
    """
    a_num, a_pre = parse_version(a)
    b_num, b_pre = parse_version(b)

    num_cmp = _cmp_numeric_lists(a_num, b_num)
    if num_cmp != 0:
        return num_cmp

    # If numeric equal, consider prerelease:
    # No prerelease > any prerelease (release > prerelease)
    if a_pre == b_pre:
        return 0
    if a_pre == "":
        return 1
    if b_pre == "":
        return -1

    # both have prerelease strings: compare lexicographically
    if a_pre < b_pre:
        return -1
    if a_pre > b_pre:
        return 1
    return 0


# -------------------------
# Range helpers
# -------------------------
def _op_eval(version, op, target):
    cmpv = compare_versions(version, target)
    if op in ("=", "=="):
        return cmpv == 0
    if op == "!=":
        return cmpv != 0
    if op == ">":
        return cmpv == 1
    if op == ">=":
        return cmpv >= 0
    if op == "<":
        return cmpv == -1
    if op == "<=":
        return cmpv <= 0
    raise ValueError(f"Unsupported operator: {op}")


def _expand_wildcard_range(range_expr: str):
    """
    Convert wildcard like "1.2.x" or "1.*" into (lower, upper) inclusive/exclusive.
    "1.2.x" => >=1.2.0 and <1.3.0
    "1.*"   => >=1.0.0 and <2.0.0
    Returns tuple (lower_expr, upper_expr) where expressions are (op, ver)
    """
    r = range_expr.strip()
    parts = r.split(".")
    if parts[-1].lower() in ("x", "*"):
        # drop the wildcard
        base = ".".join(parts[:-1])
        # lower is >= base.0
        lower = (">=", base + ("" if base == "" else ".") + "0")
        # upper is < increment(base)
        # increment the last numeric part
        nums, _ = parse_version(base)
        if not nums:
            # wildcard like "*"
            return ((">=", "0"), ("<", "1000000"))
        # increment last
        nums[-1] += 1
        upper_ver = ".".join(str(n) for n in nums)
        return (lower, ("<", upper_ver))
    else:
        # not a wildcard
        return None


def _caret_range(ver: str):
    """
    ^1.2.3 means >=1.2.3 and <2.0.0 (if major!=0)
    If major==0, caret rules are more restrictive:
      ^0.2.3 -> >=0.2.3 <0.3.0
      ^0.0.3 -> >=0.0.3 <0.0.4
    We'll implement a reasonable interpretation:
    """
    nums, _ = parse_version(ver)
    if not nums:
        return None
    if len(nums) == 1:
        major = nums[0]
        if major == 0:
            # ^0 -> >=0 <1 (unlikely)
            return ((">=", ver), ("<", str(major+1)))
        return ((">=", ver), ("<", str(major+1)))
    # has at least major,minor
    major = nums[0]
    minor = nums[1] if len(nums) > 1 else 0
    if major == 0:
        # ^0.minor.patch -> <0.(minor+1).0
        upper = [0, minor+1]
        upper_ver = ".".join(str(x) for x in upper)
        return ((">=", ver), ("<", upper_ver))
    else:
        upper = [major+1]
        upper_ver = ".".join(str(x) for x in upper)
        return ((">=", ver), ("<", upper_ver))


def _tilde_range(ver: str):
    """
    ~1.2.3 := >=1.2.3 <1.3.0
    ~1.2   := >=1.2.0 <1.3.0
    ~1     := >=1.0.0 <2.0.0
    """
    nums, _ = parse_version(ver)
    if not nums:
        return None
    if len(nums) == 1:
        low = ver
        high = str(nums[0]+1)
        return ((">=", low), ("<", high))
    # increment minor
    major = nums[0]
    minor = nums[1] if len(nums) > 1 else 0
    upper = [major, minor+1]
    upper_ver = ".".join(str(x) for x in upper)
    return ((">=", ver), ("<", upper_ver))


def _parse_single_range(token: str):
    """
    Parse a single token (no OR) and return a list of (op, version) requirements
    that must all be true (AND).
    """
    token = token.strip()
    if token == "":
        return []

    # hyphen range "1.2.0 - 1.4.5"
    if " - " in token:
        left, right = token.split(" - ", 1)
        return [(">=", left.strip()), ("<=", right.strip())]

    # caret ^1.2.3
    if token.startswith("^"):
        inner = token[1:].strip()
        rng = _caret_range(inner)
        if rng:
            return [rng[0], rng[1]]

    # tilde ~1.2.3
    if token.startswith("~"):
        inner = token[1:].strip()
        rng = _tilde_range(inner)
        if rng:
            return [rng[0], rng[1]]

    # wildcard e.g., 1.2.x or 1.* or *.x
    if "x" in token or "*" in token:
        expanded = _expand_wildcard_range(token)
        if expanded:
            return [expanded[0], expanded[1]]

    # comparators like >=, <=, >, <, !=, ==, =
    m = re.match(r'^(>=|<=|>|<|!=|==|=)\s*(.+)$', token)
    if m:
        op = m.group(1)
        ver = m.group(2).strip()
        return [(op, ver)]

    # plain range like "1.2" treat as exact or >=1.2.0 <1.3.0 ?
    # We'll treat plain "1.2.3" as exact equality, and "1.2" as wildcard "1.2.x"
    if re.match(r'^\d+(\.\d+){2,}$', token):
        return [("=", token)]
    if re.match(r'^\d+(\.\d+){0,1}$', token):
        # treat as wildcard minor or major
        expanded = _expand_wildcard_range(token + ".x")
        if expanded:
            return [expanded[0], expanded[1]]

    # fallback: try equality
    return [("=", token)]


# -------------------------
# Public function: satisfies
# -------------------------
def satisfies(version: str, range_expr: str) -> bool:
    """
    Check if 'version' satisfies 'range_expr'.
    range_expr supports:
      - OR with '||'
      - AND with ',' or space (interpreted as AND)
      - individual operators via _parse_single_range
    Examples:
      satisfies("1.2.3", ">=1.2.0 <2.0.0")
      satisfies("1.5.0", "^1.2.0")
      satisfies("1.2.3", "1.2.x")
      satisfies("10.0.19044", ">=10.0.0")
    """

    if range_expr is None or range_expr.strip() == "":
        return True  # empty range accepts everything

    # OR-split by '||'
    or_parts = [p.strip() for p in range_expr.split("||") if p.strip() != ""]
    for or_part in or_parts:
        # AND-split by comma or spaces conservatively
        # First split by comma; if no comma, split by whitespace tokens preserving quoted ranges
        and_tokens = []
        if "," in or_part:
            and_tokens = [t for t in or_part.split(",") if t.strip() != ""]
        else:
            # split by whitespace but keep comparators like "<=1.2.3"
            and_tokens = [t for t in re.split(r'\s+', or_part) if t.strip() != ""]

        all_true = True
        for token in and_tokens:
            reqs = _parse_single_range(token)
            # every requirement in reqs must be true (e.g., >=a and <b)
            for op, ver in reqs:
                if op not in (">=", ">", "<=", "<", "=", "==", "!="):
                    # op from caret/tilde/wildcard returned as (">=", ver) or ("<", ver)
                    pass
                # Evaluate using comparator
                try:
                    ok = _op_eval(version, op, ver)
                except Exception:
                    ok = False
                if not ok:
                    all_true = False
                    break
            if not all_true:
                break

        if all_true:
            return True

    return False


# -------------------------
# Some convenience helpers
# -------------------------
def version_key(v):
    """Return key usable for sorting versions (higher -> newer)"""
    return cmp_to_key(lambda a, b: compare_versions(a, b))(v)


# -------------------------
# Self-test / examples
# -------------------------
if __name__ == "__main__":
    tests = [
        ("1.2.3", ">=1.2.0"),
        ("1.2.3", ">=1.2.4"),
        ("1.5.0", "^1.2.3"),
        ("0.2.5", "^0.2.3"),
        ("1.2.3", "~1.2.0"),
        ("1.2.3", "1.2.x"),
        ("10.0.19044", ">=10.0.0"),
        ("1.2.3-beta", ">=1.2.3"),
        ("1.2.3-beta", "<=1.2.3"),
    ]

    for ver, rng in tests:
        print(f"{ver} satisfies {rng}? -> {satisfies(ver, rng)}")

    # comparison checks
    cmp_cases = [
        ("1.2.3", "1.2.4"),
        ("1.2.3", "1.2.3"),
        ("10.0.19044", "10.0.19043"),
        ("1.2.3-beta", "1.2.3"),
    ]
    for a, b in cmp_cases:
        print(f"compare_versions({a}, {b}) -> {compare_versions(a,b)}")
