import numpy as np
import matplotlib.pyplot as plt
import casadi as ca

sig = 10
beta = 8/3
ro = 28
x0 = [1.0, 0.0, 0.0]

x_sym = ca.MX.sym('x', 3)
h_sym = ca.MX.sym('h')
xdot = ca.vertcat(sig*(x_sym[1]-x_sym[0]), x_sym[0]*(ro-x_sym[2])-x_sym[1], x_sym[0]*x_sym[1]-beta*x_sym[2])
f_ca = ca.Function('f', [x_sym], [xdot])
k1 = f_ca(x_sym)
k2 = f_ca(x_sym + h_sym/2 * k1)
k3 = f_ca(x_sym + h_sym/2 * k2)
k4 = f_ca(x_sym + h_sym   * k3)
x_next = x_sym + h_sym/6 * (k1 + 2*k2 + 2*k3 + k4)
F = ca.Function('F', [x_sym, h_sym], [x_next])

def integrate(F_step, x0, h, N):
    x0_arr = np.array(x0, dtype=float)
    F_map  = F_step.mapaccum(N)
    h_seq  = ca.DM.ones(1, N) * h
    X_seq  = F_map(x0_arr, h_seq).full().T
    X      = np.vstack([x0_arr, X_seq])
    t      = h * np.arange(N + 1)
    return t, X

t_ca, X_ca = integrate(F, x0, 0.01, 10000)

x0_pert = [1.0 + 1e-3, 0.0, 0.0]
_, X_pert = integrate(F, x0_pert, 0.01, 10000)

fig = plt.figure(figsize=(12, 6))

ax3d = fig.add_subplot(121, projection='3d')
ax3d.plot(X_ca[:, 0], X_ca[:, 1], X_ca[:, 2], lw=0.4, label=r'$x_0 = [1, 0, 0]$')
ax3d.plot(X_pert[:, 0], X_pert[:, 1], X_pert[:, 2], lw=0.4, alpha=0.6,
          label=r'$x_0 = [1.001, 0, 0]$')
ax3d.set_xlabel(r'$x_1$'); ax3d.set_ylabel(r'$x_2$'); ax3d.set_zlabel(r'$x_3$')
ax3d.set_title('Lorenz attractor')
ax3d.legend(fontsize=8)

ax2d = fig.add_subplot(122)
dist = np.linalg.norm(X_ca - X_pert, axis=1)
ax2d.semilogy(t_ca, dist)
ax2d.set_xlabel('t')
ax2d.set_ylabel(r'$\|x(t) - x_\mathrm{pert}(t)\|$')
ax2d.set_title('Divergence of nearby trajectories (log scale)')
ax2d.grid(True, which='both')

plt.tight_layout()
plt.show()
