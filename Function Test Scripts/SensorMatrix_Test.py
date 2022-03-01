"""
   THIS SCRIPT SERVES TO TEST THE VELOSTAT-BASED SENSOR MATRIX, WITH
   A CD4067 MUX ARRAY MINIMIZING THE REQUIRED WIRES AND CONNECTIONS NEEDED.
   THE SCRIPT SETS THE TWO MUXES TO ALLOW ANY SENSOR TO BE READ. AFTER READING
   ALL SENSORS, THE DATA IS CALIBRATED AND TRANSLATED INTO A MORE USEFUL FORM.
   THIS SCRIPT GENERATES AN OUTPUT OF 4 DIRECTIONAL BUTTONS, WITH CERTAIN
   REGIONS SERVING AS UP, RIGHT, DOWN, AND LEFT DIRECTIONS. THERE IS ALSO A
   PUSH BUTTON TO RESET CALIBRATION VALUES IF THE MATRIX IS NOT WORKING
   PROPERLY.
"""

# IMPORT ALL NEEDED LIBRARIES
import board                                              # IMPORTS IMPORTANT DATA FOR THE RP2040
from digitalio import DigitalInOut, Direction, Pull       # IMPORTS ABILITY TO MANIPULATE PICO PINS
import analogio                                           # IMPORTS USAGE OF ANALOG PINS ON PICO
import array                                              # IMPORTS ABILITY TO USE DATA ARRAYS
import time                                               # IMPORTS USAGE OF SYTEM TIME

"""INITIALIZE ALL NEEDED PINS, SETTING PIN DIRECTIONS AND NUMBERS"""
# OBJECTS TO REPRESENT THE OUTPUT MUX SELECTION PINS
# THESE PINS DRIVE SENSOR ROWS HIGH/LOW, PROVIDING 3.3V POWER
muxOutApin = DigitalInOut(board.GP2)
muxOutApin.direction = Direction.OUTPUT
muxOutBpin = DigitalInOut(board.GP3)
muxOutBpin.direction = Direction.OUTPUT
muxOutCpin = DigitalInOut(board.GP4)
muxOutCpin.direction = Direction.OUTPUT
muxOutDpin = DigitalInOut(board.GP5)
muxOutDpin.direction = Direction.OUTPUT
# OBJECTS TO REPRESENT THE INPUT MUX SELECTION PINS
# THESE PINS ENABLE READING OF INDIVIDUAL SENSOR COLUMNS FOR VOLTAGES
muxInApin = DigitalInOut(board.GP6)
muxInApin.direction = Direction.OUTPUT
muxInBpin = DigitalInOut(board.GP7)
muxInBpin.direction = Direction.OUTPUT
muxInCpin = DigitalInOut(board.GP8)
muxInCpin.direction = Direction.OUTPUT
muxInDpin = DigitalInOut(board.GP9)
muxInDpin.direction = Direction.OUTPUT
# OBJECTS TO REPRESENT ADDITIONAL NEEDED PINS
voltageInPin = analogio.AnalogIn(board.GP26)      # pin to respresent analog reading pin for reading sensor voltage
calibResetPin = DigitalInOut(board.GP10)          # pin to represent digital reading pin for calibration reset
calibResetPin.direction = Direction.INPUT
calibResetPin.pull = Pull.UP

"""CONSTANTS ABOUT THE SENSOR MATRIX"""
numOfSensorRows = 12
numOfSensorCols = 8
numOfSensors = 96

"""ALL FUNCTIONS RELATED TO READING AND WRITING FROM GLOBAL DATA ARRAYS"""
# FUNCTIONS FOR ARRAY THAT STORE THE LOW RANGE CALIBRATION DATA
def WriteSensorArray_LowData(row, col, value):
    index = (row * numOfSensorCols) + col
    sensorData_low[index] = value
def ReadSensorArray_LowData(row, col):
    index = (row * numOfSensorCols) + col
    return sensorData_low[index]
# FUNCTIONS FOR ARRAY THAT STORE THE THRESHOLD LEVEL CALIBRATION DATA
def WriteSensorArray_ThresholdData(row, col, value):
    index = (row * numOfSensorCols) + col
    sensorData_threshold[index] = value
def ReadSensorArray_ThresholdData(row, col):
    index = (row * numOfSensorCols) + col
    return sensorData_threshold[index]
# FUNCTIONS FOR ARRAY THAT STORE THE HIGH RANGE CALIBRATION DATA
def WriteSensorArray_HighData(row, col, value):
    index = (row * numOfSensorCols) + col
    sensorData_high[index] = value
def ReadSensorArray_HighData(row, col):
    index = (row * numOfSensorCols) + col
    return sensorData_high[index]
# FUNCTIONS FOR ARRAY THAT STORES THE MOST RECENT VOLTAGE READING
def WriteSensorArray_CurrentData(row, col, value):
    index = (row * numOfSensorCols) + col
    sensorData_current[index] = value
def ReadSensorArray_CurrentData(row, col):
    index = (row * numOfSensorCols) + col
    return sensorData_current[index]
# FUNTIONS FOR ARRAY THAT STORES "PRESS" DETECTIONS
def WriteSensorDetectionArray(row, col, value):
    index = (row * numOfSensorCols) + col
    sensorData_detection[index] = value
def ReadSensorDetectionArray(row, col):
    index = (row * numOfSensorCols) + col
    return sensorData_detection[index]


"""ALL FUNCTIONS RELATED TO PERFORMING ALGORITHMS AND POLLING SENSORS"""
# FUNCTION TO REMAP AN INTEGER OF ONE RANGE INTO ANOTHER RANGE
# ACCEPTS THE VARIABLE, ITS MIN/MAX RANGE, AND THE DESIRED MIN/MAX RANGE
# RETURNS THE RESULT OF CALCULATION
def IntegerMap(x, i_m, i_M, o_m, o_M):
    return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

# COMPLETE FUNCTION TO READ THE VALUE OF A SINGLE SENSOR IN THE SENSOR ARRAY.
# ACCEPTS A ROW AND COLUMN VALUE, AND RETURNS NOTHING. INSTEAD, THIS FUNCTION
# DIRECTLY WRITES TO THE PROGRAM'S SENSOR DATA ARRAY.
# THIS FUNCTION SHOULD TAKE LESS THAN 0ms TO PERFORM!
def CheckOneSensor(row, col):
    # CREATE VARIABLES TO REPRESENT EACH PIN TO SET ON THE OUTPUT MUX.
    # USE FLOOR DIVISION TO CONVERT THE DECIMAL NUMBER TO BINARY, AND STORE
    # THE RESULT IN THE OUTPUT MUX'S A-D PINS
    outputA = row % 2
    tempMath = row // 2
    outputB = tempMath % 2
    tempMath = tempMath // 2
    outputC = tempMath % 2
    tempMath = tempMath // 2
    outputD = tempMath % 2
    # DO THE SAME PROCESS, EXCEPT FOR THE CURRENT COLUMN. RESULTS ARE STORE IN
    # INPUT MUX PINS
    inputA = col % 2
    tempMath = col // 2
    inputB = tempMath % 2
    tempMath = tempMath // 2
    inputC = tempMath % 2
    tempMath = tempMath // 2
    inputD = tempMath % 2
    
    # SET THE PINS ON THE PICO TO THE VARIABLES THAT WERE CALCULATED
    muxOutApin.value = outputA
    muxOutBpin.value = outputB
    muxOutCpin.value = outputC
    muxOutDpin.value = outputD
    muxInApin.value = inputA
    muxInBpin.value = inputB
    muxInCpin.value = inputC
    muxInDpin.value = inputD
    
    # MUX PINS ARE SET: READ THE VOLTAGE FROM A SPECIFIC SENSOR. THEN REMAP THE
    # RESULT INTO A SMALLER RANGE TO SAVE DATA
    rawVoltage = voltageInPin.value
    
    # WRITE DATA TO SENSOR DATA ARRAY
    WriteSensorArray_CurrentData(row, col, rawVoltage)
    
# FUNCTION TO AUTOMATICALLY CHECK ALL SENSORS IN THE SENSOR MATRIX
# ACCEPTS NOTHING, AND RETURNS NOTHING
def CheckAllSensors():
    # ITERATE THROUGH EACH ROW AND COLUMN
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            CheckOneSensor(rowCounter, colCounter)

""" ALL FUNCTIONS RELATED TO PERFORMING CALIBRATIONS FOR THE SYSTEM"""
# FUNCTION TO CALIBRATE THE SENSOR MATRIX, FINDING THE AVERAGE OF THE LOWEST POSSIBLE READINGS
# DIRECTLY WRITES TO LOW VALUE STORAGE ARRAY, AND IS USUALLY PERFORMED AT STARTUP
# ACCEPTS NOTHING, AND RETURNS NOTHING
def CalibrateLow():
    # CREATE CONSTANTS THAT CONTROL THE ACCURACY OF THE SENSOR CALIBRATION
    numOfSamples = 3            # total samples per sensor
    totalCalibrationTime = 3    # total time to wait for entire calibration process
    offsetValue = 5           # amount to shift calibration amount to account for drift/noise
    
    # CALCULATE THE DELAY BETWEEN INDIVIDUAL SAMPLES
    calibrationDelay = (totalCalibrationTime * 1.0) / (numOfSamples * numOfSensors)
    
    # CREATE ARRAY TO STORE AVERAGES, AND FILL WITH ZERO
    averageStorage = array.array('L')
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            averageStorage.append(0)
    
    # START THE PROCESS OF SAMPLING EACH SENSOR A CERTAIN NUMBER OF TIMES.
    # THE SUM OF THEIR SAMPLED VALUES IS STORED IN THE AVERAGE ARRAY
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            for sampleCounter in range(numOfSamples):
                CheckOneSensor(rowCounter, colCounter)
                currentVoltage = ReadSensorArray_CurrentData(rowCounter, colCounter)
                index = (rowCounter * numOfSensorCols) + colCounter
                averageStorage[index] = currentVoltage + averageStorage[index]
                time.sleep(calibrationDelay)
    
    # AFTER SAMPLING EACH SENSOR, FIND THE AVERAGE VALUE BY DIVIDING BY NUMBER OF SAMPLES
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            index = (rowCounter * numOfSensorCols) + colCounter
            averageVal = averageStorage[index] // numOfSamples
            if averageVal < 0 or averageVal > 65535:
                print("error has occured, check math")
                averageVal = 0
            else:
                pass
            WriteSensorArray_LowData(rowCounter, colCounter, (averageVal + offsetValue))

# FUNCTION THAT WILL RECALCULATE WHAT THE THRESHOLD VALUE SHOULD BE FOR A SPECIFIC SENSOR
# ACCEPTS ROW AND COLUMN, AND RETURNS NOTHING
def CalibrateThreshold(row, col):
    # CONSTANTS NEEDED FOR THE FUNCTION
    thresholdPercentage = 0.4      # constant that determines where inbetween high/low the threshold should be
    
    # GET THE REQUIRED INFORMATION FROM ARRAYS
    lowValue = ReadSensorArray_LowData(row, col)
    highValue = ReadSensorArray_HighData(row, col)
    
    # CALCULATE THE THRESHOLD
    newThreshold = int(((highValue - lowValue) * thresholdPercentage) + lowValue)
    
    # STORE THE THRESHOLD INTO ITS ARRAY
    WriteSensorArray_ThresholdData(row, col, newThreshold)

def ResetCalibration(resetBtnStatus):
    # PERFORM RECALIBRATION OF SYSTEM IF CALIBRATION BUTTON IS PRESSED
    if resetBtnStatus == 0:
        print("Recalibrating the system. Please be patient!")
        # TO CLEAR THRESHOLD AND HIGH CALIBRATION, WE NEED TO CLEAR BOTHT THEIR ARRAYS.
        # THE SYSTEM WILL AUTOMATICALLY RESET THEIR VALUES OVER TIME
        for rowCounter in range(numOfSensorRows):
            for colCounter in range(numOfSensorCols):
                WriteSensorArray_ThresholdData(rowCounter, colCounter, 0)
                WriteSensorArray_HighData(rowCounter, colCounter, 0)
                
        # TO CLEAR LOW CALIBRATION, WE NEED TO RECALL THE FUNCTION THAT RUNS AT STARTUP
        CalibrateLow()
        print("System recalibration finished. System ready to use!")
        time.sleep(1.0)
    else:
        pass

""" FUNCTIONS THAT USE COLLECTED SENSOR DATA TO PRODUCE OUTPUTS OR RESULTS"""
# FUNCTION TO COMPARE EACH SENSOR TO ITS THRESHOLD VALUE, AND TRANSLATE THE RESULT INTO A "PRESS"
# FUNCTION WRITES DIRECTLY TO A DATA ARRAY FOR ITS RESULTS
# ACCEPTS NOTHING, AND RETURNS NOTHING
def CheckAllPresses():
    # START BY CHECKING ALL SENSORS FOR CURRENT VALUES
    CheckAllSensors()
    
    # COMPARE THE CURRENT SENSOR VALUE TO ITS PREVIOUS VALUE
    # IF THE DIFFERENCE IN VALUES IS HIGHER THAN A SPECIFIC AMOUNT, TREAT THAT AS A PRESS
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            # GET THE LAST RECORDED VALUE AND THRESHOLD FOR THIS SENSOR
            currentValue = ReadSensorArray_CurrentData(rowCounter, colCounter)
            currentThreshold = ReadSensorArray_ThresholdData(rowCounter, colCounter)
            
            # CHECK IF THE VALUE IS HIGHER THAN THE DESIRED THRESHOLD
            if currentValue > currentThreshold:
                # GET THE HIGH VALUE TO CHECK IF THRESHOLD NEEDS ADJUSTING
                currentHigh = ReadSensorArray_HighData(rowCounter, colCounter)
                
                # IF CURRENT VALUE IS HIGHER THAN RECORDED HIGHEST, UPDATE HIGHEST AND RECALCULATE THRESHOLD
                if currentValue > currentHigh:
                    WriteSensorArray_HighData(rowCounter, colCounter, currentValue)
                    CalibrateThreshold(rowCounter, colCounter)
                else:
                    pass
                
                # WRITE TO THE DETECTION ARRAY THAT A "PRESS" HAS BEEN FOUND
                WriteSensorDetectionArray(rowCounter, colCounter, 1)
            else:
                WriteSensorDetectionArray(rowCounter, colCounter, 0)

# FUNCTION THAT CONVERTS THE PRESS DATA INTO ARROW DATA
# THIS FUNCTION SPECIFICALLY IS FOR DANCE DANCE REVOLUTION, CONTAINING UP, DOWN, LEFT AND RIGHT ARROWS
# ACCEPTS NOTHING, AND RETURNS A PACKED VARIABLE FOR (up, right, down, left, and a placeholder)
def CheckArrowPressesDDR():
    # CREATE TEMP VARIABLES FOR STORAGE
    upPasses = 0            # pass variables check how many times a sensor
    rightPasses = 0         # within a specific region is activated
    downPasses = 0
    leftPasses = 0
    upPress = False         # press booleans are for after logic is performed
    rightPress = False
    downPress = False
    leftPress = False
    
    # CHECK THE DETECTION ARRAY IN A SPECIFIC REGION TO DETERMINE IF AN UP ARROW IS PRESSED
    for rowCounter in range(0, 4):
        for colCounter in range(2, 6):
            if ReadSensorDetectionArray(rowCounter, colCounter) == 1:
                upPasses+=1
            else:
                pass
    # CHECK FOR RIGHT ARROW
    for rowCounter in range(4, 8):
        for colCounter in range(5, 8):
            if ReadSensorDetectionArray(rowCounter, colCounter) == 1:
                rightPasses+=1
            else:
                pass
    # CHECK FOR DOWN ARROW
    for rowCounter in range(8, 12):
        for colCounter in range(2, 6):
            if ReadSensorDetectionArray(rowCounter, colCounter) == 1:
                downPasses+=1
            else:
                pass
    # CHECK FOR LEFT ARROW
    for rowCounter in range(4, 8):
        for colCounter in range(0, 3):
            if ReadSensorDetectionArray(rowCounter, colCounter) == 1:
                leftPasses+=1
            else:
                pass

    # CHECK THE NUMBER OF PRESS OCCURANCES. IF IT IS LARGER THAN THE THRESHOLD, TREAT IT
    # AS A TRUE ARROW PRESS. THESE VALUES CAN BE ADJUSTED TO ENHANCE SENSITIVITY
    upPress = (upPasses > 4)
    rightPress = (rightPasses > 3)
    downPress = (downPasses > 4)
    leftPress = (leftPasses > 3)
    
    # RETURN THE RESULTS OF EACH ARROW PRESS AS PACKED VARIABLE
    return (upPress, rightPress, downPress, leftPress, 0)

""" ALL FUNCTIONS FOR PRINTING OUT DATA TO THE USER THROUGH THE TERMINAL """
# FUNCTION TO PRINT THE "PRESS" ARRAY TO THE USER
def PrintPresses():
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            print(ReadSensorDetectionArray(rowCounter, colCounter), end=" ")
        print("")

# FUNCTION TO PRINT THE DATA FROM THE MOST RECENT SENSOR POLLING
def PrintSensorVals():
    for rowCounter in range(numOfSensorRows):
        for colCounter in range(numOfSensorCols):
            print(ReadSensorArray_CurrentData(rowCounter, colCounter), end=" ")
        print("")

# FUNCTION TO PRINT A DATA COMPARISON BETWEEN THE MOST RECENT SENSOR VALUE AND ITS THRESHOLD
# USEFULL FOR CHECKING IF THE THRESHOLD IS TOO LOW OR TOO HIGH DURING NORMAL USE
def PrintSensorsVsThresholds():
    for rowCounter in range(numOfSensorRows):
        for colCounterCurrent in range(numOfSensorCols):
            print(ReadSensorArray_CurrentData(rowCounter, colCounterCurrent), end=" ")
        print(" | ", end="")
        for colCounterThreshold in range(numOfSensorCols):
            print(ReadSensorArray_ThresholdData(rowCounter, colCounterThreshold), end=" ")
        print("")

""" ALL GLOBAL PYTHON ARRAYS WILL BE DEFINED BELOW"""
# CREATE ALL DATA ARRAYS NEEDED FOR THE PROGRAM. ARRAY TYPE CAN BE SPECIFIED, IN EFFORT
# TO USE MINIMAL MEMORY. THIS USES THE PYTHON ARRAY LIBRARY!
sensorData_low = array.array('I')
for rowCounter in range(numOfSensorRows):
    for colCounter in range(numOfSensorCols):
        sensorData_low.append(0)
sensorData_threshold = array.array('I')
for rowCounter in range(numOfSensorRows):
    for colCounter in range(numOfSensorCols):
        sensorData_threshold.append(0)
sensorData_high = array.array('I')
for rowCounter in range(numOfSensorRows):
    for colCounter in range(numOfSensorCols):
        sensorData_high.append(0)
sensorData_current = array.array('I')
for rowCounter in range(numOfSensorRows):
    for colCounter in range(numOfSensorCols):
        sensorData_current.append(0)
sensorData_detection = array.array('B')
for rowCounter in range(numOfSensorRows):
    for colCounter in range(numOfSensorCols):
        sensorData_detection.append(0)

""" BEGIN THE ACTUAL PROCESS OF THE PROGRAM """
# CALIBRATE THE SENSOR MATRIX BY FINDING THE LOW RANGE OF SENSORS
# PRINT OUT THE RESULT TO VERIFY THE PROCESS WORKED
CalibrateLow()
print(sensorData_low)
time.sleep(3)

# ENTER MAIN LOOP TO REPEAT PROCESSES
while True:
    # GET THE CURRENT SYSTEM TIME
    start = time.monotonic_ns()
    
    # CHECK TO SEE IF A RESET OF CALIBRATION DATA IS DESIRED
    ResetCalibration(calibResetPin.value)
    
    # CHECK TO SEE IF ANY PRESSES HAVE BEEN DETECTED
    CheckAllPresses()
    
    # TRANSLATE PRESSES INTO POSSIBLE ARROW KEYS
    pressesDDR = CheckArrowPressesDDR()
    
    
    # CALCULATE HOW LONG IT TOOK FOR THE PROCESSES TO OCCUR
    ms_duration = (((time.monotonic_ns() - start) + 500000)
               // 1000000)
    
    # PRINT OUT THE RESULTS TO THE USER
    print(pressesDDR)
    
    # SOME OTHER POSSIBLE PRINTS FOR MORE INFORMATION
    #PrintSensorsVsThresholds()
    #PrintSensorVals()
    #PrintPresses()
    
    # PRINT OUT THE TIME IT TOOK TO PERFORM THE PROCESSES
    print("Time it took this loop: ", end="")
    print(ms_duration)
    
    # SLOW DOWN THE PROCESS FOR TERMINAL SANITY
    time.sleep(0.1)
    print("-------------------------------")