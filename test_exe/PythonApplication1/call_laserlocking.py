# -*- coding: utf-8 -*-
# Form implementation generated from reading ui file 'connect_me.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!
# 导入程序运行必须模块
import sys
# PyQt5中使用的基本控件都在PyQt5.QtWidgets模块中
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import QtWidgets
# 导入designer工具生成的UI模块
from laserlocking import Ui_MainWindow
import CEIC_26_AOM_control
import keysight_53230A
import tensorflow.keras.models as models
from sklearn.preprocessing import MinMaxScaler
import joblib
import numpy as np
import csv
import time
from coremorrow_control import CoremorrowControl


class MyMainForm(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainForm, self).__init__(parent)
        self.setupUi(self)
        self.CEIC_26_AOM = CEIC_26_AOM_control.CEIC_26_AOM_control()
        self.my_keysight_53230A = keysight_53230A.Get_keysight_53230A()
        self.start_frequency = 0
        self.baseline_frequency = 0
        # self.last_frequency = 0
        self.baseline = 0
        self.distance_frequency = 0
        self.currrent_frequency = 0
        self.model_predict_frequency = 0
        self.Vpzt = 2.5
        self.fre_to_v = 0
        self.pzt_flag = 0
        self.predictmodel = models.Sequential()
        self.sklearn = MinMaxScaler()
        self.coremorrowControl = self.initialization_coremorrow(serial_port="")  ###
        self.determine_AOM_port.clicked.connect(self.initialization_AOM_port)
        self.determine_model.clicked.connect(self.initialization_load_model)
        self.determine_sklearn.clicked.connect(self.initialization_sklearn)
        self.select_visa_button.clicked.connect(self.show_visa_resources_list)
        self.determine_53230.clicked.connect(self.initialization_53230A)
        self.get.clicked.connect(self.get53230A)
        self.initialization_button.clicked.connect(self.initialization)
        self.start_button.clicked.connect(self.laser_lock)

    def initialization_coremorrow(self, serial_port):
        Vpzt = 2.5
        coremorrowControl = CoremorrowControl(serial_port=serial_port)
        coremorrowControl.voltage_value_integer = int(Vpzt)
        coremorrowControl.voltage_value_score = Vpzt - coremorrowControl.voltage_value_integer
        coremorrowControl.send_single_voltage()
        time.sleep(1)
        return coremorrowControl

    def initialization_AOM_port(self):
        self.CEIC_26_AOM.port = self.port.text()

    def initialization_load_model(self):
        self.predictmodel = models.load_model(self.model.text())

    def initialization_sklearn(self):
        self.sklearn = joblib.load(self.sklearn_range.text())

    def show_visa_resources_list(self):
        self.comboBox.clear()
        self.my_keysight_53230A.resourcelist = self.my_keysight_53230A.resourcemanager.list_resources()
        self.comboBox.addItems(self.my_keysight_53230A.resourcelist)

    def initialization_53230A(self):
        self.my_keysight_53230A.resourcename = self.comboBox.currentText()
        self.my_keysight_53230A.open_resource = self.my_keysight_53230A.resourcemanager.open_resource(
            self.my_keysight_53230A.resourcename)
        self.my_keysight_53230A.open_resource.timeout = 6000

    def send_pzt_command(self, Vpzt):
        if Vpzt == 0:
            Vpzt = self.Vpzt
        self.coremorrowControl.voltage_value_integer = int(Vpzt)
        self.coremorrowControl.voltage_value_score = Vpzt - self.coremorrowControl.voltage_value_integer
        self.coremorrowControl.send_single_voltage()

    def get_fre_to_v(self):
        last = self.my_keysight_53230A.reading_53230A()
        Vpzt = 2.5
        sum = 0
        for i in range(5):
            Vpzt += 0.1
            print("v = ", Vpzt)
            self.send_pzt_command(Vpzt)
            time.sleep(2)
            cur = self.my_keysight_53230A.reading_53230A()
            delta = cur - last
            print("delta = ", delta)
            sum += cur - last
            last = cur
        fre_to_v = sum / 5
        if delta > 0:
            pzt_flag = 0
        else:
            pzt_flag = 1

        # print("pzt_flag", pzt_flag)
        return abs(fre_to_v), pzt_flag

    def get53230A(self):
        frequency = self.my_keysight_53230A.reading_53230A()
        self.show_53230A.setText(str(frequency))

    def save(number):
        with open('data0921.csv', 'a+', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(str(number) + '\t')

    def get_distance_frequency(self):
        self.currrent_frequency = self.my_keysight_53230A.reading_53230A()
        if self.currrent_frequency < 0:
            QMessageBox.information(QtWidgets.QWidget(), '信息提示对话框', "53230A数据获取出错", QMessageBox.Yes)
        else:
            self.save(self.currrent_frequency)
            self.distance_frequency = self.currrent_frequency - self.baseline

    def selectway(self):
        self.CEIC_26_AOM.control_frequency = 0
        for i in range(1, 4):
            self.CEIC_26_AOM.control_frequency = self.CEIC_26_AOM.control_frequency + i * 2000000
            self.CEIC_26_AOM.controlAOM()
            self.get_distance_frequency()
            time.sleep(1)
            if i == 3:
                self.CEIC_26_AOM.control_frequency = 0
                self.CEIC_26_AOM.controlAOM()
                # if a<last_frequency:
                if self.distance_frequency < 0:
                    self.CEIC_26_AOM.flag = 1
                else:
                    self.CEIC_26_AOM.flag = 0

    def initialization(self):
        self.start_frequency = self.my_keysight_53230A.reading_53230A()
        self.selectway()
        self.fre_to_v, self.pzt_flag = self.get_fre_to_v()
        self.baseline_frequency = self.frequency_baseline.text()

    def predict_frequency(self, sum_frequency):
        # data_min=new_scaler.min_
        # data_max=new_scaler.max_
        data_range = self.sklearn.data_range_
        data_scaler_min = self.sklearn.min_
        newData = sum_frequency / data_range + data_scaler_min

        predict_scaler = np.reshape(newData, (newData.shape[0], 1, 1))
        self.model_predict_frequency = self.predictmodel.predict(predict_scaler)
        self.model_predict_frequency = self.sklearn.inverse_transform(self.model_predict_frequency)

    def pzt_change_frequency_AOM(self):
        self.send_pzt_command(self.Vpzt)
        # logging.info(' Vpzt  = ' + str(Vpzt))
        self.CEIC_26_AOM.controlAOM()

    def laser_lock(self):
        self.baseline = self.my_keysight_53230A.reading_53230A()
        # sum_frequency = self.baseline
        # flg_frequency = 0
        free_frequency = self.baseline
        while True:
            # print('loop',i)
            self.distance_frequency = self.get_distance_frequency()
            delta_fre_to_baseline = self.currrent_frequency - self.baseline
            # sum_frequency += self.distance_frequency
            # flg_frequency += self.distance_frequency
            if self.Vpzt >= 0 or self.Vpzt <= 5:
                print('distance_frequency', self.distance_frequency)
                print('delta_fre_to_baseline', delta_fre_to_baseline)
                if delta_fre_to_baseline > self.fre_to_v or delta_fre_to_baseline < -self.fre_to_v:
                    # logging.info(' pzt  change')
                    if self.flag_pzt == 0:
                        if delta_fre_to_baseline > 0:
                            self.Vpzt -= 0.1
                            self.CEIC_26_AOM.control_frequency -= self.fre_to_v
                            free_frequency -= self.fre_to_v
                            # self.pzt_change_frequency_AOM(flg_frequency)
                            # logging.info(' Vpzt  = ' + str(Vpzt))
                        else:
                            self.Vpzt += 0.1
                            self.CEIC_26_AOM.control_frequency += self.fre_to_v
                            free_frequency += self.fre_to_v
                    else:
                        if delta_fre_to_baseline > 0:
                            self.Vpzt += 0.1
                            self.CEIC_26_AOM.control_frequency += self.fre_to_v
                            free_frequency += self.fre_to_v
                        else:
                            self.Vpzt -= 0.1
                            self.CEIC_26_AOM.control_frequency -= self.fre_to_v
                            free_frequency -= self.fre_to_v

                    self.pzt_change_frequency_AOM()
                    # logging.info(' Vpzt  = ' + str(Vpzt))
                    if self.Vpzt <= 0 or self.Vpzt >= 5:
                        # logging.info(' Vpzt  = ' + str(Vpzt))
                        # logging.info('sys.exit')
                        sys.exit()

                else:
                    self.show_distance_frequency.setText(str(self.distance_frequency / 1000000))

                    self.CEIC_26_AOM.control_frequency = \
                        self.predict_frequency(self, free_frequency) - self.baseline
                    self.CEIC_26_AOM.controlAOM()
                    free_frequency = (self.CEIC_26_AOM.control_frequency + self.baseline + self.currrent_frequency) / 2
            else:
                sys.exit()
            '''
            if self.distance_frequency > 50000000: #and distance_frequency < 1000000000:
               QMessageBox.information(QtWidgets.QWidget(), '信息提示对话框', "超出控制范围", QMessageBox.Yes)
                   #break
               #i+=1
               #elif distance_frequency > 1000000000:
                   #print('error1')
                   #break
            else:
               #print('distance_frequency',distance_frequency/1000000)
                   #control_frequency=predict(sum_frequency,dataset,model)-last_frequency
               self.show_distance_frequency.setText(str(self.distance_frequency/1000000))
               self.CEIC_26_AOM.control_frequency = self.predict_frequency(self,sum_frequency= sum_frequency) - self.baseline
               self.CEIC_26_AOM.controlAOM()
               # i+=1
            '''


if __name__ == "__main__":
    # 固定的，PyQt5程序都需要QApplication对象。sys.argv是命令行参数列表，确保程序可以双击运行
    app = QApplication(sys.argv)
    # 初始化
    myWin = MyMainForm()
    # 将窗口控件显示在屏幕上
    myWin.show()
    # 程序运行，sys.exit方法确保程序完整退出。
    sys.exit(app.exec_())