import socket
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QTextEdit
import numpy as np
import pyqtgraph as pg
import bluetooth
import serial  # 导入serial库用于串口操作

# 全局变量用于初始化串口，这里的参数需根据实际情况调整
ser = serial.Serial('COM3', 115200, timeout=0.1)


class EmittingStream(QObject):
    textWritten = pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))


class SerialReadThread(QThread):
    update_data = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.is_running = False

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                # 先发送扫描信号
                ser.write(b'scan\n')
                print("sent")
                while not ser.in_waiting:
                    time.sleep(0.1)
                if ser.in_waiting:  # 检查串口是否有数据可读
                    print("rec")
                    raw_data = ser.read(10000).decode('utf-8')[3:-4] # 读取一行数据并解码、去除空白字符
                    print(raw_data)
                    data_list = raw_data.split('.')  # 按点分割数据，假设ESP32发送的数据是以点分隔每个元素的格式
                    if len(data_list) == 32 * 32:  # 确保接收到的数据量符合预期（这里假设是32x32的数据格式）
                        int_data_list = list(map(int, data_list))
                        np_data = np.array(int_data_list).reshape(32, 32)
                        self.update_data.emit(np_data)
                    else:
                        print("error")

            except Exception as e:
                print("串口读取线程错误:", e)
                break

    def stop(self):
        self.is_running = False


class Stats(QMainWindow):
    old_image = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        # Load UI
        self.ui = uic.loadUi("ScanGUI.ui", self)
        self.setWindowTitle("Gas Source Tracking System")

        # Output Display
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.outputTextEdit = self.ui.findChild(QTextEdit, "Console")

        # Parameters
        self.esp_ip = "192.168.8.165"
        self.esp_port = 54080

        # Initialize data
        self.data = np.arange(1024).reshape(32, 32)

        # 创建串口读取线程实例
        self.serial_read_thread = SerialReadThread()
        self.serial_read_thread.update_data.connect(self.Handle_Update_Image)

        # Events
        self.ui.scan.clicked.connect(self.Scan)
        self.ui.stop.clicked.connect(self.Stop)

        # Form Greyscale Color Map
        colors = [(i, i / 2, 0) for i in range(256)]
        self.colormap = pg.ColorMap(pos=np.linspace(0.0, 1.0, 256), color=colors)

        # Figures Initialization
        self.plot = self.ui.IMG1

        self.img_item = pg.ImageItem()
        plot_instance = self.plot.addPlot()
        plot_instance.addItem(self.img_item)
        #self.img_item.setLookupTable(self.colormap.getLookupTable())
        self.img_item.setImage(self.data)
        plot_instance.hideAxis('bottom')
        plot_instance.hideAxis('left')

        self.show()

    @pyqtSlot(str)
    def normalOutputWritten(self, text):
        cursor = self.outputTextEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.outputTextEdit.setTextCursor(cursor)
        self.outputTextEdit.ensureCursorVisible()

    def on_connection_success(self):
        print("Successfully connected to the server!")

    def on_connection_failed(self, error_message):
        print(error_message)

    @pyqtSlot(np.ndarray)
    def Handle_Update_Image(self, new_data):
        matrice = new_data.reshape(32, 32)
        self.img_item.setImage(matrice)
        self.show()

    def Scan(self):
        try:
            # 这里不再创建ScanThread，而是直接操作serial_read_thread
            if not self.serial_read_thread.isRunning():
                print("Start Serial Reading...")
                self.serial_read_thread.start()
        except:
            print("线程相关错误.")

    def Stop(self):
        self.serial_read_thread.stop()
        print("串口读取停止.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    stats = Stats()
    stats.show()
    sys.exit(app.exec_())