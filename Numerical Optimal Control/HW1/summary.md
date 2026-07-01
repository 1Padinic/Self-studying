# HW-1 — What I learned

## Concepts
- **IVP:** `ẋ = f(x)`, `x(0) = x₀`. Any n-th order ODE gets rewritten in **state-space form** by defining derivatives as new state components.
- **Picard–Lindelöf:** `f` locally Lipschitz in `x` ⇒ existence and uniqueness of a local solution. Polynomial dynamics (Lorenz, mass-spring) are locally but not globally Lipschitz — still enough.

## Integrators compared
- **`solve_ivp` / `ode45`** — Dormand–Prince RK4(5) with adaptive step. Reference-quality.
- **Explicit Euler** — 1st order. Visible drift at `h = 0.125` even on a mild oscillator.
- **RK4** — 4th order. At `h = 0.5` already sits on top of the reference for smooth problems.

## CasADi
- Symbolic framework: `MX.sym` → expression → `ca.Function` → numeric eval **and** exact derivatives via `ca.jacobian`.
- Two different derivatives to keep straight:
  1. `f(x)` — the ODE RHS. Known analytically.
  2. `∂x(T)/∂x₀` — sensitivity of the trajectory endpoint to its input. Only produced by autodiff through the whole integrator.

## Python loop vs CasADi rollout
- Python `for` loop over `F(x, h).full()` breaks the symbolic chain at every step ⇒ **cannot autodiff through it**.
- `F.mapaccum(N)` chains `F` N times as one symbolic Function ⇒ differentiable end-to-end, and faster (no per-step Python overhead).
- Every downstream NOC method (multiple shooting, collocation, MPC) relies on this.

## Lorenz / chaos
- Sensitive dependence on initial conditions: `‖x(t) − x_pert(t)‖ ~ e^{λt}` (butterfly effect, λ ≈ 0.9).
- Chaos makes long-horizon sensitivities numerically meaningless — the Jacobian norm grows exponentially. Only differentiate on short horizons or use shooting/collocation.

## Note
`lipschitz_checker.py` (numeric + SymPy classifier for problem 1(a)) was written by Claude and **has not been fully verified**. Cross-check its verdicts against the answer key before trusting them.
