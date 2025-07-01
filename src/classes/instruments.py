import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
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
    
    def input_signal_sin(self, channel=1, n_points=1000, frequency=1000, amplitude=1.0, offset=0.0):
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
        signal = amplitude * np.sin(2 * np.pi * frequency * t + offset)
        self.osc.write('')
        return signal

class TemperatureChamber:
    def __init__(self, address='USB0::0x0000::0x0000::INSTR', timeout=5000, mock=False):
        self.mock = mock
        self.connected = False
        if not self.mock:
            self.rm = pyvisa.ResourceManager()
            self.chamber = self.rm.open_resource(address)
            self.chamber.write_termination = '\n' # type: ignore
            self.chamber.timeout = timeout
            self.connected = True
            idn = self.chamber.query('*IDN?') # type: ignore
            print(f'*IDN? = {idn.rstrip()}')
        else:
            self.chamber = None
            self.connected = True

    def set_temperature(self, temp_c):
        if not self.mock:
            self.chamber.write(f'TEMP {temp_c}') # type: ignore
        else:
            print(f"[MOCK] Set temperature to {temp_c} °C")

    def get_temperature(self):
        if not self.mock:
            temp = float(self.chamber.query('MEAS:TEMP?')) # type: ignore
            print(f"Current temperature: {temp} °C")
            return temp
        else:
            print("[MOCK] Returning mock temperature: 25.0 °C")
            return 25.0

    def start(self):
        if not self.mock:
            self.chamber.write('START') # type: ignore
        else:
            print("[MOCK] Chamber start")

    def stop(self):
        if not self.mock:
            self.chamber.write('STOP') # type: ignore
        else:
            print("[MOCK] Chamber stop")

    def close(self):
        if not self.mock and self.chamber:
            self.chamber.close()
            self.rm.close()
        self.connected = False