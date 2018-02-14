import matplotlib.pyplot as plt
import numpy as np

_pow = 2

_frames = 100

data = np.zeros((_frames+1, 1))

colors = ["green", "blue", "red", "purple", "orange", "yellow", "grey"]


fig, ax = plt.subplots()

for _pow in range(2, 9):
    const = 255**(1 /(_pow * 1.0))
    for y in range(_frames + 1):

        data[y] = int((y / (_frames * 1.0) * const)**_pow)
    ax.plot(np.arange(_frames+1), data, lw=2.0, alpha=0.5, color=colors[_pow - 2])
plt.show()
