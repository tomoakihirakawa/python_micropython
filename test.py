import matplotlib.pyplot as plt
import numpy as np
import time

fig = plt.figure()
ax = fig.add_subplot(111)

# some X and Y data
x = [0]
y = [0]

li, = ax.plot(x, y, 'o')

# draw and show it
fig.canvas.draw()
plt.show(block=False)

# loop to update the data
for i in range(100):
    try:
        x.append(i)
        y.append(i)

        # set the new data
        li.set_xdata(x)
        li.set_ydata(y)
        ax.relim()
        ax.autoscale_view(True, True, True)
        fig.canvas.draw()
        plt.pause(0.0001)
        time.sleep(0.01)
    except KeyboardInterrupt:
        plt.close('all')
        break
