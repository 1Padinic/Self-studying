# Linear Regression & Gradient Descent — Explained

A companion guide to `task1.py`. The script is a small teaching demo that makes **one point** three times:

> A model is only as good as the *shape* you assume for it. Fit a straight line and it only works on straight data. When the data is curved, you must change the shape you fit — and you can find the best fit either with an exact **formula** or by **iterating** (gradient descent).

---

## 1. What is regression, really?

You have data: pairs of `(x, y)`. You believe `y` depends on `x` through some rule, and you want to find that rule.

The simplest rule is a line through the origin:

```
  y ≈ w * x
```

Here `w` (the **weight** or slope) is the one number we're trying to learn. "Learning" just means: **pick the `w` that makes the predictions closest to the real data.**

To make "closest" precise, we measure how wrong a given `w` is with the **squared error**:

```
  Error(w) = sum over all points of ( prediction − truth )²
           = Σ ( w·xᵢ − yᵢ )²
```

- We square each miss so that positive and negative errors don't cancel out, and so big misses are punished more than small ones.
- The best `w` is the one that makes this total as **small as possible**.

This whole approach is called **Ordinary Least Squares (OLS)** — "least squares" because we minimize the sum of squared errors.

---

## 2. The exact formula (closed-form OLS)

For the simple one-weight case, we don't need to guess. Calculus gives an exact answer.

**Idea:** `Error(w)` is a parabola in `w` (a U-shape). The minimum is at the bottom, where the slope of that U is zero. So we take the derivative, set it to 0, and solve.

```
  d/dw  Σ (w·xᵢ − yᵢ)²  =  2 · Σ xᵢ·(w·xᵢ − yᵢ)  =  0
```

Solving for `w`:

```
        Σ (xᵢ · yᵢ)
  w  =  ─────────────
          Σ (xᵢ²)
```

In matrix / vector notation (with `X` and `Y` as columns of numbers):

```
        Xᵀ Y
  w  =  ─────
        Xᵀ X
```

**Reading the formula:**
- `Xᵀ Y` = multiply each x by its matching y, add them all up.
- `Xᵀ X` = square each x, add them all up.
- Divide. Done. One shot, exact, no iteration.

**In the code** this is the single line:

```python
w = (1.0/np.dot(X_lin.T, X_lin))[0,0] * X_lin.T.dot(Y_lin)[0,0]
```

> **Why doesn't this always work?** The clean formula exists only for simple, linear cases. For anything bigger (many weights, non-linear models, neural networks) it becomes impossible or too expensive to solve directly. That's why we need the next method.

---

## 3. Gradient descent (the general-purpose method)

When there's no formula, we **search** for the best `w` step by step.

Picture `Error(w)` as a valley. You're standing somewhere on the slope in the dark. You can't see the bottom, but you *can* feel which way is downhill. So you take a small step downhill, then feel again, then step again — until the ground is flat (the bottom).

- **"Which way is downhill?"** → the **gradient** (the derivative of the error).
- **"How big a step?"** → the **step size** (also called learning rate).

### The update rule

```
  w_new = w_old − step_size · gradient
```

The minus sign is key: the gradient points *uphill* (toward larger error), so we move the **opposite** way to go down.

### What the gradient is here

We already computed the derivative of the squared error above. For fitting `y ≈ w·f(x)`:

```
  gradient = 2 · Σ f(xᵢ) · ( w·f(xᵢ) − yᵢ )
```

In matrix form (with `F` = the column of `f(x)` values):

```
  gradient = 2 · Fᵀ · ( F·w − Y )
```

So the full step is:

```
  w_new = w_old − step_size · 2 · Fᵀ · ( F·w_old − Y )
```

Repeat this thousands of times and `w` slides down to the bottom of the valley — the **same answer** the exact formula would give, just reached by walking instead of teleporting.

### Reading each piece

| Symbol            | Meaning                                             |
|-------------------|-----------------------------------------------------|
| `F·w`             | current predictions                                 |
| `F·w − Y`         | the errors (how wrong we are right now)             |
| `Fᵀ · (F·w − Y)`  | the gradient — which way to move `w` to shrink error|
| `step_size · …`   | a small, cautious nudge in that direction           |
| `w_new = w − …`   | update the weight and repeat                         |

---

## 4. Basis functions — the real lesson

A **basis function** `f(x)` is just "the shape you decide to fit." You're always fitting `y ≈ w · f(x)`; you get to choose `f`.

- `f(x) = x` → you're fitting a **straight line**. Great for linear data, useless for a curve.
- `f(x) = x²` → you're fitting a **parabola**. Now a curved dataset becomes fittable with the very same math.

This is the punchline of the whole script:

> **Changing the basis function is what lets a "linear" method fit non-linear data.** The math (least squares, gradient descent) stays identical — you just feed it `x²` instead of `x`.

---

## 5. How the three experiments in `task1.py` map to the theory

| Part | Data                 | Method                          | Basis   | Outcome                                  |
|------|----------------------|---------------------------------|---------|------------------------------------------|
| 1    | line & parabola + noise | (just generating data)       | —       | fake but realistic data to test on       |
| 2a   | line (`2x + noise`)  | exact OLS formula               | `x`     | **good** fit, `w ≈ 2`                     |
| 2b   | parabola (`2x² + noise`) | exact OLS formula           | `x`     | **bad** — a straight line can't bend      |
| 3    | parabola (`2x² + noise`) | gradient descent            | `x²`    | **good** fit, `w ≈ 2`                     |

Part 2b is a *deliberate failure*: it shows that a straight line simply cannot fit a curve, no matter how perfectly you compute the slope. Part 3 fixes it by switching the basis to `x²` — and demonstrates gradient descent while doing so.

---

## 6. Practical knobs (worth understanding)

- **Step size (`0.0001` in the code).** Too big → you overshoot the valley and the error *explodes*. Too small → you crawl and never arrive in the allotted steps. Tuning this is a real skill, not a detail.
- **Number of iterations (`10000`).** This is the stopping rule: "walk this many steps, then stop." A smarter rule would stop once `w` stops changing meaningfully.
- **Noise.** The `+ noise` in the data is why `w` lands *near* 2, not exactly 2. Real measurements are never clean, and a good model shouldn't chase the noise.

---

## 7. How many samples do you need?

There is no magic number, but there are three forces that decide it. All three showed up in this homework.

### a) Noise sets the floor: error shrinks like 1/√N

Each data point is `truth + noise`. When you fit, the noise partially cancels out across points — but slowly. The uncertainty in your learned weight shrinks proportionally to **1/√N**:

```
  uncertainty in w  ∝  σ / √N        (σ = how noisy each point is)
```

The √ is the painful part: to make your estimate **10× more precise you need 100× more data**. Consequences:

- Going from 10 → 100 points helps a lot. Going from 10,000 → 20,000 barely matters.
- Noisier data (bigger σ) needs proportionally more samples for the same confidence.
- This is why `w` lands *near* 2 with 100 noisy points, and would land *nearer* with 10,000 — but never exactly on it.

### b) Model size sets a hard minimum: more weights need more points

Every weight is an unknown the data must pin down. With `P` weights and `N` points:

- **N < P** — the system is *underdetermined*: infinitely many weight vectors fit the data **perfectly**, including ones that are pure nonsense between the points. The fit tells you nothing.
- **N ≈ P** — the model can memorize every point, noise included. Perfect training fit, garbage in between. This is **overfitting**.
- **Rule of thumb: N ≥ 10·P** — roughly ten points per weight before you can start trusting the fit.

**This exact trap is in `task2.py`:** the sinusoidal basis with `K = 20` harmonics has **41 weights but only 10 data points**. The curve threads through every point (outlier included!) — not because it found the true function, but because 41 knobs can bend through any 10 points. The comment in the file admits it honestly: *"with such a low amount of data, it is hard to tell whether sinusoidal fits closely to the 'real' function."* That's underdetermination talking.

Compare `task3.py`: the same 41-weight basis, but with **1000 points** (N ≈ 24·P) — now the wiggles are actually constrained by data, and the fit is trustworthy.

### c) Coverage matters, not just count

N points are only useful where they *are*. 1000 points all bunched at small `x` tell you nothing about the function at large `x` — any extrapolation there is faith, not fit. This bites hardest with:

- **skewed sampling** — the exponential `X` in `task1.py` puts most points near 0 and only a few far out, so the fit is well-anchored on the left and increasingly guesswork on the right;
- **local basis functions** — a Gaussian RBF bump with no data near its center gets an arbitrary weight, since no point constrains it.

### Practical checklist

1. Count your weights `P`. Aim for **N ≥ 10·P**; treat N < P as meaningless.
2. Eyeball the noise. Noisier data → more samples (precision only improves as √N).
3. Check coverage: do you have points across the whole range you care about?
4. The honest test isn't "does it fit my points" — it's "does it fit points I *held out*." If you can't afford held-out data, you don't have enough data.

---

## 8. The q-norm loss — making regression robust to outliers

Everything so far used **squared error**. That choice was never questioned — but it's a choice, and it has a weakness: squaring makes big misses *very* expensive. One outlier with a residual of 40 contributes `40² = 1600` to the loss, while ten honest points with residuals of 1 contribute 10 total. The optimizer will happily sell out all ten to appease the one. That's exactly what happens in `task2.py`: the outlier drags the OLS line far above the true one.

### The fix: change the exponent

Squared error is just the **2-norm** of the residual vector. Generalize the exponent and you get the **q-norm loss**:

```
  L(w) = Σ | yᵢ − xᵢ·w |^q          with  1 ≤ q ≤ 2
```

| q     | Name                              | Behavior                                        |
|-------|-----------------------------------|--------------------------------------------------|
| 2     | Ordinary Least Squares            | smooth, closed-form, but outlier-sensitive       |
| 1.1–1.5 | q-norm ("Lq regression")        | compromise: mostly smooth, mostly robust         |
| 1     | Least Absolute Deviations (LAD)   | maximally robust, but not differentiable at 0    |

**Why a smaller q resists outliers.** Look at how much one point's residual `r` contributes to the loss:

```
  q = 2:   |r|²      →  residual 40 costs 1600   (screams)
  q = 1.1: |r|^1.1   →  residual 40 costs ~58    (mutters)
```

Even sharper: the *gradient* is what actually moves `w`, and each point's pull on the gradient scales like `|r|^(q−1)`. At `q = 2` the pull grows **linearly** with the residual — the farther a point is from the line, the harder it yanks. At `q = 1.1` the pull grows like `|r|^0.1`, nearly **flat** — a point 40 away pulls barely harder than a point 2 away. The outlier loses its veto; the majority wins.

### The gradient

Differentiate `L(w)` term by term (chain rule on `|r|^q`, with `r = y − x·w`):

```
  ∇w L  =  −q · Σ xᵢ · |rᵢ|^(q−1) · sign(rᵢ)
```

or in matrix form:

```
  ∇w L  =  −q · Xᵀ ( |r|^(q−1) ⊙ sign(r) )        r = Y − X·w,   ⊙ = element-wise
```

Sanity check: plug in `q = 2` and you get `−2·Xᵀr = 2·Xᵀ(Xw − Y)` — exactly the OLS gradient from §3. The q-norm is a strict generalization.

### No formula this time — gradient descent is mandatory

For `q = 2` the gradient set to zero gives the closed-form OLS solution (§2). For any other `q` the `|r|^(q−1)` factor makes the equation unsolvable by rearranging symbols — so we walk instead, with the same update rule as always:

```
  w_new = w_old − step_size · ∇w L
        = w_old + step_size · q · Xᵀ ( |r|^(q−1) ⊙ sign(r) )
```

**In the code** (`task2.py`, fourth fit):

```python
r = Y_outlier - X_h.dot(w_q)
w_q += step_size*q*X_h.T.dot(np.power(np.abs(r), q-1)*np.sign(r))
```

Note the step size dropped to `0.001`: the q-norm gradient doesn't grow with residual size the way the OLS gradient does, so its scale is different and the knob needs re-tuning (§6 again).

### Why this is the "right" answer to the outlier problem

The sinusoidal and RBF fits in `task2.py` treat the outlier as **signal** and bend the curve through it — spending 41 weights to fit 10 points (§7b). The q-norm fit does the opposite: it keeps the correct **linear** basis and one weight, and changes only what "close to the data" *means*, so the outlier is quietly outvoted. Result: slope ≈ 5, essentially the clean-data OLS answer, without deleting a single point.

> **The general lesson:** the basis function decides *what shape* you fit (§4); the loss function decides *what "fits well" means*. Outliers are a loss-function problem, not a basis problem.

---

## One-sentence summary

**Regression finds the weight `w` that minimizes a loss; you can get `w` from an exact formula when the problem is simple (squared error, linear basis), or by gradient descent when it isn't — the choice of basis function (`x` vs `x²`) decides whether you can fit curved data, and the choice of loss (2-norm vs q-norm) decides whether one outlier can ruin the fit.**
