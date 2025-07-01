import numpy as np
import time
from .instruments import Oscilloscope, SpectrumAnalyzer, PowerSupply, TemperatureChamber

initial_temp = 25  # Default temperature for measurements
gain_currently = 1.0 # Default gain for measurements, can be adjusted as needed

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
        
        osc = Oscilloscope()
        
        self.input_signal = osc.input_signal_sin()
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
    def __init__(self, gain=gain_currently):
        self.gain = gain
        self.ps = PowerSupply()
        self.tc = TemperatureChamber()
        self.tc.set_temperature(initial_temp)  # Set initial temperature

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

        with open('data\\input_offset_voltage_data.txt', 'w') as f:
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

class InputOffsetVoltage_drift(InputOffsetVoltage):
    """
    Extends V_os to automate the measurement of input offset voltage drift with temperature using a temperature chamber.

    Methods
    -------
    measure_drift(temp_list, v_in=0.0, channel=1, n_points=1000, sample_rate=1000, settle_time=120):
        For each temperature in temp_list, sets the chamber, measures V_os, and returns the average and maximum drift (dV_os/dT).
    close():
        Closes the power supply, oscilloscope, and temperature chamber connections.
    """
    def __init__(self, gain=gain_currently):
        super().__init__(gain)

    def measure_drift(self, temp_list, v_in=0.0, channel=1, n_points=1000, sample_rate=1000, settle_time=120):
        """
        temp_list: list of temperatures (°C) to measure at
        settle_time: seconds to wait for chamber to stabilize at each temperature
        """
        vtyp_list = []
        vmax_list = []
        actual_temps = []
        for temp in temp_list:
            self.tc.set_temperature(temp)
            print(f"Waiting for chamber to stabilize at {temp} °C...")
            time.sleep(settle_time)
            actual_temp = self.tc.get_temperature()
            vtyp, vmax = self.measure(v_in=v_in, channel=channel, n_points=n_points, sample_rate=sample_rate)
            vtyp_list.append(vtyp)
            vmax_list.append(vmax)
            actual_temps.append(actual_temp)
        # Calculate gradient (dV_typ/dT) at each temperature
        grad_vtyp = np.gradient(vtyp_list, actual_temps)
        mean_grad = np.mean(grad_vtyp)
        std_grad = np.std(grad_vtyp)
        drift_typ = mean_grad + 0.47 * std_grad  # 68th percentile
        drift_max = np.amax(grad_vtyp)

        return drift_typ, drift_max

    def close(self):
        super().close()


class InputBiasCurrent:
    """
    Automates the measurement of input bias current (I_B) for an op-amp by measuring the voltage drop across a high-value resistor in series with the input.

    Parameters
    ----------
    gain : float
        The gain of the amplifier circuit.
    ps_address : str
        VISA address of the power supply.
    osc_address : str
        VISA address of the oscilloscope.
    res : float
        Resistance value in ohms (default: 10000).

    Methods
    -------
    measure_ib(v_in=0.0, channel=1, n_points=1000, sample_rate=1000):
        Sets the input voltage, measures the voltage drop across the resistor, and calculates the input bias current (typical = 84th percentile: mean+std).
    close():
        Closes the power supply and oscilloscope connections.
    """
    def __init__(self, gain=gain_currently, res: float = 10000):
        self.gain = gain
        self.ps = PowerSupply()
        self.osc = Oscilloscope()
        self.tc = TemperatureChamber()
        self.tc.set_temperature(initial_temp)  # Set initial temperature
        self.resistance = res  # Resistance in ohms

    def measure_ib(self, v_in=0.0, channel=1, n_points=1000, sample_rate=1000):
        """
        Measures the input bias current by applying v_in, measuring the voltage drop across the resistor,
        and calculating I_B = V_drop / R.
        """
        self.ps.ps.write(f'VOLT {v_in}')
        self.ps.ps.write('OUTP ON')
        time.sleep(1)  # Wait for stabilization
        timebase, voltages = self.osc.waveform(channel=channel, n_points=n_points, sample_rate=sample_rate)
        mean = np.mean(voltages) / self.gain  # Average voltage drop across resistor
        std = np.std(voltages) / self.gain
        v_typ = mean + 0.47 * std  # 68th percentile
        v_max = np.amax(voltages) / self.gain
        ib_typ = v_typ / self.resistance  # Input bias current in Amps
        ib_max = v_max / self.resistance
        self.ps.ps.write('OUTP OFF')

        return ib_typ, ib_max

    def close(self):
        self.ps.close()
        self.osc.close()
        self.tc.close()

