from machine import Pin, UART, I2C
from ds1302 import DS1302
from ssd1306 import SSD1306_I2C
import utime

count = 0

button_pin = 4
button = Pin(button_pin, machine.Pin.IN, machine.Pin.PULL_UP)

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)

oldState = 0
startTime = utime.time();
printTime = 60
printTimeInterval = 300
maxCount = 50000

recv=""
recv_buf=""

uart = UART(0,115200) # uart on uart1 with baud of 115200
uart.write('AT+CWMODE=1'+'\r\n')
utime.sleep(2)
# print ("  - Connecting to WiFi...")
# uart.write('AT+CWJAP="'+wifi_ssid+'","'+wifi_password+'"'+'\r\n')
# utime.sleep(15)

print ("  - Setting Connection Mode...")
uart.write('AT+CIPMUX=1'+'\r\n')
utime.sleep(2)
print ("  - Starting Webserver..")
uart.write('AT+CIPSERVER=1,80'+'\r\n') #Start webserver on port 80
utime.sleep(2)
print ("Webserver Ready!")
print("")

clk_pin = 5
dat_pin = 6
rst_pin = 7
ds = DS1302(Pin(clk_pin),Pin(dat_pin),Pin(rst_pin))
#ds.date_time([2024, 7, 20, 6, 22, 26, 45, 0]) # set datetime.

fileName = str(ds.year()) + str(ds.month()) + str(ds.day()) + "_" + str(ds.hour()) + str(ds.minute()) + str(ds.second())
startTimeStr = str(ds.year()) + "-" + str(ds.month()) + "-" + str(ds.day()) + " " + str(ds.hour()) + ":" + str(ds.minute()) + ":" + str(ds.second())
runFile = open("run_" + fileName + ".txt" ,"w")
runFile.write("Start time: " + startTimeStr + "\r\n")
runFile.flush()

def pushData(elapsedTime, count):
        countStr = "<html><head><style>.dashboard {padding: 10px;}.color-box {width: 100%;display: flex;flex-wrap: wrap;justify-content: space-between;}.box {display: flex;height: 120px;flex-direction: column;width: 180px;align-items: center;justify-content: center;border-radius: 10px;margin: 10px 5px;}.box i {font-size: 1.3rem;margin-bottom: 5px;color: #000000;}.skyblue {background-color: rgb(135, 220, 253);}.yellow {background-color: rgb(231, 251, 151);}.purple {background-color: rgb(243, 178, 255);}.red {background-color: rgb(255, 178, 178);}</style></head><body><script>document.body.innerHTML = \"<div class=\\\"dashboard\\\"><div class=\\\"color-box\\\"><table style=\\\"margin-left: auto; margin-right: auto;\\\"><tr><th><div class=\\\"box yellow\\\"><p><i class=\\\"fa-solid fa-comment\\\"></i></p><p> Elapsed Time </p><h3> \\\"" + elapsedTime + "\\\" </h3></div></th></tr><tr><td><div class=\\\"box purple\\\"><p> <i class=\\\"fa-solid fa-thumbs-up\\\"></i> </p><p> <b>Count</b></p><h3> \\\"" + str(count) + "\\\" </h3></div></td></tr><tr><td><div class=\\\"box skyblue\\\"><p> <i class=\\\"fa-solid fa-thumbs-up\\\"></i> </p><p> <b>Start Time</b></p><h3> \\\"" + startTimeStr + "\\\" </h3></div></td></tr></table></div></div>\"</script></body></html>"
        ciplength=str(len(countStr)+2) # calculates byte length of send plus newline
        uart.write('AT+CIPSEND=0,' + ciplength +'\r\n')
        utime.sleep(0.1)
        uart.write(countStr +'\r\n')

pix_res_x = 128
pix_res_y = 32
scl_pin = 27
sda_pin = 26

i2c_dev = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=200000)
oled = SSD1306_I2C(pix_res_x, pix_res_y, i2c_dev)

def display_text(oled, counter, time):
    oled.fill(0)
    oled.text(str(counter), 7, 7)
    oled.text(str(counter), 7, 22)
    #oled.text(time, 7, 22)
    oled.show()

pushData("00:00:00", 0)

while True:
    currentTime = utime.time()
    elapsedSeconds = currentTime - startTime
    elapsedTime = convert(elapsedSeconds)

    if button.value():
        oldState = button.value();

    if not button.value() and button.value() != oldState:
        count = count + 1
        display_text(oled, count, elapsedTime)
        oldState = button.value()
        pushData(elapsedTime, count)
        utime.sleep_ms(50)

    if elapsedSeconds == printTime:
        countStr = elapsedTime + ": " + str(count) + "\n"
        runFile.write(countStr)
        runFile.flush()
        printTime = printTime + printTimeInterval

    if count == maxCount:
        endStr = elapsedTime + ": " + str(count) + "\n"
        runFile.write(endStr)
        runFile.flush()

