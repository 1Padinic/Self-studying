# EE 555 — Data Science for Energy Systems (self-study)

Self-paced work through UW's EE 555 course material. This folder covers **Homework 1: Linear Regression & Gradient Descent**, implemented from scratch in NumPy — no scikit-learn, no autograd.

## Skills demonstrated

- **Linear regression from first principles** — derived and implemented the closed-form OLS solution (`w = (XᵀX)⁻¹XᵀY`) and understood when it exists vs. when iteration is required.
- **Gradient descent** — implemented the update loop by hand, including deriving the gradient of squared loss; tuned step size and iteration count, and understood the failure modes (divergence when the step is too large, and rescaling the step when N grows because the gradient scales with it).
- **Basis functions** — used linear, polynomial, multi-sinusoidal (Fourier-style), and Gaussian RBF bases, showing how a "linear" method fits non-linear data by transforming the features.
- **Statistical judgment**, not just code:
  - *Task 1:* compared Gaussian vs. exponential noise and analyzed how non-Gaussian noise degrades the OLS fit.
  - *Task 2:* showed how a single outlier corrupts OLS; compared removing it vs. modeling around it with flexible bases, and recognized that 41 weights on 10 data points is underdetermined — a perfect fit that can't be trusted.
  - *Task 3:* identified an unknown basis function (sinusoid) from raw data and fit it with gradient descent; verified a more complex model was an overcomplication.
- **NumPy fluency** — vectorized matrix operations throughout; matplotlib for every result.

## Files

| File | Contents |
|---|---|
| `task1.py` | OLS closed-form fit on linear vs. non-linear data; gradient descent with polynomial basis; non-Gaussian noise experiment |
| `task2.py` | Outlier analysis; multi-sinusoidal and Gaussian RBF fits via gradient descent |
| `task3.py` | Basis-function identification on unknown data; single vs. multi-harmonic fits |
| `task1_explained.md` | Study notes written while working: OLS derivation, gradient descent intuition, basis functions, choosing sample size |
| `homework_1.ipynb` | Original course notebook (assignment source) |
