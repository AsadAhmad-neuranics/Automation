import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import pyvisa
import time


class PowerSupply:
    def __init__(self, address='GPIB0::5::INSTR', timeout=5000):
        self.rm = pyvisa.ResourceManager()
        self.ps = self.rm.open_resource(address)
        self.ps.write_termination = '\n'
        self.ps.timeout = timeout
        self.connected = True
        self.ps.write('*RST')
        self.ps.write('*CLS')
        idn = self.ps.query('*IDN?')
        print(f'*IDN? = {idn.rstrip()}')

    def setup_list(self, voltages, currents, dwells, bosts=None, eosts=None):
        if bosts is None:
            bosts = [0] * len(voltages)
        if eosts is None:
            eosts = [0] * len(voltages)
        self.voltages = voltages
        self.currents = currents
        self.dwells = dwells

        self.ps.write('LIST:VOLT ' + ','.join(map(str, voltages)) + ',(@1)')
        self.ps.write('LIST:CURR ' + ','.join(map(str, currents)) + ',(@1)')
        self.ps.write('LIST:DWEL ' + ','.join(map(str, dwells)) + ',(@1)')
        self.ps.write('LIST:TOUT:BOST ' + ','.join(map(str, bosts)) + ',(@1)')
        self.ps.write('LIST:TOUT:EOST ' + ','.join(map(str, eosts)) + ',(@1)')
        self.ps.write('VOLT:MODE LIST,(@1)')
        self.ps.write('CURR:MODE LIST,(@1)')
        self.ps.write('TRIG:SOUR BUS,(@1)')
        self.ps.write('LIST:COUNT 1,(@1)')
        self.ps.write('LIST:STEP AUTO,(@1)')

    def setup_datalog(self, dlog_per=0.2):
        dlog_time = sum(self.dwells)
        self.dlog_time = dlog_time
        self.dlog_per = dlog_per
        self.ps.write('SENS:DLOG:FUNC:VOLT 1,(@1)')
        self.ps.write('SENS:DLOG:FUNC:CURR 1,(@1)')
        self.ps.write(f'SENS:DLOG:TIME {dlog_time}')
        self.ps.write(f'SENS:DLOG:PER {dlog_per}')
        self.ps.write('TRIG:DLOG:SOUR BUS')

    def run_list_and_log(self, log_filename="External:\\log1.csv", save_to="meas_data.txt"):
        self.ps.write('OUTPUT ON,(@1)')
        self.ps.write('INIT (@1)')
        self.ps.write(f'INIT:DLOG "{log_filename}"')

        # Wait for both list and datalog to be ready for trigger
        mask = 0x80 | 0x100
        for _ in range(10):
            time.sleep(0.1)
            reg = int(self.ps.query('STAT:QUES:INST:ISUM1:COND?'))
            print('STAT:QUES:INST:ISUM1:COND? = ' + hex(reg))
            if (reg & mask) == mask:
                print('LIST and DLOG Waiting trigger detected')
                break
        else:
            print('Could not detect waiting trigger')
            self.ps.write('OUTPUT OFF,(@1)')
            return

        self.ps.write('*TRG')
        print('DLOG time =', int(self.dlog_time))
        print('Waiting ', end='', flush=True)
        for _ in range(int(self.dlog_time + 1)):
            time.sleep(1.0)
            print('.', end='', flush=True)
        print()

        self.ps.write('OUTPUT OFF,(@1)')
        dlog_count = int(self.dlog_time / self.dlog_per)
        self.ps.write(f'FETC:DLOG? {dlog_count * 2},(@1)')
        rdata = self.ps.read_ascii_values()

        # Error checking
        err = ''
        while 'No error' not in err:
            err = self.ps.query('SYST:ERR?')
            print('SYST:ERR? = ' + err.rstrip())

        # Save data
        with open(save_to, 'w') as f:
            for i in range(dlog_count):
                f.write(f"{rdata[i]}, {rdata[dlog_count + i]}\n")
        print('Done')

    def measure_current(self):
        """Measure and return the current output from the power supply (in Amps)."""
        current = float(self.ps.query('MEAS:CURR?'))
        print(f"Measured current: {current} A")
        return current
    
    def turn_on_time(self, threshold=0.95, timeout=5.0, interval=0.01):
        """
        Measure the turn-on time by enabling output and timing until current stabilizes.
        threshold: Fraction of final current to consider as 'on' (e.g., 0.95 for 95%)
        timeout: Maximum time to wait in seconds
        interval: Time between measurements in seconds
        """
        self.ps.write('OUTP ON')
        start_time = time.time()
        currents = []
        while True:
            current = self.measure_current()
            currents.append(current)
            if len(currents) > 5:
                avg = sum(currents[-5:]) / 5
                if avg > 0 and current >= threshold * avg:
                    break
            if time.time() - start_time > timeout:
                print("Timeout waiting for turn-on.")
                break
            time.sleep(interval)
        turn_on_time = time.time() - start_time
        print(f"Turn-on time: {turn_on_time:.3f} s")
        return turn_on_time

    def close(self):
        self.ps.close()
        self.rm.close()
        self.connected = False

class Oscilloscope:
    def __init__(self, address='SPIB0::7::INSTR', timeout=5000, mock=False):
        self.mock=mock
        self.connected = False
        if not self.mock:
            self.rm = pyvisa.ResourceManager()
            self.scope = self.rm.open_resource(address)
            self.scope.write_termination = '\n'
            self.scope.timeout = timeout
            self.connected = True
            idn = self.scope.query('*IDN?')
            print(f'*IDN? = {idn.rstrip()}')
        else:
            self.scope = None
            self.connected = True # For mock mode
    
    def waveform(self, channel=1, n_points=1000, sample_rate=1e3):
        """Aquire waveform data from the oscilloscope or generate mock data."""
        if not self.mock:
            # Example SCPI commands, adjust for specific oscilloscope model
            self.scope.write(f":WAV:SOUR CHAN{channel}")
            self.scope.write(":WAV:MODE NORM")
            self.scope.write(f":WAV:POIN {n_points}")
            raw_data = self.scope.query_binary_values(":WAV:DATA?", datatype='B', container=np.array)
            voltages = raw_data # times some scale factor if needed
            timebase = np.linspace(0, n_points / sample_rate, n_points)
        else:
            # Generate mock signal data (heartbeat-like waveform, magnetic wave)
            timebase = np.linspace(0, n_points / sample_rate, n_points)
            voltages = np.sin(np.random.randint(1,10)*np.pi*np.random.randint(10,100)*timebase) + np.random.randint(0,2)*np.sin(np.random.randint(1,10)*np.pi*np.random.randint(50,200)*timebase) + np.random.randint(0,1)*np.sin(np.random.randint(1,10)*np.pi*np.random.randint(5,100)*timebase)
            voltages += np.random.randint(0,9) * np.random.randn(n_points)/10 # Add some noise
        return timebase, voltages
    
    def plot_waveform(self, timebase, voltages, sample_rate=1e3, peak_height=None):
        """Plot the time-domain waveform and its frequency spectrum"""
        # Plot waveform
        fig1, ax1 = plt.subplots()
        ax1.plot(timebase, voltages, marker='o', linestyle='--', color='salmon')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Voltage (V)')
        ax1.set_title('Oscilloscope Waveform')
        ax1.grid(True)

        # FFT and spectrum plot
        N = len(voltages)
        yf = np.fft.fft(voltages)
        xf = np.fft.fftfreq(N, 1 / sample_rate)
        pos_mask = xf >= 0 # Filter out negative frequencies

        spectrum = np.abs(yf[pos_mask])
        freqs = xf[pos_mask]
        
        if peak_height is None:
            peak_height = 0.1 * np.max(spectrum) # 10% of max by default
        peak_indices, _ = find_peaks(spectrum, height=peak_height)
        peak_freqs = freqs[peak_indices].tolist()

        fig2, ax2 = plt.subplots()
        ax2.plot(xf[pos_mask], np.abs(yf[pos_mask]), marker='o', linestyle='-', color='royalblue')
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Magnitude')
        ax2.set_title('Spectral Analysis (FFT)')
        ax2.grid(True)

        plt.show()
        return peak_freqs, fig1, fig2

    def close(self):
        if not self.mock and self.scope:
            self.scope.close()
            self.rm.close()
        self.connected = False#

class SpectrumAnalyzer:
    def __init__(self, address='GPIB0::10::INSTR', timeout=5000, mock=False):
        self.mock = mock
        self.connected = False
        if not self.mock:
            self.rm = pyvisa.ResourceManager()
            self.sa = self.rm.open_resource(address)
            self.sa.write_termination = '\n'
            self.sa.timeout = timeout
            self.connected = True
            idn = self.sa.query('*IDN?')
            print(f'*IDN? = {idn.rstrip()}')
        else:
            self.sa = None
            self.connected = True

    def configure(self, start_freq=1e3, stop_freq=1e6, rbw=1e3):
        if not self.mock:
            self.sa.write(f'FREQ:START {start_freq}')
            self.sa.write(f'FREQ:STOP {stop_freq}')
            self.sa.write(f'BAND {rbw}')
        else:
            self.start_freq = start_freq
            self.stop_freq = stop_freq
            self.rbw = rbw

    def trace(self, n_points=1001):
        if not self.mock:
            self.sa.write(f'FORM ASC')
            self.sa.write(f'TRAC:MODE WRIT')
            data = self.sa.query_ascii_values(f'TRAC? TRACE1')
            freqs = np.linspace(float(self.sa.query('FREQ:START?')), float(self.sa.query('FREQ:STOP?')), len(data))
            return freqs, np.array(data)
        else:
            freqs = np.linspace(self.start_freq, self.stop_freq, n_points)
            noise = np.random.normal(0, 1, n_points)
            return freqs, noise

    def plot_trace(self, freqs, spectrum):
        plt.figure()
        plt.plot(freqs, spectrum)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Magnitude')
        plt.title('Spectrum Analyzer Trace')
        plt.grid(True)
        plt.show()

    def close(self):
        if not self.mock and self.sa:
            self.sa.close()
            self.rm.close()
        self.connected = False





'''
class Instrument:
    def __init__(self, address):
            
        self._address = address
        self._isconnected = False

    def address(self):
        return self._address
    
    def isconnected(self):
        return self._isconnected

    def connect(self):
        # Code to establish a connection to the SCPI instrument
        self._isconnected = True

    def disconnect(self):
        # Code to disconnect from the SCPI instrument
        self._isconnected = False

    def send_command(self, command):
        if self._isconnected == False:
            raise Exception("Instrument not connected")
        # Code to send a SCPI command to the instrument and return the response
        return f"Command '{command}' sent to {self.__address}"
'''


