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

## One-sentence summary

**Regression finds the weight `w` that minimizes squared error; you can get `w` from an exact formula when the problem is simple, or by gradient descent when it isn't — and the choice of basis function (`x` vs `x²`) is what decides whether a straight-line method can fit curved data.**
