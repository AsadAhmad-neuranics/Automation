import pyvisa
import time

rm = pyvisa.ResourceManager()
ps = rm.open_resource('USB0::0x2A8D::0x1002::MY61005055::0::INSTR')
ps.write_termination = '\n'
ps.timeout = 5000

ps.write('*RST')
ps.write('*CLS')
idn = ps.query('*IDN?')
print('*IDN? = ' + idn.rstrip('\n'))

# Define voltage, current, and dwell lists
list_volts = [0.1, 0.2, 0.5, 0.8, 0.9] # Voltage list
list_currs = [1.2, 1.2, 1.2, 1.2, 1.2] # Current list
list_dwels = [3.0, 1.5, 1.0, 1.5, 3.0] # Dwell list (how long to wait at each step)

results = []

ps.write('OUTPUT ON')

for v, c, dwell in zip(list_volts, list_currs, list_dwels):
    ps.write(f'VOLT {v}', '(@1)')
    ps.write(f'CURR {c}', '(@1)')
    print(f'Set V={v}V, I={c}A, waiting {dwell}s...')
    time.sleep(dwell)
    v_meas = float(ps.query('MEAS:VOLT?,' '(@1)'))
    c_meas = float(ps.query('MEAS:CURR?', '(@1)'))
    print(f'Measured V={v_meas:.4f}V, I={c_meas:.4f}A')
    results.append((v_meas, c_meas))

ps.write('OUTPUT OFF')
ps.close()
rm.close()

# Save data to file
with open('meas_data.txt', 'w') as f:
    for v, c in results:
        f.write(f"{v}, {c}\n")

print('Done')