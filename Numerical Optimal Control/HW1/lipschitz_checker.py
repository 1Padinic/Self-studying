#!/usr/bin/env python3
r"""
lipschitz_checker.py  --  classify a function as

      GLOBALLY LIPSCHITZ  (GL) | LOCALLY LIPSCHITZ (LL) | NOT LOCALLY LIPSCHITZ (NLL)

Written for NOC / Exercise 1, problem 1(a).

Theory
------
f : D subset R^n -> R^m  is Lipschitz on S subset D with constant L if

        || f(x) - f(y) ||  <=  L || x - y ||        for all x, y in S.

The smallest valid L on a convex set S equals the supremum of the difference
quotient, and (where f is differentiable) equals sup_x ||Df(x)|| -- the operator
norm of the Jacobian (|f'(x)| in the scalar case). From this:

  * GLOBALLY Lipschitz  <=>  sup over ALL of D of the slope is finite.
  * LOCALLY  Lipschitz  <=>  the slope is *locally bounded*: for every point x0
                             the difference quotient stays bounded as x,y -> x0.
  * NOT locally Lipschitz <=> at some point x0 the slope blows up
                             (e.g. sqrt|x| at 0), or f jumps (a discontinuity).

So the ONLY thing separating "locally but not globally" from "not locally" is
*where* the slope becomes unbounded:

    unbounded only as ||x|| -> infinity   =>  LOCALLY Lipschitz (not global)
    unbounded near a finite point x0       =>  NOT locally Lipschitz at x0.

Strategy of this script
------------------------
1. NLL test  (a local, finite-point property):
   at each "suspect" point x0 (always the origin, plus points found by a coarse
   scan, plus any the user supplies) measure the one-sided slope
        S(r) = max_{||u||=r} ||f(x0+u) - f(x0)|| / r
   for geometrically shrinking r.  If S(r) -> infinity  =>  NOT locally Lipschitz.

2. GL vs LL test  (only reached if no finite blow-up exists):
   estimate the largest local slope  g(R) = max_{||x||<=R} ||Df(x)||  over
   growing R.  Bounded as R grows  =>  GLOBAL (report L ~ g).  Growing  =>  LOCAL.

The numeric engine below handles any  f : R^n -> R^m .  For a *scalar* symbolic
expression it additionally reports the EXACT Lipschitz constant / exact bad
points via SymPy.

Usage
-----
    python lipschitz_checker.py                 # run the Exercise-1 demo (all 9)
    python lipschitz_checker.py "x**2"          # classify a scalar expression
    python lipschitz_checker.py "sqrt(Abs(x))"  # ^ or Abs(x)**Rational(1,2)

    # from Python, for your own (possibly vector) function:
    from lipschitz_checker import classify
    classify(lambda x: np.linalg.norm(x), dim=3, name="||x||_2")
"""
from __future__ import annotations

import argparse
import numpy as np

# large slopes (exp, x^2, ...) legitimately overflow far from the origin; the
# code filters non-finite values, so silence the cosmetic runtime warnings.
np.seterr(over="ignore", invalid="ignore", divide="ignore")

# --------------------------------------------------------------------------- #
#  tunable thresholds (documented so they can be justified in a report)        #
# --------------------------------------------------------------------------- #
BLOWUP_RADII  = [10.0 ** (-k) for k in range(1, 10)]  # 1e-1 ... 1e-9
BLOWUP_ABS    = 1.0e3   # final slope must exceed this to count as "blowing up"
BLOWUP_GROW   = 30.0    # ... and must have grown by at least this factor
GLOBAL_RS     = (1.0, 10.0, 100.0, 1000.0)            # region sizes for g(R)
GLOBAL_GROW   = 5.0     # g(R) grown by more than this over the range => not GL
FD_STEP       = 1.0e-4  # finite-difference step for the Jacobian norm


# --------------------------------------------------------------------------- #
#  small geometry helpers                                                      #
# --------------------------------------------------------------------------- #
def _sphere(dim, n, rng):
    """n unit vectors uniformly on the sphere in R^dim (rows)."""
    v = rng.standard_normal((n, dim))
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def _ball(dim, n, R, rng):
    """n points uniformly in the ball of radius R in R^dim (rows)."""
    u = _sphere(dim, n, rng)
    r = R * rng.random(n) ** (1.0 / dim)
    return u * r[:, None]


def _f(f, x):
    """Evaluate user f at 1-D point x, return a 1-D float array (or nan array)."""
    try:
        val = np.atleast_1d(np.asarray(f(x), dtype=float)).ravel()
        return val
    except Exception:
        return np.array([np.nan])


# --------------------------------------------------------------------------- #
#  primitive slope measurements                                               #
# --------------------------------------------------------------------------- #
def _slope_from(f, x0, r, dirs):
    """max over directions of ||f(x0 + r u) - f(x0)|| / r  (one-sided slope)."""
    f0 = _f(f, x0)
    best = 0.0
    for u in dirs:
        s = np.linalg.norm(_f(f, x0 + r * u) - f0) / r
        if np.isfinite(s):
            best = max(best, s)
    return best


def _jac_opnorm(f, x, delta=FD_STEP):
    """
    Estimate ||Df(x)||_2 (largest singular value of the Jacobian) by central
    finite differences.  This is the local Lipschitz constant at a smooth x.
    """
    x = np.asarray(x, float)
    n = x.shape[0]
    f0 = _f(f, x)
    m = f0.shape[0]
    J = np.empty((m, n))
    for i in range(n):
        e = np.zeros(n)
        e[i] = delta
        J[:, i] = (_f(f, x + e) - _f(f, x - e)) / (2.0 * delta)
    if not np.all(np.isfinite(J)):
        return np.nan
    return np.linalg.norm(J, 2)


# --------------------------------------------------------------------------- #
#  step 1 : blow-up (NLL) detection at a point                                #
# --------------------------------------------------------------------------- #
def estimate_blowup(f, x0, rng, n_dir=41):
    """
    Return (diverges, S, radii): does the difference quotient at x0 blow up
    as r->0?  For each direction u and radius r we take the largest of

        ||f(x0+ru) - f(x0)|| / r          (one-sided; needs f(x0) finite)
        ||f(x0-ru) - f(x0)|| / r
        ||f(x0+ru) - f(x0-ru)|| / (2r)    (straddling; independent of f(x0))

    The straddling quotient also catches jump discontinuities (e.g. a step)
    and points where f itself is undefined (e.g. x/||x|| at 0).
    """
    x0 = np.atleast_1d(np.asarray(x0, float))
    dirs = _sphere(x0.shape[0], n_dir, rng)
    f0 = _f(f, x0)
    f0_ok = bool(np.all(np.isfinite(f0)))
    S = []
    for r in BLOWUP_RADII:
        best = 0.0
        for u in dirs:
            fp_ = _f(f, x0 + r * u)
            fm_ = _f(f, x0 - r * u)
            cands = [np.linalg.norm(fp_ - fm_) / (2.0 * r)]
            if f0_ok:
                cands.append(np.linalg.norm(fp_ - f0) / r)
                cands.append(np.linalg.norm(fm_ - f0) / r)
            for s in cands:
                if np.isfinite(s):
                    best = max(best, s)
        S.append(best)
    S = np.array(S)
    diverges = bool(
        S[-1] > BLOWUP_ABS
        and S[-1] > BLOWUP_GROW * max(S[0], 1e-12)
        and S[-1] >= S[-4]                     # still increasing at the finest scales
    )
    return diverges, S, BLOWUP_RADII


def find_suspects(f, dim, rng, R=5.0, n=400, r=1e-6, keep=3):
    """Points where a fixed-scale slope is largest -> candidate singularities."""
    pts = _ball(dim, n, R, rng)
    dirs = _sphere(dim, 8, rng)
    scores = np.array([_slope_from(f, p, r, dirs) for p in pts])
    order = np.argsort(scores)[-keep:]
    return [pts[i] for i in order]


# --------------------------------------------------------------------------- #
#  step 2 : global vs local (growth of the slope with region size)            #
# --------------------------------------------------------------------------- #
def global_slope_growth(f, dim, rng, n_base=600):
    """Return (bounded, L_estimate, g_values, Rs)."""
    g = []
    for R in GLOBAL_RS:
        base = np.vstack([_ball(dim, n_base, R, rng), _sphere(dim, n_base, rng) * R])
        best = 0.0
        for b in base:
            v = _jac_opnorm(f, b)
            if np.isfinite(v):
                best = max(best, v)
        g.append(best)
    g = np.array(g)
    growth = g[-1] / max(g[0], 1e-12)
    bounded = not (growth > GLOBAL_GROW and g[-1] > g[0])
    return bounded, float(np.max(g)), g, GLOBAL_RS


# --------------------------------------------------------------------------- #
#  top-level numeric classifier                                               #
# --------------------------------------------------------------------------- #
def classify(f, dim=1, suspects=None, name=None, rng=None, verbose=True):
    """
    Classify f : R^dim -> R^m .  `f` takes a 1-D numpy array of length `dim`
    and returns a scalar or 1-D array.  Returns a dict with the verdict.
    """
    if rng is None:
        rng = np.random.default_rng(0)

    # ---- assemble suspect points: origin first, then user, then scan ----
    cand = [np.zeros(dim)]
    if suspects:
        cand += [np.atleast_1d(np.asarray(s, float)) for s in suspects]
    cand += find_suspects(f, dim, rng)

    # ---- step 1: not-locally-Lipschitz? ----
    for x0 in cand:
        diverges, S, radii = estimate_blowup(f, x0, rng)
        if diverges:
            res = dict(verdict="NOT LOCALLY LIPSCHITZ", tag="NLL",
                       L=np.inf, bad_point=x0, slope_seq=S, radii=radii, name=name)
            if verbose:
                _report(res)
            return res

    # ---- step 2: global vs local ----
    bounded, L, g, Rs = global_slope_growth(f, dim, rng)
    res = dict(verdict="GLOBALLY LIPSCHITZ" if bounded else "LOCALLY LIPSCHITZ",
               tag="GL" if bounded else "LL",
               L=(L if bounded else np.inf), L_local=L, g=g, Rs=Rs, name=name)
    if verbose:
        _report(res)
    return res


def _report(res):
    head = f"  [{res['name']}]" if res.get("name") else ""
    print(f"\n=== {res['verdict']} ({res['tag']}){head} ===")
    if res["tag"] == "NLL":
        p = res["bad_point"]
        p = float(p[0]) if p.shape[0] == 1 else np.round(p, 4)
        print(f"    slope blows up near x0 = {p}")
        print("    r      :  " + "  ".join(f"{r:8.0e}" for r in res["radii"]))
        print("    slope  :  " + "  ".join(f"{s:8.2e}" for s in res["slope_seq"]))
        print("    -> difference quotient -> infinity : no finite local constant.")
    else:
        print("    R          :  " + "  ".join(f"{R:10.0f}" for R in res["Rs"]))
        print("    max ||Df|| :  " + "  ".join(f"{v:10.3g}" for v in res["g"]))
        if res["tag"] == "GL":
            print(f"    -> slope stays bounded as R grows.  Lipschitz constant L ~= {res['L']:.4g}")
        else:
            print("    -> slope finite everywhere but grows without bound as ||x||->inf.")


# --------------------------------------------------------------------------- #
#  optional: EXACT answer for a scalar symbolic expression (SymPy)            #
# --------------------------------------------------------------------------- #
def scalar_symbolic(expr_str, verbose=True):
    """Exact GL/LL/NLL + exact L for a 1-D expression in the variable x."""
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        parse_expr, standard_transformations,
        implicit_multiplication_application, convert_xor)

    x = sp.Symbol("x", real=True)
    tran = standard_transformations + (implicit_multiplication_application, convert_xor)
    loc = {"x": x, "e": sp.E, "pi": sp.pi, "abs": sp.Abs, "sqrt": sp.sqrt,
           "sqrt": sp.sqrt, "sqrtn": sp.sqrt}
    expr = parse_expr(expr_str, local_dict=loc, transformations=tran)
    fp = sp.diff(expr, x)

    INF = (sp.oo, -sp.oo, sp.zoo)
    is_inf = lambda v: (v in INF) or bool(getattr(v, "is_infinite", False))

    # collect finite suspect points (singularities of f and f')
    suspects = set()
    for g in (expr, fp):
        try:
            s = sp.singularities(g, x, sp.Reals)
            if isinstance(s, sp.Set) and s.is_FiniteSet:
                for p in s:
                    if p.is_real and p.is_finite:
                        suspects.add(p)
        except Exception:
            pass

    bad = []
    for p in sorted(suspects, key=lambda z: float(z)):
        # is f actually defined (finite, real) at p?  (skip domain holes like 1/x @0)
        try:
            val = complex(expr.subs(x, p).evalf())
            if not (np.isfinite(val.real) and abs(val.imag) < 1e-9):
                continue
        except Exception:
            continue
        # jump discontinuity?
        try:
            lft = sp.limit(expr, x, p, "-")
            rgt = sp.limit(expr, x, p, "+")
            if not any(is_inf(v) for v in (lft, rgt)) and sp.simplify(lft - rgt) != 0:
                bad.append((p, "jump discontinuity"))
                continue
        except Exception:
            pass
        # derivative -> infinity?
        for d in ("+", "-"):
            try:
                if is_inf(sp.limit(sp.Abs(fp), x, p, d)):
                    bad.append((p, "infinite slope (f' -> oo)"))
                    break
            except Exception:
                pass

    # exact  sup_x |f'(x)|  =  smallest global Lipschitz constant.
    # Look at: bounded corners (singularities of f' with finite |f'|), interior
    # critical points of |f'| (where f''=0), and the behaviour as x -> +/-oo.
    # Return oo if unbounded, or None if it cannot be settled symbolically.
    def exact_sup_abs():
        cands = []
        try:
            s = sp.singularities(fp, x, sp.Reals)
        except Exception:
            s = sp.S.EmptySet
        if s == sp.S.EmptySet:
            pass
        elif isinstance(s, sp.Set) and s.is_FiniteSet:
            for p in s:                                   # bounded corner or blow-up?
                if not (p.is_real and p.is_finite):
                    continue
                for d in ("+", "-"):
                    try:
                        lim = sp.limit(sp.Abs(fp), x, p, d)
                    except Exception:
                        continue
                    if is_inf(lim):
                        return sp.oo
                    if lim.is_real and lim.is_finite and lim.is_number:
                        cands.append(lim)
        else:
            return None                                   # infinitely many (e.g. tan)
        try:
            crit = sp.solve(sp.diff(fp, x), x)
        except Exception:
            crit = []
        for c in crit if isinstance(crit, (list, tuple)) else []:
            if getattr(c, "is_real", False):
                try:
                    v = sp.simplify(sp.Abs(fp.subs(x, c)))
                except Exception:
                    continue
                if is_inf(v):
                    return sp.oo
                if v.is_real and v.is_finite and v.is_number:
                    cands.append(v)
        for pt in (sp.oo, -sp.oo):
            try:
                lim = sp.limit(sp.Abs(fp), x, pt)
            except Exception:
                continue
            if is_inf(lim):
                return sp.oo
            if all(getattr(lim, a, False) for a in ("is_real", "is_finite", "is_number")):
                cands.append(lim)
        if not cands:
            return None
        try:
            return sp.simplify(sp.Max(*cands))
        except Exception:
            return None

    if bad:
        res = dict(verdict="NOT LOCALLY LIPSCHITZ", tag="NLL",
                   derivative=fp, L=sp.oo, bad=bad)
    else:
        sup = exact_sup_abs()
        if sup is None:
            res = dict(verdict="UNDETERMINED (symbolic)", tag="?",
                       derivative=fp, L=None, bad=[])
        elif is_inf(sup):
            res = dict(verdict="LOCALLY LIPSCHITZ", tag="LL",
                       derivative=fp, L=sp.oo, bad=[])
        else:
            res = dict(verdict="GLOBALLY LIPSCHITZ", tag="GL",
                       derivative=fp, L=sp.simplify(sup), bad=[])

    if verbose:
        print(f"\n=== SymPy exact analysis : {res['verdict']} ({res['tag']}) ===")
        print(f"    f(x)  = {expr}")
        print(f"    f'(x) = {res['derivative']}")
        if res["bad"]:
            for p, why in res["bad"]:
                print(f"    at x = {p}: {why}")
        elif res["tag"] == "GL":
            print(f"    exact Lipschitz constant  L = sup|f'| = {res['L']}")
        elif res["tag"] == "LL":
            print("    |f'| is finite everywhere but unbounded  =>  local, not global.")
        else:
            print("    sup|f'| not resolved symbolically -> rely on the numeric verdict.")
    return res


# --------------------------------------------------------------------------- #
#  demo : Exercise 1, problem 1(a)  --  all nine functions                     #
# --------------------------------------------------------------------------- #
def demo():
    rng = np.random.default_rng(0)
    A = np.array([[2.0, 1.0, 0.0],
                  [0.0, 3.0, 1.0],
                  [1.0, 0.0, 1.0]])
    smax = np.linalg.norm(A, 2)

    # (function, dim, printable name, expected tag from the answer key)
    problems = [
        (lambda x: x[0] ** 2,                         1, "x^2",                 "LL"),
        (lambda x: np.sqrt(np.abs(x[0])),             1, "|x|^(1/2)",           "NLL"),
        (lambda x: np.sign(x[0]) * np.sqrt(np.abs(x[0])), 1, "sign(x)|x|^(1/2)","NLL"),
        (lambda x: x @ x,                             3, "||x||^2",             "LL"),
        (lambda x: np.linalg.norm(x),                 3, "||x||",               "GL"),
        (lambda x: np.sqrt(np.linalg.norm(x)),        3, "||x||^(1/2)",         "NLL"),
        (lambda x: np.linalg.norm(A @ x),             3, "||Ax||",              "GL"),
        (lambda x: np.sin(x @ (A @ x)),               3, "sin(x^T A x)",        "LL"),
        (lambda x: np.sin(np.linalg.norm(x)),         3, "sin(||x||)",          "GL"),
    ]
    roman = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]

    print("Exercise 1(a) -- classifying each function as GL / LL / NLL")
    print(f"(using A with largest singular value sigma_max = {smax:.4f})")
    rows = []
    for tag_id, (f, dim, nm, expected) in zip(roman, problems):
        res = classify(f, dim=dim, name=nm, rng=rng, verbose=True)
        rows.append((tag_id, nm, res["tag"], expected))

    # summary checkbox table
    print("\n" + "=" * 62)
    print("SUMMARY".center(62))
    print("=" * 62)
    print(f"{'#':>4}  {'function':<18} {'GL':^4}{'LL':^4}{'NLL':^4}  {'(key)':>6}")
    print("-" * 62)
    for tag_id, nm, got, exp in rows:
        cell = {k: (" X " if got == k else " . ") for k in ("GL", "LL", "NLL")}
        ok = "ok" if got == exp else "!!"
        print(f"{tag_id:>4}  {nm:<18} {cell['GL']:^4}{cell['LL']:^4}{cell['NLL']:^4}  {exp:>4} {ok}")
    print("-" * 62)
    print("X = classifier's verdict;  (key) = expected answer;  ok = matches key")


# --------------------------------------------------------------------------- #
#  CLI                                                                          #
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(
        description="Classify a function as GL / LL / NLL (Lipschitz continuity).")
    ap.add_argument("expr", nargs="?",
                    help="scalar expression in x, e.g. \"x**2\" or \"sqrt(Abs(x))\". "
                         "If omitted, runs the Exercise-1 demo (all 9 functions).")
    args = ap.parse_args()

    if args.expr is None:
        demo()
        return

    # scalar expression: exact (symbolic) + numeric cross-check
    try:
        sym = scalar_symbolic(args.expr)
    except Exception as exc:
        sym = None
        print(f"[symbolic step unavailable: {exc}]")

    try:
        import sympy as sp
        from sympy.parsing.sympy_parser import (
            parse_expr, standard_transformations,
            implicit_multiplication_application, convert_xor)
        x = sp.Symbol("x", real=True)
        tran = standard_transformations + (implicit_multiplication_application, convert_xor)
        expr = parse_expr(args.expr,
                          local_dict={"x": x, "e": sp.E, "pi": sp.pi, "abs": sp.Abs},
                          transformations=tran)
        fl = sp.lambdify(x, expr, "numpy")
        f = lambda arr: np.atleast_1d(np.asarray(fl(arr[0]), dtype=float))
        classify(f, dim=1, name=str(expr))
    except Exception as exc:
        print(f"[numeric step failed: {exc}]")


if __name__ == "__main__":
    main()
