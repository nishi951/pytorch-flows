import matplotlib
from matplotlib.widgets import Slider, RangeSlider, Button
import matplotlib.pyplot as plt
import numpy as np

def circle(h, w, r):
    y, x = np.meshgrid(np.linspace(-h/2, h/2, h), np.linspace(-w/2, w/2, w))
    circ = np.sqrt(y**2 + x**2) <= r
    circ = circ.astype(np.float32)
    return circ


def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def circle_stack(n, c, h, w):
    imgs = np.zeros((n, c, h, w))
    for i in range(n):
        t = (i - n/2)/(n/2) # [-1, 1]
        for j in range(c):
            offset = (j - c/2) / c # [-0.5, 0.5]
            r = (h*3/4) * sigmoid(2*t - j)
            imgs[i, j, ...] = circle(h, w, r)
    return imgs

def main():
    matplotlib.use('WebAgg')
    n, c, h, w = 10, 5, 100, 100
    arr = circle_stack(n, c, h, w)

    init_n = 0

    # Make a horizontal slider to control the step
    fig, ax = plt.subplots(nrows=1, ncols=c, figsize=(c*3, 3))
    for j in range(c):
        ax[j].imshow(arr[init_n, j])
        ax[j].set_title(f'channel {j}')

    # Make space for slider
    fig.subplots_adjust(bottom=0.25)

    # Make slider
    axstep = fig.add_axes([0.25, 0.1, 0.5, 0.03])
    n_slider = Slider(
        ax=axstep,
        label='n',
        valmin=0,
        valmax=n-1,
        valstep=1,
        valinit=init_n
    )

    # The function to be called anytime a slider's value changes
    def update(new_n):
        for j in range(c):
            ax[j].imshow(arr[int(new_n), j])
        fig.canvas.draw_idle()

    # register the update function with each slider
    n_slider.on_changed(update)
    plt.show()


if __name__ == '__main__':
    main()
