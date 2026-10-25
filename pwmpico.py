#library setup
from machine import Pin, PWM, ADC #from pico, import needed vars
from time import ticks_us, ticks_diff #importing time func for later use
from array import array #importing arrays for use

#To-DO for PWM
#3. Fix takereadings function/analog measured output
#4. Func used twice? fix.
#5. Testing examples in a txt file
#6. Updated work plan 

#7. Find the pin that the filter outputs to

#To-Do
#Lab 4
#Lab 5
#pwm
#pb

### MEASURE WAVE
def getfeatures(states: array):
    '''
    (array) -> float, float
    
    Calculates, prints, and returns duty cycle and average voltage.
    
    states is a vector, list or array containing 0/1 readings
    '''

    highs=0 # count the HIGHs/variable set up
    for i in states: # gets all items in states array
        if i==1: highs+=1 # if state is on/high, add to high counter

    duty=(highs/len(states))*100 # calc duty factor (duty is % of time PWM is on )
    avg=3.3*(duty/100)   # calc avg voltage
    print(f"\tMeasured duty factor of {round(duty,2)}%, average of {round(avg,2)}V.")
    return (duty, avg)

def takereadings(wave_type: str):
    '''
    (str) -> array or array, float, float # for type ac and dc
    
    Checks and logs states over a 1-second period.
    
    wave_type should be "ac" or "dc"
    '''
    print("\tTaking readings...",end=" ")
    if wave_type not in ("ac", "dc"):
        raise ValueError('wave_type must be "ac" or "dc".')

    start=ticks_us() # Establish start time to count a second from

    if wave_type=="ac": # if alternating current, ...
        vals=array("B") # use array B
        while ticks_diff(ticks_us(),start) < 1_000_000: # for 1 second period
            vals.append(OUTPIN.value()) # log the state
    else: # if direct current, ...
        vals=array("H") # ADC readings fit in an unsigned 16-bit value
        while ticks_diff(ticks_us(),start) < 1_000_000: # for 1 second period
            vals.append(adc.read_u16())  # log the state

    # Display number of readings and time spent
    nor=len(vals) # number of readings (nor) is number of values taken
    elapsed_ms=ticks_diff(ticks_us(),start)//1000
    print(f"Done\n\tTook {nor} readings over {elapsed_ms}ms.")

    return vals

### EMIT WAVE
OUTPINNUM=0 # IMPORTANT: Numbers correspond to GPx signal labels, NOT physical pins!
OUTPIN=Pin(OUTPINNUM) # initializes pin num as pin
pwm=PWM(OUTPIN, freq=9, duty_u16=32768) # freq: min 9, max 125_000; duty: min 0, max 65536 - returns PWM wave class & sends initial wave
print(f"PWM wave being emitted from pin {OUTPINNUM} at {pwm.freq()}Hz...")

### DIGITAL STUFF
print("\nFirst phase:")
states=takereadings("ac") # take all digital states and check if high (1) or low (0)
dduty, dvol = getfeatures(states)

### ANALOG STUFF
print("\nSecond phase:")

ANINPINNUM=26 # sets analog pin num
ANINPIN=Pin(ANINPINNUM) # GPs 26, 27 and 28 can take analog input; initializes pin num as pin
adc=ADC(ANINPIN) # returns avrg voltage between 0V and 3.3V in size pico can process

anvals=takereadings("dc") # take all analog states

# ADC.read_u16() scales 0-3.3 V to 0-65535. The filtered PWM voltage is
# its average level, so infer duty from the average voltage, not a 0/1 threshold.
adc_average=sum(anvals)/len(anvals)
avol=3.3*adc_average/65535
aduty=(avol/3.3)*100
print(f"\tMeasured analog average of {round(avol,2)}V, equivalent duty factor of {round(aduty,2)}%.")

### Calculate differences
diff_duty = dduty - aduty
diff_vol = dvol - avol

dhighs = 0 # initialize variable for number of digital highs (dhighs)
dlows = 0 # initialize variable for number of digital lows (dlows)
for i in states: # gets all items in states
    if i == 1: # if state is on (1), ...
        dhighs += 1 # add to digital high counter
    if i == 0: # if state is off (0), ...
        dlows += 1 # add to digital low counter

ahighs = 0 # initialize variable for number of analog highs
alows = 0 # initialize variable for number of analog lows
for i in anvals: # classify ADC samples relative to the half-scale voltage
    if i >= 32768:
        ahighs += 1 # add to analog high counter
    else:
        alows += 1 # add to analog low counter

### Print Results

print(f"The difference between the digital and analog duty cycles is {round(diff_duty, 2)}.")
print(f"The difference between the digital and analog voltages is {round(diff_vol, 2)}.")
print(f"There are {dhighs} highs and {dlows} lows in the initial signal.")
print(f"There are {ahighs} analog samples at/above half-scale and {alows} below it.")

### END
pwm.deinit()
print("\nEmission stopped.")