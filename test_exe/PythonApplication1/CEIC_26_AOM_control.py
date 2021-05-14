import binascii

import crcmod
import serial
import numpy as np
import time


class CEIC_26_AOM_control(object):
    def __init__(self):
        self.port = ""
        self.control_frequency = 0
        self.__crc16_hex = ""
        self.__crc16_commond = ""
        self.__FTW = 0
        self.__control_frequency_commond = ""
        self.flag = 0
        self.control_commond = ""


    def caculate_frequncy(self):
        if self.flag == 1:
            control_frequency = (300000000 + self.control_frequency)
            self.__FTW = int(np.round(control_frequency * 4294967296 / 1000000000))
            # print('control',control)
        else:
            control_frequency = (300000000 - self.control_frequency)
            self.__FTW = int(np.round(control_frequency * 4294967296 / 1000000000))
            # print('control',control)


    def caculate_crc16(self):
        crc16 = crcmod.predefined.Crc('crc-16')
        crc16_hex = binascii.unhexlify(self.__crc16_hex)
        crc16.update(crc16_hex)
        self.__crc16_commond = '{:x}'.format(crc16.crcValue)


    def get_control_commond(self):
        self.__control_frequency_commond = '{:x}'.format(self.__FTW)
        len_control_frequency_commond = len(self.__control_frequency_commond)
        if len_control_frequency_commond == 8:
            self.__control_frequency_commond = self.__control_frequency_commond
        else:
            self.__control_frequency_commond = (8 - len_control_frequency_commond) * '{:x}'.format(
                0x0) + self.__control_frequency_commond
        '''
        elif len_control_frequency_commond == 7:
            self.__control_frequency_commond = '{:x}'.format(0x0) + self.__control_frequency_commond
        elif len_b == 6:
            self.__control_frequency_commond = 2 * '{:x}'.format(0x0) + self.__control_frequency_commond
        elif len_b == 5:
            self.__control_frequency_commond = 3 * '{:x}'.format(0x0) + self.__control_frequency_commond
        elif len_b == 4:
            self.__control_frequency_commond = 4 * '{:x}'.format(0x0) + self.__control_frequency_commond
        elif len_b == 3:
            self.__control_frequency_commond = 5 * '{:x}'.format(0x0) + self.__control_frequency_commond
        elif len_b == 2:
            self.__control_frequency_commond = 6 * '{:x}'.format(0x0) + self.__control_frequency_commond
        else:
            self.__control_frequency_commond = 7 * '{:x}'.format(0x0) + self.__control_frequency_commond
        '''
        self.__crc16_hex = '{:x}'.format(0xA55A5AA5) + '{:x}'.format(0x0) + '{:x}'.format(0x1) + '{:x}'.format(
            0x0) + '{:x}'.format(0x1) + self.__control_frequency_commond + '{:x}'.format(0x3) + '{:x}'.format(
            0xff1) + '{:x}'.format(0x5AA5A55A)
        self.__crc16_commond = self.caculate_crc16()
        len_crc16_commond = len(self.__crc16_commond)
        if len_crc16_commond == 4:
            self.__crc16_commond = self.__crc16_commond
        else:
            self.__crc16_commond = (4 - len_crc16_commond) * '{:x}'.format(0x0) + self.__crc16_commond
        '''
        elif len_c == 3:
            self.__crc16_commond = '{:x}'.format(0x0) + self.__crc16_commond
        elif len_c == 2:
            self.__crc16_commond = 2 * '{:x}'.format(0x0) + self.__crc16_commond
        else:
            self.__crc16_commond = 3 * '{:x}'.format(0x0) + self.__crc16_commond
        '''
        self.control_commond = self.__crc16_hex + self.__crc16_commond


    def controlAOM(self):
        # d_control = (delta_distance_frequency)*4/5/1000
        if self.control_frequency > 50000000 and self.control_frequency < -50000000:
            print('errror2')
        else:
            self.caculate_frequncy()
            self.get_control_commond()
            # print(type(frequency_AOM))
            ser = serial.Serial('/dev/ttyUSB0', 9600)
            if ser.isOpen == False:
                ser.open()  # 打开串口
            date = bytes.fromhex(self.control_commond)
            # print('date',date)
            ser.write(date)
            # frequency_AOM=""
            while True:
                size = ser.inWaiting()  # 获得缓冲区字符
                if size != 0:
                    # response = ser.read(size)        # 读取内容并显示
                    # print response
                    ser.flushInput()  # 清空接收缓存区
                    time.sleep(0.1)  # 软件延时
                ser.close()
                break
