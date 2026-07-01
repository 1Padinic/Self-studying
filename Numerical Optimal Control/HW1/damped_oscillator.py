import numpy as np
from scipy.integrate import solve_ivp
import matplotlib.pyplot as plt
import casadi as ca

def f(t, x):
    x1, x2 = x
    return [x2,                 
            -0.2 * x2 - x1]     
def f1(x):
    x1, x2 = x
    return np.array([x2,                 
            -0.2 * x2 - x1])

def explicit_euler(x,h=0.125):
    return x+h*f1(x)

def rk4(x,h=0.5):
    k1 = f1(x)
    k2 = f1(x + k1*h/2)
    k3 = f1(x + k2*h/2)
    k4 = f1(x + k3*h)
    return x+h/6*(k1+2*k2+2*k3+k4)
x0 = [1.0, 0.0]

Ts = 0.5
t_eval = Ts * np.arange(20)
t_span = (t_eval[0], t_eval[-1])
def integrate_step(step, x0, h, N):
    x = np.array(x0, dtype=float)
    X = np.zeros((N + 1, len(x)))
    X[0] = x
    for i in range(N):
        x = step(x, h)
        X[i+1] = x
    t = h * np.arange(N + 1)
    return t, X

sol = solve_ivp(f, t_span, x0, method='RK45', t_eval=t_eval)
t_ref, x1_ref, x2_ref = sol.t, sol.y[0], sol.y[1]

t_eu, X_eu = integrate_step(explicit_euler, x0, 0.125, 76)
t_rk, X_rk = integrate_step(rk4,            x0, 0.5,   19)

x_sym = ca.MX.sym('x', 2)
h_sym = ca.MX.sym('h')
xdot  = ca.vertcat(x_sym[1], -0.2 * x_sym[1] - x_sym[0])
f_ca  = ca.Function('f', [x_sym], [xdot])

k1 = f_ca(x_sym)
k2 = f_ca(x_sym + h_sym/2 * k1)
k3 = f_ca(x_sym + h_sym/2 * k2)
k4 = f_ca(x_sym + h_sym   * k3)
x_next = x_sym + h_sym/6 * (k1 + 2*k2 + 2*k3 + k4)
F = ca.Function('F', [x_sym, h_sym], [x_next])

def rk4_ca(x, h):
    return F(x, h).full().flatten()

t_ca, X_ca = integrate_step(rk4_ca, x0, 0.5, 19)

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(t_ref, x1_ref, 'o',  color='C0', label=r'solve_ivp $x_1$')
ax.plot(t_ref, x2_ref, 's',  color='C0', label=r'solve_ivp $x_2$', markerfacecolor='none')

ax.plot(t_eu, X_eu[:, 0], '--', color='C1', label=r'Euler $x_1$ (h=0.125)')
ax.plot(t_eu, X_eu[:, 1], ':',  color='C1', label=r'Euler $x_2$ (h=0.125)')

ax.plot(t_rk, X_rk[:, 0], '-',  color='C2', label=r'RK4 numpy $x_1$ (h=0.5)')
ax.plot(t_rk, X_rk[:, 1], '-.', color='C2', label=r'RK4 numpy $x_2$ (h=0.5)')

ax.plot(t_ca, X_ca[:, 0], 'd', color='C3', markersize=5, label=r'RK4 CasADi $x_1$')
ax.plot(t_ca, X_ca[:, 1], 'd', color='C3', markersize=5, markerfacecolor='none',
        label=r'RK4 CasADi $x_2$')

ax.set_xlabel('t  [s]')
ax.set_ylabel('state')
ax.set_title('Damped oscillator: solve_ivp vs. Euler vs. RK4 (numpy & CasADi)')
ax.grid(True)
ax.legend(ncol=4, fontsize=8)
plt.tight_layout()
plt.show()
