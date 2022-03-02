from machine import Pin, UART, Timer, I2C, SPI
import time
import sys

import adafruit_gps
import adxl34x
import l3gd20
import sdcard
import uos


GPS = True
ACC = True
GYR = True

if GPS:
    gps_uart = UART(1, baudrate=9600, tx=Pin(8), rx=Pin(9))
    gps = adafruit_gps.GPS(gps_uart, debug=False)
    gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")      #Only GMA & RMC messages
    gps.send_command(b"PMTK220,100")

if ACC:
    i2c_acc = I2C(0, scl=Pin(5), sda=Pin(4), freq=400_000)
    accelerometer = adxl34x.ADXL345(i2c_acc)
    accelerometer.data_rate = adxl34x.DataRate.RATE_3200_HZ

if GYR:
    i2c_gyro = I2C(1, scl=Pin(3), sda=Pin(2), freq=400_000)
    gyro = l3gd20.L3GD20_I2C(i2c_gyro, rate = l3gd20.L3DS20_RATE_800HZ)

sd_cs = Pin(15, Pin.OUT)
spi = SPI(1,
          baudrate=1000000,
          polarity=0,
          phase=0,
          bits=8,
          firstbit=SPI.MSB,
          sck=Pin(10),
          mosi=Pin(11),
          miso=Pin(12))
sd = sdcard.SDCard(spi, sd_cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/")

# Create a file and write something to it
file = open("/test01.csv", "w")
file.write("Gyro_x, Gyro_y, Gyro_z, Acc_x, Acc_y, Acc_z\r\n")

led = Pin(25, Pin.OUT)
counter =0

def main():

    gps_timer = Timer(period=100, mode=Timer.PERIODIC, callback=gps_update)
    gyro_acc_timer = Timer(period=10, mode=Timer.PERIODIC, callback=fast_update)
    time.sleep(10)
    gyro_acc_timer.deinit()
    gps_timer.deinit()
    time.sleep(1)
    file.close()
    print(counter)
    #sys.exit()
    while True:
        led.on()
        time.sleep(.25)
        led.off()
    #    time.sleep(.75)



def gps_update(t):
    GPS = True
    g = gyro.gyro
    #gps.update()
    #if gps.has_fix:
    #    parse_GPS()
    #else:
    #    print("Waiting For Fix...")

def fast_update(t):
    #print("(%f, %f, %f, " % gyro.gyro, end = '')
    #print("%f, %f, %f)" % accelerometer.acceleration)
    global counter
    g = gyro.gyro
    a = accelerometer.acceleration
    counter=counter+1

    file.write("%f, %f, %f, %f, %f, %f\r\n" % (g[0], g[1], g[2], a[0], a[1], a[2]))


def parse_GPS():
    print("=" * 40)  # Print a separator line.
    print(
        "Fix timestamp: {}/{}/{} {:02}:{:02}:{:02}".format(
            gps.timestamp_utc.tm_mon,  # Grab parts of the time from the
            gps.timestamp_utc.tm_mday,  # struct_time object that holds
            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
            gps.timestamp_utc.tm_year,  # the fix time.  Note you might
            gps.timestamp_utc.tm_hour,  # not get all data like year, day,
            gps.timestamp_utc.tm_min,  # month!
            gps.timestamp_utc.tm_sec,
        )
    )
    print("Latitude: {0:.6f} degrees".format(gps.latitude))
    print("Longitude: {0:.6f} degrees".format(gps.longitude))
    print("Fix quality: {}".format(gps.fix_quality))

    if gps.satellites is not None:
        print("# satellites: {}".format(gps.satellites))
    if gps.altitude_m is not None:
        print("Altitude: {} meters".format(gps.altitude_m))
    if gps.speed_knots is not None:
        print("Speed: {} knots".format(gps.speed_knots))
    if gps.track_angle_deg is not None:
        print("Track angle: {} degrees".format(gps.track_angle_deg))
    if gps.horizontal_dilution is not None:
        print("Horizontal dilution: {}".format(gps.horizontal_dilution))
    if gps.height_geoid is not None:
        print("Height geoid: {} meters".format(gps.height_geoid))

main()
