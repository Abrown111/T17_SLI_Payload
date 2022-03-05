from machine import Pin, I2C, Timer
import sdcard
import uos
import utime
import time

gyro = I2C(0, sda=Pin(4), scl=Pin(5))
accel = I2C(1, sda=Pin(2), scl=Pin(3), freq=400000)
cs = machine.Pin(15, machine.Pin.OUT)
spi = machine.SPI(1, baudrate=1000000, polarity=0, phase=0, bits=8, firstbit=machine.SPI.MSB, sck=machine.Pin(10), mosi=machine.Pin(11), miso=machine.Pin(12))
sd = sdcard.SDCard(spi, cs)
vfs = uos.VfsFat(sd)
uos.mount(vfs, "/sd")


button=Pin(20, Pin.IN)

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
counter = 0

accel.writeto_mem(ADXL345_I2C, POWER_CTL, b'\x08')
accel.writeto_mem(ADXL345_I2C, BW_RATE, b'\r')
accel.writeto_mem(ADXL345_I2C, DATA_FORMAT, b'\x00')
gyro.writeto_mem(I2C_REG, CTRL1, b'\x0f')

def twos_comp(fullbit):
    if fullbit & 32768:
        return -((fullbit^65535)+1)
    else:
        return fullbit

def roll(adress, xreg1, xreg2):
    X1=gyro.readfrom_mem(adress, xreg1, 1)
    X2=gyro.readfrom_mem(adress, xreg2, 1)
    xvalues=((X2[0]<<8)|X1[0])
    xvalues=twos_comp(xvalues)/Sens
    return xvalues

def pitch(adress, yreg1, yreg2):
    Y1=gyro.readfrom_mem(adress, yreg1, 1)
    Y2=gyro.readfrom_mem(adress, yreg2, 1)
    yvalues=((Y2[0]<<8)|Y1[0])
    yvalues=twos_comp(yvalues)/Sens
    return yvalues

def yaw(adress, zreg1, zreg2):
    Z1=gyro.readfrom_mem(adress, zreg1, 1)
    Z2=gyro.readfrom_mem(adress, zreg2, 1)
    zvalues=((Z2[0]<<8)|Z1[0])
    zvalues=twos_comp(zvalues)/Sens
    return zvalues

def accel_x(adress, xreg1, xreg2):
    Ax=accel.readfrom_mem(adress, xreg1, 1)
    Bx=accel.readfrom_mem(adress, xreg2, 1)
    x_accel=((Bx[0]<<8)|Ax[0])
    x_accel=twos_comp(x_accel)/256
    x_accel=x_accel*32.2
    return x_accel

def accel_y(adress, yreg1, yreg2):
    Ay=accel.readfrom_mem(adress, yreg1, 1)
    By=accel.readfrom_mem(adress, yreg2, 1)
    y_accel=((By[0]<<8)|Ay[0])
    y_accel=twos_comp(y_accel)*32.2
    return y_accel

def accel_z(adress, zreg1, zreg2):
    Az=accel.readfrom_mem(adress, zreg1, 1)
    Bz=accel.readfrom_mem(adress, zreg2, 1)
    z_accel=((Bz[0]<<8)|Az[0])
    z_accel=twos_comp(z_accel)*32.2
    return z_accel

start_time=time.time()
accelfile=open("/sd/acceldata.csv", "w")

def fast_update(t):
    x_acceleration=accel_x(ADXL345_I2C, DATAX0, DATAX1)
    y_acceleration=accel_y(ADXL345_I2C, DATAY0, DATAY1)
    z_acceleration=accel_z(ADXL345_I2C, DATAZ0, DATAZ1)
    x_gyro=roll(I2C_REG, OUT_X_L, OUT_X_H)
    y_gyro=pitch(I2C_REG, OUT_Y_L, OUT_Y_H)
    z_gyro=yaw(I2C_REG, OUT_Z_L, OUT_Z_H)
    accelfile.write(str(x_acceleration) + "\n")
    if button.value() == 0:
        collection_timer.deinit()
        accelfile.close()
        data = open("/sd/acceldata.csv", "r")
        datalength=data.readlines()
        print(accel_x(ADXL345_I2C, DATAX0, DATAX1))
        print(len(datalength))
        print(time.time()-start_time)
        data.close()
        print("done")

collection_timer = Timer(period=3, mode=Timer.PERIODIC, callback=fast_update)



    
        
    
        
    
        

    