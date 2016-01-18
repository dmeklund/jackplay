"""
The JackPlay jack client
"""
from .plotter import QtPlotter
from .components import PeriodogramComponent, SpectrogramComponent, LowPassFilter
from .data import DataProcessor
from . import components

import jack
import numpy as np

from functools import partial
import threading
import time

max_storage_time_secs = 20


class JackPlay(object):
    def __init__(self, client_name):
        # self._fig = None
        self._ax = None
        self._line = None
        self._lastupdate = time.time()
        self._client = jack.Client(client_name)
        self._event = threading.Event()
        self._plotter = QtPlotter()
        self._processor = DataProcessor(self._client.samplerate, max_storage_time_secs, self._client.blocksize)
        self._processor_modulate = DataProcessor(self._client.samplerate, max_storage_time_secs, self._client.blocksize)
        self._periodogram = PeriodogramComponent(self._processor, 1, self._client.samplerate)
        # self._filter = LowPassFilter(self._processor, 200, self._client.samplerate)
        self._filter = components.VariableBandPassFilter(self._processor, self._processor_modulate, self._client.samplerate)
        # self._data = ArrayStream(5)
        # self._lastdata = np.zeros(1024)
        self._initialize()

    def _process(self, frames):
        data_inport = self._client.inports[0] #'input_1']
        modulate_inport = self._client.inports[1] #'input_2']
        outport = self._client.outports[0] #'output_1']
        modulate = modulate_inport.get_array()
        if np.any(modulate):
            print("Got modulate data!")
        self._processor_modulate.register_data(modulate)
        self._processor.register_data(data_inport.get_array())
        outport.get_buffer()[:] = self._filter.filter()
        # for inport, outport in zip(self._client.inports, self._client.outports):
        #     self._processor.register_data(inport.get_array())
        #     # self._lastdata = inport.get_array()
        #     # outport.get_buffer()[:] = inport.get_buffer()
        #     outport.get_buffer()[:] = self._filter.filter(inport.get_array()).tobytes()


    def _shutdown(self, status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)
        self._event.set()

    def _initialize(self):
        self._client.set_process_callback(self._process)
        self._client.set_shutdown_callback(self._shutdown)
        # for number in 1,: #, 2:
        self._client.inports.register("input_1") #.format(number))
        self._client.inports.register("input_2")
        self._client.outports.register("output_1") #.format(number))
        self._plotter.add_plot("raw", "Raw Data", partial(self._processor.get_data, 0.05))
        self._plotter.add_plot("periodogram", "Periodogram", self._periodogram.get_periodogram)
        self._plotter.add_image("spectrogram", "Spectrogram", SpectrogramComponent(self._processor, 10, self._client.samplerate).get_spectrogram)

    def run(self):
        with self._client:
            capture = self._client.get_ports(is_physical=True, is_output=True)
            for src, dest in zip(capture, self._client.inports):
                self._client.connect(src, dest)
            playback = self._client.get_ports(is_physical=True, is_input=True)
            for src, dest in zip(self._client.outports, playback):
                self._client.connect(src, dest)
            self._plotter.run()
            # print("Press Ctrl-C to stop")
            # try:
            #     self._event.wait()
            # except KeyboardInterrupt:
            #     print("\nInterrupted by user")


def main():
    JackPlay("jackplay").run()


if __name__ == "__main__":
    main()
