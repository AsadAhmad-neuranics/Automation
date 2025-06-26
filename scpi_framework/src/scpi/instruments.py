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
    
class Oscilloscope(Instrument):
    def __init__(self, address, mock=False):
        

        super().__init__(address)
        self.mock = mock

        if not self.mock:
            rm = pyvisa.ResourceManager()
            self._resource = rm.open_resource(address)
        else:
            self._resource = None

    def connect(self):
        if not self.mock:
            if not self._resource:
                rm = pyvisa.ResourceManager()
                self._resource = rm.open_resource(self._address)
        self._isconnected = True
        
    def get_time(self):
        if self.mock:
            return 1.23
        return float(self.device.query("MEAS:TIM:ACQT?"))
    
    def get_voltage(self):
        if self.mock:
            return 3.45
        return float(self.device.query("MEAS:VOLT?"))
    
    def identity(self):
        if self.mock:
            return "Mock Oscilloscope - No hardware connected"
        return self.device.query("*IDN?")
    
    def plot_Waveform(self, time_values, fourier_transform=False, sample_rate = 1e3, mock_voltages=[]):
        
        voltages = []

        for t in time_values:
            if not self.mock:
                self._resource.write(f"TIMEBASE:SCALE {t}")
                voltage = float(self._resource.query("MEAS:VOLT?"))
                voltages.append(voltage)
            else:
                  voltages = mock_voltages
            
        oscfig, ax_osc = plt.subplots()
        ax_osc.plot(time_values, voltages, marker='o', linestyle='-', color='salmon', )
        ax_osc.set_xlabel('Timebase (s)')
        ax_osc.set_ylabel('Voltages (V)')
        ax_osc.set_title('Oscilloscope Waveform')
    
        if fourier_transform:
            frfig, ax_fr = plt.subplots()
            voltages = np.array(voltages)
            N = len(voltages)
            yf = np.fft.fft(voltages)
            xf = np.fft.fftfreq(N, 1/ sample_rate)
            #idx = np.argsort(xf)
            pos_mask = xf >= 0
            
            ax_fr.plot(xf[pos_mask], np.abs(yf[pos_mask]), marker='o', linestyle='-', color='royalblue')
            ax_fr.set_xlabel('Frequency (Hz)')
            ax_fr.set_ylabel('Magnitude')
            ax_fr.set_title('Fourier Transform of Oscilloscope Waveform')
            return [oscfig, frfig]
        
        return oscfig
    
'''


        