"""
     THIS SCRIPT ACTS AS A TEST FILE FOR MANY DIFFERENT PROCESSES INVOLVING THE "FRAMEBUFFERS" OF
     THE LEDS AND VARIOUS SPRITES.
     AN IMPORTANT NOTE: WHILE ALL FUNCTIONS REFERENCE ROW/COLUMN, OR X/Y, ALL ARRAYS ARE ONLY 1 DIMENSION!
     THIS ALLOWS US TO USE THE array LIBRARY IN CIRCUITPYTHON, AND FORCE THE ARRAYS TO BE OF A BYTE TYPE TO
     SAVE MEMORY!
     TO READ/WRITE FROM THESE ARRAYS, WE USE A SHORT EQUATION TO CALCULATE ROW/COLUMN POSITIONS IN A SEQUENTIAL
     SET OF DATA IN THE ARRAY. THAT WAY, THE USER ONLY NEEDS TO THINK ABOUT ROWS AND COLUMNS OR X AND Y!

"""


import board                                              # IMPORTS IMPORTANT DATA FOR THE RP2040
import array                                              # IMPORTS ABILITY TO USE DATA ARRAYS
import time                                               # IMPORTS USAGE OF SYTEM TIME
import random                                             # IMPORTS ABILITY TO GENERATE RANDOM NUMBERS
import gc                                                 # IMPORTS ABILITY TO CHECK MEMORY USAGE

# CONSTANTS ABOUT THE LED ARRAY
numOfLEDRows = 16      # NUMBER OF LED ROWS IN THE MATRIX
numOfLEDCols = 16      # NUMBER OF LED COLUMNS IN THE MATRIX
ledMatrixWidth = 15    # MEASUREMENTS IN CENTIMETERS
ledMatrixHeight = 15   # MEASUREMENTS IN CENTIMETERS
horizSpacingLED = 1    # SPACING BETWEEN EACH LED'S MIDDLE HORIZONTALLY, IN CENTIMETERS
vertSpacingLED = 1     # SPACING BETWEEN EACH LED'S MIDDLE HORIZONTALLY, IN CENTIMETERS

# FUNCTION THAT MAPS ONE RANGE OF NUMBERS TO ANOTHER
def IntegerMap(x, i_m, i_M, o_m, o_M):
    return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)

# FUNCTION THAT TRANSLATES AN LED'S ROW/COLUMN TO A PHYSICAL LOCATION IN CENTIMETERS
def RowCol2LEDLocation(row, col):
    ledX = col * horizSpacingLED
    ledY = ((numOfLEDRows - 1) - row) * vertSpacingLED
    return ledX, ledY

# FUNCTIONS TO READ AND WRITE FROM THE GLOBAL FRAMEBUFFER ARRAY
# THIS GLOBAL ARRAY IS CALLED frame_buffer AND IS A BYTE ARRAY
def WriteFrameBufferArray(row, col, value):
    index = (row * numOfLEDCols) + col
    frame_buffer[index] = value
def ReadFrameBufferArray(row, col):
    index = (row * numOfLEDCols) + col
    return frame_buffer[index]
# FUNCTION TO REPLACE ALL FRAME BUFFER DATA WITH 0
def ClearFrameBufferArray():
    for clearRow in range(numOfLEDRows):
        for clearCol in range(numOfLEDCols):
            WriteFrameBufferArray(clearRow, clearCol, 0)
# FUNCTION TO PRINT OUT THE DATA IN THE FRAME BUFFER
def PrintFrameBufferArray():
    for matrixRow in range(numOfLEDRows):
        for matrixCol in range(numOfLEDCols):
            print(ReadFrameBufferArray(matrixRow, matrixCol), end=" ")
        print("")

""" CREATION OF THE MAIN FRAME BUFFER THAT WILL BE USED THROUGH THE SCRIPT"""
frame_buffer = array.array('B')
for rowCounter in range(numOfLEDRows):
    for colCounter in range(numOfLEDCols):
        frame_buffer.append(0)

""" FIRST TEST: CREATE/CALCULATE A CIRCLE ON THE MAIN FRAME BUFFER, THEN APPEND THE RELEVANT DATA TO A NEW SPRITE ARRAY"""
# find the middle of the led matrix, to use as the rootX and rootY
rootX = int(ledMatrixWidth // 2)
rootY = int(ledMatrixHeight // 2)

# lets place a circle of "smallest" size into the frame buffer
# set the radius of the first circle to 6cm, to start
radius = 6
# use math to calculate which LEDs would be powered when drawing a circle
for matrixRow in range(numOfLEDRows):
    for matrixCol in range(numOfLEDCols):
            # convert each LED to a physical location
            ledLocation = RowCol2LEDLocation(matrixRow, matrixCol)
            ledLocationX = ledLocation[0]
            ledLocationY = ledLocation[1]
            # run math equations
            squaredX = (ledLocationX - rootX)**2
            squaredY = (ledLocationY - rootY)**2
            sumXY = squaredX + squaredY
            squaredRadius = radius**2
            # check whether LED should be on or off, then write data to the framebuffer
            if sumXY <= squaredRadius:
                WriteFrameBufferArray(matrixRow, matrixCol, 1)
            else:
                WriteFrameBufferArray(matrixRow, matrixCol, 0)

#print out the frame buffer to see how the data is looking
PrintFrameBufferArray()

# begin process of finding sprite bounds
# scan the frame buffer, and find the top and bottom of the sprite
topFound = False      # flag for finding top of sprite
bottomFound = False   # flag for finding top of sprite
topLocation = 0       # location in frame buffer of top of sprite
bottomLocation = 0    # location in frame buffer of top of sprite
currentRow = 0        # variable used for loop counting

# check all pixels in the frame buffer until conditions are met
while topFound == False or bottomFound == False:
    if topFound == False:
        for currentCol in range(numOfLEDCols):
            if ReadFrameBufferArray(currentRow, currentCol) == 1:
                topFound = True
                topLocation = currentRow
            else:
                pass
    else:
        ledCheck = 0
        for currentCol in range(numOfLEDCols):
            if ReadFrameBufferArray(currentRow, currentCol) == 1:
                ledCheck = 1
            else:
                pass
        # check if any pixels were illuminated on that row: if not, bottom found
        if ledCheck == 0:
            bottomFound = True
            bottomLocation = currentRow
    #increment the row per loop
    currentRow = currentRow + 1

# find the size of the sprite along the y axis
spriteSizeY = bottomLocation - topLocation

# print out information about what was found
print("Top of sprite location: ", end="")
print(topLocation)
print("Bottom of sprite location: ", end="")
print(bottomLocation)
print("Size of the sprite, vertically: ", end="")
print(spriteSizeY)

# repeat the whole process, but scan columns instead of rows
leftFound = False      # flag for finding top of sprite
rightFound = False   # flag for finding top of sprite
leftLocation = 0       # location in frame buffer of top of sprite
rightLocation = 0    # location in frame buffer of top of sprite
currentCol = 0        # variable used for loop counting

while leftFound == False or rightFound == False:
    if leftFound == False:
        for currentRow in range(numOfLEDRows):
            if ReadFrameBufferArray(currentRow, currentCol) == 1:
                leftFound = True
                leftLocation = currentCol
            else:
                pass
    else:
        ledCheck = 0
        for currentRow in range(numOfLEDRows):
            if ReadFrameBufferArray(currentRow, currentCol) == 1:
                ledCheck = 1
            else:
                pass
        # check if any pixels were illuminated on that row: if not, bottom found
        if ledCheck == 0:
            rightFound = True
            rightLocation = currentCol
    #increment the row per loop
    currentCol = currentCol + 1

# find the size of the sprite along the x axis
spriteSizeX = rightLocation - leftLocation
print("Left side of sprite location: ", end="")
print(leftLocation)
print("Right side of sprite location: ", end="")
print(rightLocation)
print(spriteSizeX)

# create the customized sprite array, taking data from a specific area in the frame buffer
# we use the size of the sprite (x, y) to only read what we need, and we use the top and left
# locations to adjust the for loop counters
# we also print out the data going into the array to see what is happening
for spriteRow in range(spriteSizeY):
    for spriteCol in range(spriteSizeX):
        tempVar = ReadFrameBufferArray(spriteRow + topLocation, spriteCol + leftLocation)
        circle_size1.append(tempVar)
        print(tempVar, end=" ")
    print("")

"""
# test the ability to generate and return arrays of different sizes, and store them
# in previously made arrays even though they had no data within them
circle_size2 = array.array('B')
print(circle_size2)

def TestReturningArrays():
    circleBuffer = array.array('B')
    for rowCounter in range(numOfLEDRows):
        for colCounter in range(numOfLEDCols):
            circleBuffer.append(5)
    return circleBuffer

circle_size2 = TestReturningArrays()
print(circle_size2)

# THIS PROCESS WORKS! THIS WILL BE UTILIZED NOW AFTER THIS SECTION
"""

""" SECOND TEST: CREATE FUNCTIONS THAT AUTOMATE THE PROCESS OF USING MATH TO GENERATE A CIRCLE, THEN STORING THAT DATA
    INTO A SMALLER, CUSTOM SPRITE BUFFER. WE START BY CREATING SOME FUNCTIONS
"""

# create a reusable function for prerendering circles of various sizes
# this function encapsulates all the previous work done globally in the script, so it can now be called at any time
# it accepts a radius in CM for the circle
def PreRenderFilledCircle(radius):
    # find the middle of the led matrix, to use as the rootX and rootY
    rootX = int(ledMatrixWidth // 2)
    rootY = int(ledMatrixHeight // 2)

    # lets place a circle of "smallest" size into the frame buffer
    # set the radius of the first circle to 5cm, to start
    for matrixRow in range(numOfLEDRows):
        for matrixCol in range(numOfLEDCols):
                ledLocation = RowCol2LEDLocation(matrixRow, matrixCol)
                ledLocationX = ledLocation[0]
                ledLocationY = ledLocation[1]
                squaredX = (ledLocationX - rootX)**2
                squaredY = (ledLocationY - rootY)**2
                sumXY = squaredX + squaredY
                squaredRadius = radius**2
                
                if sumXY <= squaredRadius:
                    WriteFrameBufferArray(matrixRow, matrixCol, 1)
                else:
                    WriteFrameBufferArray(matrixRow, matrixCol, 0)
    # scan the frame buffer, and find the top and bottom of the sprite
    topFound = False      # flag for finding top of sprite
    bottomFound = False   # flag for finding top of sprite
    topLocation = 0       # location in frame buffer of top of sprite
    bottomLocation = 0    # location in frame buffer of top of sprite
    currentRow = 0        # variable used for loop counting

    # check all pixels in the frame buffer until conditions are met
    while topFound == False or bottomFound == False:
        if topFound == False:
            for currentCol in range(numOfLEDCols):
                if ReadFrameBufferArray(currentRow, currentCol) == 1:
                    topFound = True
                    topLocation = currentRow
                else:
                    pass
        else:
            ledCheck = 0
            for currentCol in range(numOfLEDCols):
                if ReadFrameBufferArray(currentRow, currentCol) == 1:
                    ledCheck = 1
                else:
                    pass
            # check if any pixels were illuminated on that row: if not, bottom found
            if ledCheck == 0:
                bottomFound = True
                bottomLocation = currentRow
        #increment the row per loop
        currentRow = currentRow + 1

    spriteSizeY = bottomLocation - topLocation

    # repeat the whole process, but scan columns instead of rows
    leftFound = False      # flag for finding top of sprite
    rightFound = False   # flag for finding top of sprite
    leftLocation = 0       # location in frame buffer of top of sprite
    rightLocation = 0    # location in frame buffer of top of sprite
    currentCol = 0        # variable used for loop counting

    while leftFound == False or rightFound == False:
        if leftFound == False:
            for currentRow in range(numOfLEDRows):
                if ReadFrameBufferArray(currentRow, currentCol) == 1:
                    leftFound = True
                    leftLocation = currentCol
                else:
                    pass
        else:
            ledCheck = 0
            for currentRow in range(numOfLEDRows):
                if ReadFrameBufferArray(currentRow, currentCol) == 1:
                    ledCheck = 1
                else:
                    pass
            # check if any pixels were illuminated on that row: if not, bottom found
            if ledCheck == 0:
                rightFound = True
                rightLocation = currentCol
        #increment the row per loop
        currentCol = currentCol + 1

    spriteSizeX = rightLocation - leftLocation

    # create the customized sprite array
    sprite_buffer = array.array('B')
    # add on the sprite's x and y size at the beginning
    sprite_buffer.append(spriteSizeX)
    sprite_buffer.append(spriteSizeY)
    # transfer data from framebuffer to array
    for spriteRow in range(spriteSizeY):
        for spriteCol in range(spriteSizeX):
            tempVar = ReadFrameBufferArray(spriteRow + topLocation, spriteCol + leftLocation)
            sprite_buffer.append(tempVar)
    # return the generated sprite data
    return sprite_buffer

# this function will read data from a sprite's framebuffer, based on the row and column requested.
# accepts a "sprite buffer", an X and a Y position
def ReadSpriteBuffer(bufferToRead, posX, posY):
    sizeX = bufferToRead[0]
    index = (posY * sizeX) + posX
    return bufferToRead[index+2]

# this function prints out the data stored within a sprite's framebuffer. This is mainly for the user,
# so we can see if the process of generating the sprite worked correctly
def PrintSprite(bufferToPrint):
    sizeX = bufferToPrint[0]
    sizeY = bufferToPrint[1]
    for spriteRow in range(sizeY):
        for spriteCol in range(sizeX):
            print(ReadSpriteBuffer(bufferToPrint, spriteCol, spriteRow), end=" ")
        print("")

# clean up the Pico's memory, then check how much memory is available before creating sprites
gc.collect()
print(gc.mem_free())

# get the current system time, to also time how long the system took to generate sprites
start = time.monotonic_ns()

# pregenerate 3 cicles of different sizes, then print them all
# create their containers
circle_size00 = array.array('B')
circle_size01 = array.array('B')
circle_size02 = array.array('B')
# generate and store info
circle_size00 = PreRenderFilledCircle(2)
circle_size01 = PreRenderFilledCircle(4)
circle_size02 = PreRenderFilledCircle(6)
# print the circles
PrintSprite(circle_size00)
PrintSprite(circle_size01)
PrintSprite(circle_size02)

# get system time again, then print the time it took in milliseconds
ms_duration = (((time.monotonic_ns() - start) + 500000)
               // 1000000)
print("")
print("------------------------------------------")
print(ms_duration)
# clean the memory and print the new memory usage
gc.collect()
print(gc.mem_free())

""" TEST 3: AFTER GENERATING SPRITES, PUT THEM TO USE BY PLACING THEM BACK ONTO THE FRAME BUFFER IN SPECIFIC LOCATIONS"""
# now we need to figure out how to place the sprites in a specific location.
# because these are circles, it would be easiest for the user to pick the center
# point where the circle will be drawn.
# this means we must do some math, using the sprites' x and y size, to translate
# the user's middle location to the sprite's top-left location.

# function to place a circle onto the global frame buffer
# takes a sprite buffer, and an x and y location
def PlaceSpriteOnFrameBuffer(spriteToPlace, locX, locY):
    # we can make use of the sprite's x/y size stored in the first and second array spots!
    startX = locX - (spriteToPlace[0]//2)
    startY = locY - (spriteToPlace[1]//2)
    
    for spriteRow in range(spriteToPlace[1]):
        for spriteCol in range(spriteToPlace[0]):
            pixelToPlace = ReadSpriteBuffer(spriteToPlace, spriteCol, spriteRow)
            WriteFrameBufferArray(spriteRow + startY, spriteCol + startX, pixelToPlace)

# test some placements, and time the process
print("Time it took to place these three circles onto the framebuffer")
start = time.monotonic_ns()
ClearFrameBufferArray()
PlaceSpriteOnFrameBuffer(circle_size02, 7, 7)
PlaceSpriteOnFrameBuffer(circle_size00, 3, 3)
#\PlaceSpriteOnFrameBuffer(circle_size01, 10, 10)
ms_duration = (((time.monotonic_ns() - start) + 500000)
               // 1000000) #I removed a zero here
print("")
print("------------------------------------------")
print(ms_duration)

#print out the frame buffer to see how the data is looking
PrintFrameBufferArray()