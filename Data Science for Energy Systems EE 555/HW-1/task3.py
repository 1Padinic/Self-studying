# Function was easily identified as sinus, I decided to do more iterations and smaller step for this one
# to identify more precisely, although didn't change much. As I already implemented multi-sinusoid function in task 2
# I decided to test it here, it does better fit the graph, although is obviously overcomplication

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import copy

data = np.loadtxt("homework_1_data.txt")
X_b = data[:,0].reshape(-1,1)
Y_b = data[:,1].reshape(-1,1)


w_next = np.random.normal(0,1,size=(1,1))
step_size = 0.0001
i = 0
max_iter = 200000
while i < max_iter:
    w_next -= step_size*np.sin(X_b).T.dot(np.sin(X_b).dot(w_next) - Y_b)
    i += 1
w = w_next.item()
print(f"learned weight w = {w:.4f}")

#plot the data and the fitted cos function
x_line = np.linspace(X_b.min(), X_b.max(), 500)
plt.scatter(X_b, Y_b, s=10, alpha=0.5, label="data")
plt.plot(x_line, w*np.sin(x_line), color="red", linewidth=2, label=f"$y = {w:.3f}\\cos(x)$")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.show()

def sinusoid_basis(x, K):                 #basis functions [1, sin(x), cos(x), sin(2x), cos(2x), ...]
    cols = [np.ones_like(x)]
    for k in range(1, K+1):
        cols.append(np.sin(k*x))
        cols.append(np.cos(k*x))
    return np.hstack(cols)

K = 20                     #number of harmonics -> 2K+1 weights
Phi = sinusoid_basis(X_b, K)
w_multi = np.random.normal(0,1,size=(2*K+1,1))
step_size = 0.0005                  #smaller than task2: 1000 points instead of 10, gradient is ~100x larger

i = 0
while i < max_iter:
    w_multi -= step_size*2*Phi.T.dot(Phi.dot(w_multi) - Y_b)
    i += 1

x_line = np.linspace(X_b.min(), X_b.max(), 500).reshape(-1,1)
plt.scatter(X_b, Y_b, s=10, alpha=0.5, label="data")
plt.plot(x_line, sinusoid_basis(x_line, K).dot(w_multi), color="orange", lw=2, label="multi-sinusoidal fit")
plt.title("Regression with multi-sinusoidal basis, weights determined by gradient descent")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.show()