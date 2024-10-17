import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

x = np.linspace(0, 10, 100)
y1 = np.sin(x) + 2
y2 = np.sin(x)

colors = ['#ff9999', '#66b3ff']
n_bins = 10
cmap = LinearSegmentedColormap.from_list('custom', colors, N=n_bins)

plt.figure(figsize=(10, 6))
plt.plot(x, y1, color='red', label='Upper')
plt.plot(x, y2, color='blue', label='Lower')

for i in range(n_bins):
    y = y2 + (y1 - y2) * i / n_bins
    plt.fill_between(x, y2, y, color=cmap(i / n_bins), alpha=0.1)

plt.title('Matplotlib Fill Between with Gradient Fill - how2matplotlib.com')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()
