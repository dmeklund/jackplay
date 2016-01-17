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

    def _update(self, plot_id):
        plt, curve, data_source, timer, minval, maxval = self._plots[plot_id]
        data = data_source()
        minval = min(data.min(), minval)
        maxval = max(data.max(), maxval)
        curve.setData(data_source())
        plt.setYRange(minval, maxval)
        self._plots[plot_id] = plt, curve, data_source, timer, minval, maxval

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
