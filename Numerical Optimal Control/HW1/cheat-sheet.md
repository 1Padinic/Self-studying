# NOC HW-1 — Cheat Sheet

## IVP
`ẋ = f(x), x(0) = x₀, t ∈ [0, T]`

Higher-order → state space: `ẋ₁ = x₂, ẋ₂ = …`, with `xᵢ := d^(i-1)q/dt^(i-1)`.

## Explicit integrators
| scheme | update | order |
|---|---|---|
| Euler | `x_{n+1} = x_n + h·f(x_n)` | 1 |
| RK4 | `k1 = f(x); k2 = f(x + h/2·k1); k3 = f(x + h/2·k2); k4 = f(x + h·k3);` `x_{n+1} = x_n + h/6·(k1 + 2k2 + 2k3 + k4)` | 4 |

## Integration loop (numpy)
```python
def integrate(step, x0, h, N):
    x = np.array(x0, dtype=float)
    X = np.zeros((N + 1, len(x))); X[0] = x
    for i in range(N):
        x = step(x, h); X[i+1] = x
    return h * np.arange(N + 1), X
```

## CasADi essentials
```python
import casadi as ca
x    = ca.MX.sym('x', n)             # symbolic vector
expr = ca.vertcat(...)               # build expression
f    = ca.Function('f', [x], [expr]) # wrap as callable
y    = f(x_num).full().flatten()     # evaluate → numpy
J    = ca.jacobian(expr, x)          # exact derivative
```

## RK4 as a CasADi Function
```python
x = ca.MX.sym('x', n); h = ca.MX.sym('h')
f = ca.Function('f', [x], [xdot_expr])
k1 = f(x); k2 = f(x + h/2*k1); k3 = f(x + h/2*k2); k4 = f(x + h*k3)
F = ca.Function('F', [x, h], [x + h/6 * (k1 + 2*k2 + 2*k3 + k4)])
```

## Symbolic rollout: `mapaccum` / `fold` / `map`
```python
F_map = F.mapaccum(N)          # chain F N times, keep all intermediate states
X_seq = F_map(x0, h_seq)       # shape (n, N),  h_seq shape (1, N)
X_end = X_seq[:, -1]

F.fold(N)   # like mapaccum but returns only the final state (cheaper)
F.map(N)    # N INDEPENDENT evaluations (no accumulation) — batching
```

## Full-trajectory sensitivity
```python
S = ca.Function('S', [x0_sym],
                [ca.jacobian(F_map(x0_sym, h_seq)[:, -1], x0_sym)])
S(x0_num)   # exact n×n Jacobian ∂x(T)/∂x0, one line
```

## Picard–Lindelöf, informal
`f` locally Lipschitz in `x` ⇒ IVP has a unique local solution.
- Polynomial dynamics (Lorenz, mass-spring) — locally but not globally Lipschitz.
- `|x|^(1/2)` near 0 — **not** locally Lipschitz → uniqueness can fail.

## Common pitfalls
- Return `np.array([...])` from `f`, not a Python list — otherwise `x + h*f(x)` concatenates instead of adding.
- Missing `*` in Python: `h/6(...)` is a call. Write `h/6 * (...)`.
- Argument order in Lorenz `ẋ₁ = σ(x₂ − x₁)` — sign flip destroys the dynamics.
- `.full()` inside a Python loop breaks CasADi's autodiff chain. Use `mapaccum` when you need derivatives.
- Chaos + long horizon ⇒ Jacobian is exact but only trusted for infinitesimal perturbations.
