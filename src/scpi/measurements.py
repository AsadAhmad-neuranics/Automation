import numpy as np
import matplotlib.pyplot as plt
import pyvisa
import time
from scipy.signal import find_peaks
from instruments import Oscilloscope, SpectrumAnalyzer, PowerSupply, TemperatureChamber

class V_os:
    """
    Automates the measurement of input offset voltage (V_os) for an op-amp or ASIC using a programmable power supply and oscilloscope.

    Methods
    -------
    measure(v_in=0.0, channel=1, n_points=1000, sample_rate=1000):
        Sets the input voltage, measures the output waveform, and returns the typical (mean) and maximum offset voltages.
    close():
        Closes the power supply and oscilloscope connections.
    """
    def __init__(self, gain, ps_address='GPIB0::5::INSTR', osc_address='SPIB0::7::INSTR', chamber_address='GPIB0::12::INSTR'):
        self.gain = gain
        self.ps = PowerSupply(address=ps_address)
        self.osc = Oscilloscope(address=osc_address)
        self.tc = TemperatureChamber(address=chamber_address)
        self.tc.set_temperature(25)  # Set initial temperature

    def measure(self, v_in=0.0, channel=1, n_points=1000, sample_rate=1000):
        # Set input voltage to v_in
        self.ps.ps.write(f'VOLT {v_in}')
        self.ps.ps.write('OUTP ON')
        time.sleep(1)  # Wait for stabilization
        # Measure output voltage using oscilloscope
        timebase, voltages = self.osc.waveform(channel=channel, n_points=n_points, sample_rate=sample_rate)
        v_offset = voltages / self.gain  # List of V_offset values
        self.ps.ps.write('OUTP OFF')
        self.V_in = v_in
        self.V_typical = np.mean(v_offset)  # Average output voltage
        self.V_max = np.amax(v_offset)  # Maximum output voltage

        return self.V_typical, self.V_max

    def close(self):
        self.ps.close()
        self.osc.close()
        self.tc.close()

class V_os_drift(V_os):
    """
    Extends V_os to automate the measurement of input offset voltage drift with temperature using a temperature chamber.

    Methods
    -------
    measure_drift(temp_list, v_in=0.0, channel=1, n_points=1000, sample_rate=1000, settle_time=120):
        For each temperature in temp_list, sets the chamber, measures V_os, and returns the average and maximum drift (dV_os/dT).
    close():
        Closes the power supply, oscilloscope, and temperature chamber connections.
    """
    def __init__(self, gain, ps_address='GPIB0::5::INSTR', osc_address='SPIB0::7::INSTR', chamber_address='GPIB0::12::INSTR'):
        super().__init__(gain, ps_address, osc_address, chamber_address)

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
            #print(f"T = {actual_temp:.2f} °C, V_typ = {vtyp:.6f} V, V_max = {vmax:.6f} V")
        # Calculate gradient (dV_typ/dT) at each temperature
        grad_vtyp = np.gradient(vtyp_list, actual_temps)
        drift_typ = np.mean(grad_vtyp)
        drift_max = np.amax(grad_vtyp)

        return drift_typ, drift_max

    def close(self):
        super().close()


class I_B:
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
        Sets the input voltage, measures the voltage drop across the resistor, and calculates the input bias current.
    close():
        Closes the power supply and oscilloscope connections.
    """
    def __init__(self, gain, ps_address='GPIB0::5::INSTR', osc_address='SPIB0::7::INSTR', chamber_address='GPIB0::12::INSTR',res: float = 10000, temp=25):
        self.gain = gain
        self.ps = PowerSupply(address=ps_address)
        self.osc = Oscilloscope(address=osc_address)
        self.tc = TemperatureChamber(address=chamber_address)
        self.tc.set_temperature(temp)  # Set initial temperature
        self.temperatre = self.tc.get_temperature()
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
        v_typ = np.mean(voltages) / self.gain  # Average voltage drop across resistor
        v_max = np.amax(voltages) / self.gain
        ib_typ = v_typ / self.resistance  # Input bias current in Amps
        ib_max = v_max / self.resistance
        self.ps.ps.write('OUTP OFF')

        return ib_typ, ib_max

    def close(self):
        self.ps.close()
        self.osc.close()
        self.tc.close()

