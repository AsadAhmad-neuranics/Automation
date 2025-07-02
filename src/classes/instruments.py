import numpy as np
import matplotlib.pyplot as plt
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

class SignalGenerator:
    def __init__(self, address, timeout=5000, role='primary'):
        self.rm = pyvisa.ResourceManager()
        self.sg = self.rm.open_resource(address)
        self.sg.write_termination = '\n'
        self.sg.timeout = timeout
        self.connected = True
        self.role = role
        self.sg.write('*RST')
        self.sg.write('*CLS')
        idn = self.sg.query('*IDN?')
        print(f'*IDN? = {idn.rstrip()}')
        # Set reference and trigger sources based on role
        if self.role == 'primary':
            self.sg.write('ROSC:SOUR INT')
            self.sg.write('TRIG:SOUR EXT')
        elif self.role == 'secondary':
            self.sg.write('ROSC:SOUR EXT')
            self.sg.write('TRIG:SOUR EXT')

    def close(self):
        self.sg.close()
        self.rm.close()
        self.connected = False

    def sin(self, frequency=1000, amplitude=1.0, offset=0.0, phase=0.0):
        amplitude = amplitude / 1000
        offset = offset / 1000
        self.sg.write(f'APPL:SIN {frequency},{amplitude},{offset}')
        self.sg.write(f'PHAS {phase}')
       

    def square(self, frequency=1000, amplitude=1.0, offset=0.0, phase=0.0):
        amplitude = amplitude / 1000
        offset = offset / 1000
        self.sg.write(f'APPL:SQU {frequency},{amplitude},{offset}')
        self.sg.write(f'PHAS {phase}')

    def enable_output(self, enable=True):
        self.sg.write('OUTP ON' if enable else 'OUTP OFF')






''''   
class SignalGenerator1:
    def __init__(self, address='USB0::0x0957::0x2707::MY62004362::INSTR', timeout=5000, relation = 'primary'):
        self.rm = pyvisa.ResourceManager()
        self.sg = self.rm.open_resource(address)
        self.relation = relation
        self.sg.write_termination = '\n'
        self.sg.timeout= timeout
        self.connected = True
        self.sg.write('*RST')
        self.sg.write('*CLS')
        idn = self.sg.query('*IDN?')
        print(f'*IDN? = {idn.rstrip()}')
        self.sg.write('ROSC:SOUR EXT')
        self.sg.write('TRIG:SOUR EXT')

    def close(self):
        """
        Closes the connection to the signal generator.
        """
        self.sg.close()
        self.rm.close()
        self.connected = False

    def sin(self, frequency=1000, amplitude=1.0, offset=0.0, duration=5.0, phase=0.0, arm_only=False):
        """
        Generates a sine wave signal for a specified duration.

        Parameters
        ----------
        frequency : float
            Frequency of the sine wave.
        amplitude : float
            Amplitude of the sine wave.
        offset : float
            DC offset of the sine wave.
        duration : float
            Duration in seconds to output the signal.
        """
        amplitude = amplitude / 1000
        offset = offset / 1000
        self.sg.write(f'APPL:SIN {frequency},{amplitude},{offset}')
        self.sg.write(f'PHAS {phase}')
        if not arm_only:
            self.sg.write('OUTP ON')
            time.sleep(duration)
            self.sg.write('OUTP OFF')

    def square(self, frequency=1000, amplitude=1.0, offset=0.0, duration=5.0, phase=0.0, arm_only=False):
        """
        Generates a square wave signal for a specified duration.

        Parameters
        ----------
        frequency : float
            Frequency of the square wave.
        amplitude : float
            Amplitude of the square wave.
        offset : float
            DC offset of the square wave.
        duration : float
            Duration in seconds to output the signal.
        """
        amplitude = amplitude / 1000
        offset = offset / 1000
        self.sg.write(f'APPL:SQU {frequency}, {amplitude}, {offset}')
        self.sg.write(f'PHAS {phase}')
        self.sg.write('OUTP ON')
        time.sleep(duration)
        self.sg.write('OUTP OFF')
        if not arm_only:
            self.sg.write('OUTP ON')
            time.sleep(duration)
            self.sg.write('OUTP OFF')
        
class SignalGenerator2:
    def __init__(self, address='USB0::0x0957::0x2707::MY62004397::0::INSTR', timeout=5000, relation = 'secondary'):
        self.rm = pyvisa.ResourceManager()
        self.sg = self.rm.open_resource(address)
        self.relation = relation
        self.sg.write_termination = '\n'
        self.sg.timeout= timeout
        self.connected = True
        self.sg.write('*RST')
        self.sg.write('*CLS')
        idn = self.sg.query('*IDN?')
        print(f'*IDN? = {idn.rstrip()}')
        self.sg.write('ROSC:SOUR INT')
        self.sg.write('TRIG:SOUR EXT')
        

    def close(self):
        """
        Closes the connection to the signal generator.
        """
        self.sg.close()
        self.rm.close()
        self.connected = False

    def sin(self, frequency=1000, amplitude=1.0, offset=0.0, duration=5.0, phase=0.0, arm_only=False):
        """
        Generates a sine wave signal for a specified duration.

        Parameters
        ----------
        frequency : float
            Frequency of the sine wave.
        amplitude : float
            Amplitude of the sine wave.
        offset : float
            DC offset of the sine wave.
        duration : float
            Duration in seconds to output the signal.
        """
        amplitude=amplitude/1000
        offset=offset/1000
        self.sg.write(f'APPL:SIN {frequency}, {amplitude}, {offset}')
        self.sg.write(f'PHAS {phase}')
        self.sg.write('OUTP ON')
        time.sleep(duration)
        self.sg.write('OUTP OFF')
        if not arm_only:
            self.sg.write('OUTP ON')
            time.sleep(duration)
            self.sg.write('OUTP OFF')

    def square(self, frequency=1000, amplitude=1.0, offset=0.0, duration=5.0, phase=0.0, arm_only=False):
        """
        Generates a square wave signal for a specified duration.

        Parameters
        ----------
        frequency : float
            Frequency of the square wave.
        amplitude : float
            Amplitude of the square wave.
        offset : float
            DC offset of the square wave.
        duration : float
            Duration in seconds to output the signal.
        """
        amplitude = amplitude / 1000
        offset = offset / 1000
        self.sg.write(f'APPL:SQU {frequency}, {amplitude}, {offset}')
        self.sg.write(f'PHAS {phase}')
        self.sg.write('OUTP ON')
        time.sleep(duration)
        self.sg.write('OUTP OFF')
        if not arm_only:
            self.sg.write('OUTP ON')
            time.sleep(duration)
            self.sg.write('OUTP OFF')
'''

''''
class Oscilloscope:
    def __init__(self, address='USB0::0x0000::0x0000::INSTR', timeout=5000):
        self.rm = pyvisa.ResourceManager()
        self.osc = self.rm.open_resource(address)
        self.osc.write_termination = '\n'
        self.osc.timeout = timeout
        self.connected = True
        self.osc.write('*RST')
'''