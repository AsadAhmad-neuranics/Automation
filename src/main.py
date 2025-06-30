# main.py

import numpy as np
import matplotlib.pyplot as plt
import pyvisa
from scpi.instruments import PowerSupply, Oscilloscope, SpectrumAnalyzer

def main():
    rm = pyvisa.ResourceManager(r"C:\Windows\System32\visa64.dll")
    resources = rm.list_resources()
    print("Available resources:", resources) 
  

if __name__ == "__main__":
    main()

