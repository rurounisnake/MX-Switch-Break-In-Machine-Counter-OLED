from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import utime

count = 0

button_pin = 4
reset_pin = 2

button = Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)
reset = Pin(reset_pin, machine.Pin.IN, machine.Pin.PULL_UP)

pix_res_x = 128
pix_res_y = 32
scl_pin = 11
sda_pin = 10

i2c_dev = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=200000)
oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)

def display_text(oled, counter, time):
    oled.fill(0)
    oled.text(str(counter), 7, 22)
    #oled.text(time, 7, 22)
    oled.show()

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

oldState = 0
startTime = utime.time();
printTime = 0
printTimeInterval = 300
maxCount = 50000

fileNameCountFileRead = open("filename.txt","r")
fileNameCount = fileNameCountFileRead.read()
fileNameCountFileRead.close()

runFile = open("run" + fileNameCount + ".txt" ,"w")
fileNameCountInt = int(fileNameCount) + 1

fileNameCountFileWrite = open("filename.txt","w")
fileNameCountFileWrite.write(str(fileNameCountInt))
fileNameCountFileWrite.close()

while True:
    currentTime = utime.time()
    elapsedSeconds = currentTime - startTime
    elapsedTime = convert(elapsedSeconds)

    if button.value():
        oldState = button.value();

    if not button.value() and button.value() != oldState:
        count = count + 1
        display_text(oled, count, elapsedTime)
        oldState = button.value();
        utime.sleep_ms(230)

    if elapsedSeconds == printTime:
        countStr = elapsedTime + ": " + str(count) + "\n"
        runFile.write(countStr)
        runFile.flush()
        printTime = printTime + printTimeInterval
        print(printTime)

    if count == maxCount:
        endStr = elapsedTime + ": " + str(count) + "\n"
        runFile.write(endStr)
        runFile.flush()

    if not reset.value():
        count = 0

    display_text(oled, count, elapsedTime)

