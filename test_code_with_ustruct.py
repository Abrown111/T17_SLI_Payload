from machine import Pin, I2C, Timer
import sdcard
import uos
import utime
import time
from ustruct import unpack

gyro = I2C(0, sda=Pin(4), scl=Pin(5))
accel = I2C(1, sda=Pin(2), scl=Pin(3))
cs = machine.Pin(15, machine.Pin.OUT)
spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))
sd = sdcard.SDCard(spi, cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")


_buffer = bytearray(6)


ADXL345_I2C= 0x53
DATAX0 = 0x32
DATAX1 = 0x33
DATAY0 = 0x34
DATAY1 = 0x35
DATAZ0 = 0x36
DATAZ1 = 0x37
BW_RATE = 0x2C
POWER_CTL = 0x2D
DATA_FORMAT = 0x31
I2C_REG=107
OUT_X_L=40
OUT_X_H=41
OUT_Y_L=42
OUT_Y_H=43
OUT_Z_L=44
OUT_Z_H=45
FIFO_CTRL=46
CTRL5=36
CTRL1=32
Sens = 1000/8.75

accel.writeto_mem(ADXL345_I2C, POWER_CTL, b'\x08')
accel.writeto_mem(ADXL345_I2C, BW_RATE, b'\x0f')
accel.writeto_mem(ADXL345_I2C, DATA_FORMAT, b'\x0f')
gyro.writeto_mem(I2C_REG, CTRL1, b'\x0f')



accelfile=open("/sd/acceldata.csv", "w")   
    
start = time.time()

while (time.time() - start) < 1:
    _buffer[0] = 0x32 & 0xFF
    accel.writeto(0x53, _buffer[:1])
    accel.readfrom_into(0x53, _buffer)
    x, y, z = unpack("<hhh", _buffer)
    x = x * 1/256 * 32.2
    y = y * 1/256 * 32.2
    z = z * 1/256 * 32.2
    accelfile.write(str(x) + "," + str(y) + "," + str(z) + "\n")
    
accelfile.close()
print("done")
