# SCPI Framework

## Overview
The SCPI Framework is a Python-based library for automating the measurement of analog ASIC parameters using SCPI-compliant lab instruments connected via USB. It provides an object-oriented interface to control power supplies, oscilloscopes, spectrum analyzers, and temperature chambers for tasks such as measuring input offset voltage (`V_os`), input offset voltage drift (`V_os_drift`), and input bias current (`I_B`).

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
2. **Configure Measurement Classes**: Instantiate measurement classes (`V_os`, `V_os_drift`, `I_B`) with the correct USB addresses if needed.
3. **Run Measurements**: Use the provided methods to automate measurements. Example:

```python
from classes.measurements import V_os
vos = V_os(gain=10)
typical, maximum = vos.measure(v_in=0.0)
print(f"V_os typical (68th percentile): {typical}")
vos.close()
```

## Notes
- Replace the USB VISA addresses in the instrument classes if your instruments use different addresses.
- Use `pyvisa.ResourceManager().list_resources()` to discover connected devices.
- The framework uses PyVISA for instrument communication and NumPy for statistical calculations.
- "Typical" values are defined as the 68th percentile (mean + 0.47 × std) for normal distributions.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.