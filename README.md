# SCPI Framework

## Overview
The SCPI Framework is a Python-based library for automating the measurement of analog ASIC parameters using SCPI-compliant lab instruments connected via USB. It provides an object-oriented interface to control power supplies, oscilloscopes, spectrum analyzers, and temperature chambers for tasks such as measuring input offset voltage (`InputOffsetVoltage`), input offset voltage drift (`InputOffsetVoltage_drift`), and input bias current (`InputBiasCurrent`).

## Features
- **USB Instrument Management**: Connect to SCPI instruments over USB using PyVISA.
- **Automated Measurements**: Measure analog ASIC parameters (`V_os`, `V_os_drift`, `I_B`) with statistical analysis.
- **Statistical Definitions**: "Typical" values are calculated as the 68th percentile (mean + 0.47 × std) of the measured distribution.
- **Temperature Chamber Integration**: Automate temperature-dependent measurements.
- **Extensible Architecture**: Easily add new instruments and measurement routines.

## Installation
To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage
1. **Connect Instruments via USB**: Ensure your instruments are connected via USB and note their VISA addresses (e.g., `USB0::0x1234::0x5678::INSTR`).
2. **Configure Measurement Classes**: Instantiate measurement classes (`InputOffsetVoltage`, `InputOffsetVoltage_drift`, `InputBiasCurrent`) with the correct USB addresses if needed.
3. **Run Measurements**: Use the provided methods to automate measurements. Example:

```python
from classes.measurements import InputOffsetVoltage
vos = InputOffsetVoltage(gain=10)
vos.measure(voltages=[0.0, 0.0, 0.0, 0.0, 0.0], 
            currents=[1.2, 1.2, 1.2, 1.2, 1.2], 
            dwells = [3.0, 1.5, 1.0, 1.5, 3.0])
vos.close()
```
4. **Read The Ouput CSV File**: The methods should create a CSV file in the same directory

## Notes
- Replace the USB VISA addresses in the instrument classes if your instruments use different addresses.
- Use `pyvisa.ResourceManager().list_resources()` to discover connected devices.
- The framework uses PyVISA for instrument communication and NumPy for statistical calculations. Any graphs will be created using matplotlib.pyplot.
- "Typical" values are defined as the 68th percentile (mean + 0.47 × std) for normal distributions.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
""I don't know what to put in here, any inputs would be greatly appreciated""