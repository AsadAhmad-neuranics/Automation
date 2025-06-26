# main.py

import numpy as np
import matplotlib.pyplot as plt
import time
import pyvisa
from scpi.instruments import PowerSupply, Oscilloscope, SpectrumAnalyzer

def main():

    
    ps = PowerSupply()
    
    # Measure quiescent current
    ps.ps.write('VOLT 3.3')
    ps.ps.write('OUTP ON')
    time.sleep(1) 
    quiescent_current = ps.measure_current()
    ps.ps.write('OUTP OFF')
    print(f"Quiescent current: {quiescent_current} A")

    # Set up power supply for a list of voltage/current pairs
    ps.setup_list(
        voltages=[0.1, 0.2, 0.5, 0.8, 0.9],
        currents=[1.2, 1.2, 1.2, 1.2, 1.2],
        dwells=[3.0, 1.5, 1.0, 1.5, 3.0]
    )
    ps.setup_datalog(dlog_per=0.2)
    ps.run_list_and_log()
    ps.close()
    
    
    osc = Oscilloscope(mock=True)
    timebase, voltages = osc.waveform(n_points=1000, sample_rate=1000)
    peak_freqs, fig1, fig2 = osc.plot_waveform(timebase, voltages, sample_rate=1000)
    for i in range(len(peak_freqs)):
        print(f"Peak Frequency {i+1}: {peak_freqs[i]} Hz")
    osc.close()


if __name__ == "__main__":
    main()