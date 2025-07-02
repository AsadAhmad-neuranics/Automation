# main.py

import numpy as np
import matplotlib.pyplot as plt
import pyvisa
from classes.instruments import PowerSupply, SignalGenerator
from classes.measurements import InputOffsetVoltage, signal_gen, double_gen

generator1_address = 'USB0::0x0957::0x2707::MY62004362::INSTR' #secondary generator
generator2_address = 'USB0::0x0957::0x2707::MY62004397::0::INSTR' #primary generator


def main():
    # Initialize VISA resource manager
    rm = pyvisa.ResourceManager()
    resources = rm.list_resources()
    print("Available resources:", resources)
    
# In your main code
gen = double_gen(addr_primary=generator1_address,
                 addr_secondary=generator2_address)
gen.configure_and_wait(type_='sin', frequency=1000, amplitude=50, offset=0)
gen.show_double()
gen.close()


    
    

if __name__ == "__main__":
    main()


