from functools import partial

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg


class QtPlotter(object):
    def __init__(self):
        self._app = QtGui.QApplication([])
        self._win = pg.GraphicsWindow(title="JackPlay Plotter")
        self._win.setWindowTitle("JackPlay Plotter")
        self._plots = dict()
        self._images = dict()

        pg.setConfigOptions(antialias=True)

    def add_plot(self, plot_id, plot_title, data_source):
        plt = self._win.addPlot(title=plot_title)
        curve = plt.plot(pen='y')
        first_data = data_source()
        curve.setData(first_data)

        plt.enableAutoRange('y', False)
        minval, maxval = first_data.min(), first_data.max()
        plt.setYRange(minval, maxval)

        timer = QtCore.QTimer()
        timer.timeout.connect(partial(self._update, plot_id))
        timer.start(50)

        self._plots[plot_id] = (plt, curve, data_source, timer, minval, maxval)

    def add_image(self, image_id, image_title, data_source):
        view = pg.ViewBox()
        self._win.addItem(view)
        img = pg.ImageItem(np.random.rand(10,10))
        # simple colormap

        # stops=np.r_[-1.0,-0.5,0.5,1.0]
        # colors=np.array([[0,0,1,0.7],[0,1,0,0.2],[0,0,0,0.8],[1,0,0,1.0]])
        # cm = pg.ColorMap(stops,colors)
        # pos = np.array([0., 1., 0.5, 0.25, 0.75])
        # color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
        # cmap = pg.ColorMap(pos, color)
        # lut = cm.getLookupTable(0.0, 1.0, 256)
        # img.setLookupTable(lut)
        view.addItem(img)
        timer = QtCore.QTimer()
        timer.timeout.connect(partial(self._update_image, image_id))
        timer.start(50)
        self._images[image_id] = (img, data_source, timer,)

    def _update(self, plot_id):
        plt, curve, data_source, timer, minval, maxval = self._plots[plot_id]
        data = data_source()
        minval = min(data.min(), minval)
        maxval = max(data.max(), maxval)
        curve.setData(data_source())
        plt.setYRange(minval, maxval)
        self._plots[plot_id] = plt, curve, data_source, timer, minval, maxval

    def _update_image(self, image_id):
        img, data_source, timer = self._images[image_id]
        data = data_source()
        img.setImage(data)

    def run(self):
        QtGui.QApplication.instance().exec_()


def update():
    print("other update called")

def test_data_source():
    return np.random.normal(size=1000)


def main():
    plotter = QtPlotter()
    plotter.add_plot("default", "Test Plot", test_data_source)
    QtGui.QApplication.instance().exec_()


if __name__ == '__main__':
    main()
