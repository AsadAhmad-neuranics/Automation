import numpy as np
import time
from .instruments import PowerSupply, SignalGenerator


class InputOffsetVoltage:
    """
    Automates the measurement of input offset voltage (V_os) for an op-amp or ASIC using a programmable power supply and oscilloscope.

    Methods
    -------
    measure(v_in=0.0, channel=1, n_points=1000, sample_rate=1000):
        Sets the input voltage, measures the output waveform, and returns the typical (84th percentile: mean+std) and maximum offset voltages.
    close():
        Closes the power supply and oscilloscope connections.
    """
    def __init__(self, gain):
        self.gain = gain
        self.ps = PowerSupply()


    def measure(self, voltages=[], currents=[], dwells=[]):
        """
        Sets the voltage, current, and dwell time for the power supply.
        
        Parameters
        ----------
        voltages : list
            List of voltages to set.
        currents : list
            List of currents to set.
        dwells : list
            List of dwell times for each voltage/current setting.
        """
        if len(voltages) != len(currents) or len(voltages) != len(dwells):
            raise ValueError("All input lists must have the same length.")
        
        results = []

        self.ps.write('OUTPUT ON', '(@1)')  # Turn on output for channel 1
        
        for v, c, dwell in zip(voltages, currents, dwells):
            self.ps.write(f'VOLT {v}', '(@1)')  # Set voltage for channel 1
            self.ps.write(f'CURR {c}', '(@1)')  # Set current for channel 1
            print(f'Set V={v}V, I={c}A, waiting {dwell}s...')
            time.sleep(dwell)
            v_meas = float(self.ps.query('MEAS:VOLT?', '(@1)'))  # Measure voltage for channel 1
            v_offset = v_meas / self.gain # Calculate V_offset
            c_meas = float(self.ps.query('MEAS:CURR?', '(@1)'))  # Measure current for channel 1
            print(f'Measured V={v_meas:.4f}V, I={c_meas:.4f}A')
            results.append((v_offset, c_meas))

        with open('src\\data\\input_offset_voltage_data.txt', 'w') as f:
            f.write("V_offset, Current\n")
            for v, c in results:
                f.write(f"{v}, {c}\n")

        '''
        mean = np.mean(v_offset)
        std = np.std(v_offset)
        self.V_typical = mean + 0.47 * std  # 68th percentile
        self.V_max = np.amax(v_offset)  # Maximum output voltage
        '''
        
        self.ps.write('OUTPUT OFF')

    def close(self):
        self.ps.close()
        self.osc.close()
        self.tc.close()

class signal_gen:
    def __init__(self):
        self.sg = SignalGenerator()

    def show(self):
        if not self.sg.connected:
            print("Failed to connect to Signal Generator.")
            return
        else:
            while True:
                duration = float(input("Enter duration in seconds (0 to exit): "))
                if duration <= 0:
                    self.sg.close()
                    break
                else:
                    type_ = input("Enter signal type (sin, square): ").strip().lower()
                    frequency = float(input("Enter frequency in Hz: "))
                    amplitude = float(input("Enter amplitude in mV: "))
                    offset = float(input("Enter offset in mV: "))
                    if type_== 'sin':
                        self.sg.sin(frequency=frequency, amplitude=amplitude, offset=offset, duration=duration)
                    elif type_ == 'square':
                        self.sg.square(frequency=frequency, amplitude=amplitude, offset=offset, duration=duration)

class double_gen():
    def __init__(self, addr_primary, addr_secondary):
        self.primary = SignalGenerator(addr_primary, role='primary')
        self.secondary = SignalGenerator(addr_secondary, role='secondary')

    def configure_and_wait(self, type_, frequency, amplitude, offset):
        # Configure both generators with the same waveform, 180° phase difference
        if type_ == 'sin':
            self.primary.sin(frequency=frequency, amplitude=amplitude, offset=offset, phase=0)
            self.secondary.sin(frequency=frequency, amplitude=amplitude, offset=offset, phase=180)
        elif type_ == 'square':
            self.primary.square(frequency=frequency, amplitude=amplitude, offset=offset, phase=0)
            self.secondary.square(frequency=frequency, amplitude=amplitude, offset=offset, phase=180)
        # Arm both outputs (do not start, just enable)
        self.primary.enable_output(True)
        self.secondary.enable_output(True)
        print("Both generators armed. Ready start output.")

    def show(self):
        if not self.primary.connected:
            print("Failed to connect to Signal Generator.")
            return
        else:
            while True:
                duration = float(input("Enter duration in seconds (0 to exit): "))
                if duration <= 0:
                    self.primary.close()
                    self.secondary.close()
                    break
                else:
                    type_ = input("Enter signal type (sin, square): ").strip().lower()
                    frequency = float(input("Enter frequency in Hz: "))
                    amplitude = float(input("Enter amplitude in mV: "))
                    offset = float(input("Enter offset in mV: "))
                    if type_== 'sin':
                        self.primary.sin(frequency=frequency, amplitude=amplitude, offset=offset, duration=duration)
                    elif type_ == 'square':
                        self.primary.square(frequency=frequency, amplitude=amplitude, offset=offset, duration=duration)

    def close(self):
        self.primary.close()
        self.secondary.close()