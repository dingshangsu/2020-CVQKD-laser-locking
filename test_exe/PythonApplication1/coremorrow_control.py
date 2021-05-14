import serial


class CoremorrowControl(object):
    '''芯明天E53D系列单路控制'''

    def __init__(self, serial_port):
        '''初始化包括指令码，电压值，定时发送时间,默认单通道'''
        self.channel_number = '{:02x}'.format(0)
        self.address = '{:02x}'.format(1)
        self.voltage_value_integer = 0  # 前两个字节表示整数电压
        self.voltage_value_score = 0  # 后两个字节表示小数电压，一位表示0.1mv
        # self.regulary_send_time = 0
        self.serial_port = serial_port

    def send_single_voltage(self):
        ser = serial.Serial(self.serial_port, 9600, timeout=5)
        if ser.isOpen():
            # print(self.serial_port+"is open")
            command_number_hex = '{:02x}'.format(0)
            if self.voltage_value_integer >= 0:
                voltage_value_integer_hex = '{:04x}'.format(self.voltage_value_integer)
                voltage_value_score_hex = '{:04x}'.format(round(self.voltage_value_score * 10000))

                #voltage_value_integer_hex = '{:04x}'.format(int(voltage))
                #voltage_value_score_hex = '{:04x}'.format(int(65535*(voltage-int(voltage))))
                '''
                check_number = '{:04x}'.format(
                    0xaa ^ int(self.address, 16) ^ 0x0b ^ 0x00 ^ 0x00 ^ int(self.channel_number[0:2], 16) ^ int(
                        voltage_value_integer_hex, 16) ^ int(voltage_value_integer_hex, 16) ^ int(
                        voltage_value_score_hex, 16))
                '''
                check_number = '{:04x}'.format(
                    0xaa ^ int(self.address, 16) ^ 0x0b ^ 0x00 ^ 0x00 ^ int(self.channel_number, 16) ^ int(
                        voltage_value_integer_hex, 16) ^ int(voltage_value_score_hex, 16))
                check_number = '{:02x}'.format(int(check_number[0:2], 16) ^ int(check_number[2:4], 16))
                # print("checkNum = ", check_number)

                #check_number = '{:02x}'.format(0xaa^int(self.address,16)^0x0b^0x00^0x00^int(self.channel_number,16)^int(voltage_value_integer_hex,16)^int(voltage_value_score_hex,16))
                # print(check_number_orignal[2:4])
                # check_number='{:x}'.format(int(binascii.b2a_hex(check_number_orignal[0:2].encode()),16)^int(binascii.b2a_hex(check_number_orignal[2:4].encode()),16))
                #print("check_number", check_number)
                '''
                send_single_voltage_command = '{:02x}'.format(0xaa) + self.address + '{:02x}'.format(
                    0x0b) + command_number_hex + '{:02x}'.format(
                    0) + voltage_value_integer_hex + voltage_value_score_hex + check_number
                '''
                send_single_voltage_command = '{:02x}'.format(0xaa) + self.address + '{:02x}'.format(
                    0x0b) + command_number_hex + '{:02x}'.format(
                    0) + self.channel_number + voltage_value_integer_hex + voltage_value_score_hex + check_number
                # send_single_voltage_commod = '{:02x}'.format(0xaa)+self._adress+'{:02x}'.format(0x0b)+'{:02x}'.format(0x00)+'{:02x}'.format(0x00)+voltage_value_integer_hex+voltage_value_score_hex+check_number
                # print("send_single_voltage_command",send_single_voltage_command)
                ser.write(bytes.fromhex(send_single_voltage_command))
                # print(send_single_voltage_commod)
                ser.close()
            else:
                print("Voltage is negative")
        else:
            print(self.serial_port + "is close")

    def read_single_voltage(self):
        ser = serial.Serial(self.serial_port, 9600, timeout=5)
        if ser.isOpen():
            # print(self.serial_port+"is open")
            check_number = '{:02x}'.format(
                0xaa ^ int(self.address, 16) ^ 0x07 ^ 0x05 ^ 0x00 ^ int(self.channel_number, 16))
            send_single_voltage_command = '{:02x}'.format(0xaa) + self.address + '{:02x}'.format(7) \
                                          + '{:02x}'.format(5) + '{:02x}'.format(0) + self.channel_number + check_number
            ser.write(bytes.fromhex(send_single_voltage_command))
            # serial_ports_waiting_number = ser.in_waiting()
            recv = ser.readline()
            recv_array = [hex(x) for x in recv]
            # print(len(recv))
            # print(recv_array)
            voltage_value_integer = int(recv_array[6], 16) * 256 + int(recv_array[7], 16)
            voltage_value_score = int(recv_array[8], 16) * 256 + int(recv_array[9], 16)
            ser.close()
            return voltage_value_integer + voltage_value_score * (1 / 65535)
        else:
            print(self.serial_port + "is close")
