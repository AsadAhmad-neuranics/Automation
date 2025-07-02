'''
This code is for Keysight E36313A Power Supply, and does not work for E36311A.
'''





import pyvisa  # VISA wrapper
import time  # time.sleep

rm = pyvisa.ResourceManager()  # resource Manager instance
ps = rm.open_resource('USB0::0x2A8D::0x1002::MY61005055::0::INSTR')  # IO resource instance
ps.write_termination = '\n'  # termination character = <LF>
ps.timeout = 5000            # set timeout 5 seconds

ps.write('*RST')         # reset
ps.write('*CLS')         # clear status
idn = ps.query('*IDN?')  # query bender id, product id, ....
print('*IDN? = ' + idn.rstrip('\n'))  # remove <LF> from response

##########
# output LIST
##########

# List voltage, current, dwell
# 0.1V/1.2A 3.0sec
# 0.2V/1.2A 1.5sec
# 0.5V/1.2A 1.0sec
# 0.8V/1.2A 1.5sec
# 0.9V.1.2A 3.0sec
list_volts = [0.1, 0.2, 0.5, 0.8, 0.9]  # voltage list
list_currs = [1.2, 1.2, 1.2, 1.2, 1.2]  # current list
list_dwels = [3.0, 1.5, 1.0, 1.5, 3.0]  # dwell list
list_bosts = [0,   0,   0,   0,   0]    # begin of step trigger out
list_eosts = [0,   0,   0,   0,   0]    # end of step trigger out

# change list data into SCPI command with comma separated string
slist_volts = ','.join(map(str,list_volts))     # comma separated string
ps.write('LIST:VOLT ' + slist_volts + ',(@1)')  # make SCPI string
slist_currs = ','.join(map(str,list_currs))
ps.write('LIST:CURR ' + slist_currs + ',(@1)')
slist_dwels = ','.join(map(str,list_dwels))
ps.write('LIST:DWEL ' + slist_dwels + ',(@1)')
slist_bosts = ','.join(map(str,list_bosts))
ps.write('LIST:TOUT:BOST ' + slist_bosts + ',(@1)')
slist_eosts = ','.join(map(str,list_eosts))
ps.write('LIST:TOUT:EOST ' + slist_eosts + ',(@1)')

ps.write('VOLT:MODE LIST,(@1)')  # output voltage transient is list
ps.write('CURR:MODE LIST,(@1)')  # output current transient is list
ps.write('TRIG:SOUR BUS,(@1)')   # trigger source is BUS (GPIB)
ps.write('LIST:COUNT 1,(@1)')    # list runs 1 time
ps.write('LIST:STEP AUTO,(@1)')  # list runs dwell pace

##########
# Data log
##########

ps.write('SENS:DLOG:FUNC:VOLT 1,(@1)')  # voltage data log ON
ps.write('SENS:DLOG:FUNC:CURR 1,(@1)')  # current data log ON

dlog_time = sum(list_dwels)  # set data log time to sum of list dwell
ps.write('SENS:DLOG:TIME ' + str(dlog_time))
dlog_per = 0.2               # set data log period to 200msec (Min 200msec)
ps.write('SENS:DLOG:PER ' + str(dlog_per)) 
ps.write('TRIG:DLOG:SOUR BUS')  # set data log trigger source to BUS (GPIB)

##########
# Start list output and data log
##########

ps.write('OUTPUT ON,(@1)')  # output on

ps.write('INIT (@1)')  # initiate list (wait for trigger status)

# !!
# !! USB memory must be connected to E36313A front panel USB port
# !!

ps.write('INIT:DLOG "External:\log1.csv"')  # initiate data log (wait for trigger status)

# confirm both list and data log functions had changed to "wait for trigger" status
#
# Questionable Status SUMMARY Register 
# bit7: WTG_DLOG ==> data log is wait for trigger status
# bit8: WTG ==> list is wait for trigger status
#
mask = 0x80 | 0x100  # mask is OR of bit7 & bit8
for i in range(10):    # repeat 10 times
    time.sleep(0.1)    # wait 100msec
    # get Questionable Status SUMMARY Register
    reg = int(ps.query('STAT:QUES:INST:ISUM1:COND?'))
    print('STAT:QUES:INST:ISUM1:COND? = ' + hex(reg))
    # break this loop if both bit7 and bit8 are 1 
    if (reg & mask) == mask:
        print('LIST and DLOG Waiting trigger detected')
        break
else:  # This For loop had run 10 times loop without break
    #　100msec x 10 times = 1 second. could not detect wait for trigger, then error.
    print('Could not detected waiting trigger')
    ps.write('OUTPUT OFF,(@1)')  # output off
    quit()  # program end

# within 10 times loop, detect wait for trigger, then trigger.
ps.write('*TRG')  # fire BUS trigger

# wait program execution for "data log time plus 1 second". 
print('DLOG time = ',int(dlog_time))
print('Waiting ', end = '', flush = True)
for i in range(int(dlog_time + 1)):   # 1 second margin
    time.sleep(1.0)
    print('.', end='', flush = True)
print()

'''  if abort list and data log
ps.write('ABORT (@1)')   # Abort list
ps.write('ABORT:DLOG')   # Abort data log
'''
ps.write('OUTPUT OFF,(@1)')    # output off

dlog_count = int(dlog_time / dlog_per)  # number of data by data log
# Fetch count = VOLT dlog_count + CURR dlog_count 
ps.write('FETC:DLOG? ' + str(dlog_count * 2) + ',(@1)')  # voltage and current
rdata = ps.read_ascii_values()  # transfer data to PC

err = ''
while( not('No error' in err) ):     # Check error of E36313A
    err = ps.query('SYST:ERR?')
    print('SYST:ERR? = ' + err.rstrip('\n'))

ps.close()    # close E36313A
rm.close()    # close resource manager

# save data to file
with open('meas_data.txt','w') as f:
    for i in range(dlog_count):
        f.write(str(rdata[i]) + ', ' + str(rdata[dlog_count + i]) + '\n')

print('Done')
