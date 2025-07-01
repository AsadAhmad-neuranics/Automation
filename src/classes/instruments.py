import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time

class PowerSupply:
    def __init__(self, address= 'USB0::0x2A8D::0x1002::MY61005055::0::INSTR', timeout= 5000):
        self.rm = pyvisa.ResourceManager()
        self.ps = self.rm.open_resource(address)
        self.ps.write_termination = '\n'
        self.ps.timeout = timeout
        self.connected = True
        self.ps.write('*RST')
        self.ps.write('*CLS')
        idn = self.ps.query('*IDN?')
        print(f'*IDN? = {idn.rstrip()}')
    
    def close(self) -> None:
        self.ps.close()
        self.rm.close()
        self.connected = False

class Oscilloscope:
    def __init__(self, address='USB0::0x0000::0x0000::INSTR', timeout=5000):
        self.rm = pyvisa.ResourceManager()
        self.osc = self.rm.open_resource(address)
        self.osc.write_termination = '\n'
        self.osc.timeout = timeout
        self.connected = True
        self.osc.write('*RST')
    
    def input_signal_sin(self, channel=1, n_points=1000, frequency=1000, amplitude=1.0, phase=0.0):
        """
        Generates a sine wave input signal.
        
        Parameters
        ----------
        channel : int
            The oscilloscope channel to use.
        n_points : int
            Number of points in the signal.
        frequency : float
            Frequency of the sine wave.
        amplitude : float
            Amplitude of the sine wave.
        offset : float
            Offset to apply to the sine wave.
        
        Returns
        -------
        np.ndarray
            The generated sine wave signal.
        """
        t = np.linspace(0, 1, n_points)
        omega = 2 * np.pi * frequency
        signal = amplitude * np.sin(omega * t + phase)
        self.osc.write('')
        return signal

