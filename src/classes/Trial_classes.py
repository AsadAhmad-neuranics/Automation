import numpy as np


class OpenLoopGain:
    def __init__(self, input_signal, output_signal):
        """
        Automates the A_OL measurement with input and output signals to calculate the gain of the ASIC.

        Parameters
        ----------
        input_signal : array-like
            The input signal waveform.
        output_signal : array-like
            The output signal waveform.
        gain : float
            The gain of the amplifier circuit.
        """
        
        
        self.input_signal = input_signal
        self.output_signal = output_signal
    
    def measure_gain(self):
        """
        Measures the gain of the amplifier circuit by calculating the ratio of output to input signal.

        Returns
        -------
        float
            The calculated gain.
        """
        if len(self.input_signal) != len(self.output_signal):
            raise ValueError("Input and output signals must have the same length.")
        
        # Calculate gain as the ratio of output to input
        gain_array = self.output_signal / self.input_signal
        gain_mean = np.mean(gain_array)
        gain_std = np.std(gain_array)
        gain_typical = gain_mean +0.47 * gain_std # 68th percentile
        gain_min = np.amin(gain_array)
        gain_currently = gain_mean # Update the global gain variable
        print(gain_currently)
        return gain_typical, gain_min

class GainBandwidthProduct(OpenLoopGain):
    def __init__(self, input_signal, output_signal, frequency=[]):
        """
        Extends OpenLoopGain to calculate the Gain-Bandwidth Product (GBP) of the amplifier.

        Parameters
        ----------
        input_signal : array-like
            The input signal waveform.
        output_signal : array-like
            The output signal waveform.
        frequency : array-like, optional
            The frequency of the input signal. If not provided, it will be calculated based on the input signal.
        """
        super().__init__(input_signal, output_signal)
        self.frequency = frequency if frequency else np.linspace(1, 1000, len(input_signal))
