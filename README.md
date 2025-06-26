# SCPI Framework

## Overview
The SCPI Framework is a Python-based library designed to facilitate communication with SCPI (Standard Commands for Programmable Instruments) compliant instruments. This framework provides an object-oriented approach to manage instrument connections and execute commands seamlessly.

## Features
- **Instrument Management**: Connect and disconnect from SCPI instruments.
- **Command Execution**: Send SCPI commands and handle responses.
- **Extensible Architecture**: Easily add new instruments and commands.

## Installation
To install the required dependencies, run:

```
pip install -r requirements.txt
```

## Usage
To use the SCPI Framework, you can start by importing the necessary classes from the library. Here is a simple example:

```python
from scpi.instrument import Instrument, PowerSupply

# Create an instance of the Instrument class
instrument = Instrument('GPIB::1::INSTR')

# Connect to the instrument
instrument.connect()

# Send a command
response = instrument.send_command('*IDN?')
print(response)

# Disconnect from the instrument
instrument.disconnect()
```

## Running Tests
To ensure the functionality of the framework, unit tests are provided. You can run the tests using:

```
pytest tests/test_instrument.py
```

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.