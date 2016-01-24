"""
The JackPlay jack client
"""
from .plotter import QtPlotter
from .components import PeriodogramComponent, SpectrogramComponent, LowPassFilter
from .data import SignalProcessor
from . import components

import jack
import numpy as np

from functools import partial
import threading
import time

max_storage_time_secs = 20


class JackPlay(object):
    """
    Set up a JACK client with inputs and outputs and hook up the desired processing components.
    """
    def __init__(self, client_name):
        self._ax = None
        self._line = None
        self._lastupdate = time.time()
        self._client = jack.Client(client_name)
        self._plotter = QtPlotter()
        self._processor = SignalProcessor(self._client.samplerate, max_storage_time_secs, self._client.blocksize)
        self._processor_modulate = SignalProcessor(self._client.samplerate, max_storage_time_secs, self._client.blocksize)
        self._periodogram = PeriodogramComponent(self._processor, 1, self._client.samplerate)
        # self._filter = LowPassFilter(self._processor, 200, self._client.samplerate)
        self._filter = components.VariableBandPassFilter(self._processor, self._processor_modulate, self._client.samplerate)
        self._initialize()

    def _process(self, frames):
        """
        Process callback when we have new data frames read from JACK. Read the data and pass them along to our
        signal processor(s).
        """
        data_inport = self._client.inports[0] #'input_1']
        modulate_inport = self._client.inports[1] #'input_2']
        outport = self._client.outports[0] #'output_1']
        modulate = modulate_inport.get_array()
        if np.any(modulate):
            print("Got modulate data!")
        self._processor_modulate.register_data(modulate)
        self._processor.register_data(data_inport.get_array())
        outport.get_buffer()[:] = self._filter.filter()

    def _shutdown(self, status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)

    def _initialize(self):
        """
        Set callbacks and add real-time plots.
        """
        self._client.set_process_callback(self._process)
        self._client.set_shutdown_callback(self._shutdown)
        self._client.inports.register("input_1")
        self._client.inports.register("input_2")
        self._client.outports.register("output_1")
        self._plotter.add_plot("raw", "Raw Data", partial(self._processor.get_data, 0.05))
        self._plotter.add_plot("periodogram", "Periodogram", self._periodogram.get_periodogram)
        self._plotter.add_image("spectrogram", "Spectrogram", SpectrogramComponent(self._processor, 10, self._client.samplerate).get_spectrogram)

    def run(self):
        """
        Run the client until the plotting component is closed.
        """
        with self._client:
            capture = self._client.get_ports(is_physical=True, is_output=True)
            for src, dest in zip(capture, self._client.inports):
                self._client.connect(src, dest)
            playback = self._client.get_ports(is_physical=True, is_input=True)
            for src, dest in zip(self._client.outports, playback):
                self._client.connect(src, dest)
            self._plotter.run()


def main():
    JackPlay("jackplay").run()


if __name__ == "__main__":
    main()
