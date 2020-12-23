import pyvisa
import serial

class Get_keysight_53230A(object):
    def __init__(self):
       self.resourcemanager = pyvisa.highlevel.ResourceManager()
       self.resourcelist = ()
       self.resourcename = ""
       self.commond = ""
    
    def connection(self):
        self.resourcelist = self.resourcemanager.list_resources()
        if len(self.resourcelist) == 0:
            print("visa connection fail")
            return 20
        else:
            self.open_resource = self.resourcemanager.open_resource(self.resourcelist[0])
            #print(self.resourcelist)
            return 21

    def reading_53230A(self):
         frequency = self.open_resource.query('MEAS:FREQ?')
         return float(frequency)

