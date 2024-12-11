import socket
import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSlot, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QTextEdit
import numpy as np
import pyqtgraph as pg
import serial  # 导入serial库用于串口操作
from datetime import datetime

# 全局变量用于初始化串口，这里的参数需根据实际情况调整
ser = serial.Serial('COM3', 115200, timeout=0.1)

global folder
folder = 'esp_data/'

def Save_Csv(fileName, data):
    csv_file_path = fileName + '.csv'
    np.savetxt(csv_file_path, data, delimiter=',', fmt='%.8f')

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
                msg = "scan\n"
                ser.write(msg.encode('utf-8'))
                print("Serial Sent: ", msg)
                while self.is_running and not ser.in_waiting:
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
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = folder + f"Autosave_{timestamp}.csv"
                        Save_Csv(filename, np_data)
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
        self.setWindowTitle("Esp Scanning System")

        # Output Display
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        self.outputTextEdit = self.ui.findChild(QTextEdit, "Console")

        # Parameters
        self.esp_ip = "192.168.8.165"
        self.esp_port = 54080

        # Initialize data
        self.data = np.arange(1024).reshape(32, 32)
        self.dark_cur = np.zeros(1024).reshape(32, 32)
        self.light_cur = np.zeros(1024).reshape(32, 32)
        self.update = np.zeros(1024).reshape(32, 32)
        self.dark_cali = False
        self.light_cali = False

        # 创建串口读取线程实例
        self.serial_read_thread = SerialReadThread()
        self.serial_read_thread.update_data.connect(self.Handle_Update_Image)

        # Events
        self.ui.scan.clicked.connect(self.Scan)
        self.ui.stop.clicked.connect(self.Stop)
        self.ui.dark_record.clicked.connect(self.Dark)
        self.ui.light_record.clicked.connect(self.Light)
        self.ui.save_csv.clicked.connect(self.Manual_Save_Csv)

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
        
        self.raw_data = new_data.reshape(32, 32)
        '''
        flat_index = np.argmax(self.matrice)

        # 通过unravel_index函数将展平索引转换为二维坐标（行、列索引）
        row_index, col_index = np.unravel_index(flat_index, self.matrice.shape)

        print(f"矩阵中的最大值是 {self.matrice[row_index, col_index]}，其坐标为（{row_index}，{col_index}）")
        '''
        if self.dark_cali and self.light_cali:
            for i in range(32):
                for j in range(32):
                    if self.dark_cur[i][j] >= self.light_cur[i][j]:
                        self.update[i][j] = 0
                    elif self.dark_cur[i][j] >= self.raw_data[i][j]:
                        self.update[i][j] = 0
                    else:
                        self.update[i][j] = (self.raw_data[i][j] - self.dark_cur[i][j])/(self.light_cur[i][j]-self.dark_cur[i][j])
            self.img_item.setImage(self.update)
        else:
            self.img_item.setImage(self.raw_data)
        self.show()

    def Scan(self):
        try:
            if not self.serial_read_thread.isRunning():
                print("Start Serial Reading...")
                self.serial_read_thread.start()
        except Exception as e:
            print("Thread Error: ", e)

    def Dark(self):
        self.dark_cur = self.raw_data
        self.dark_cali = True
        print("dark record")
        
    def Light(self):
        self.light_cur = self.raw_data
        self.light_cali = True
        print("light record")

    def Stop(self):
        self.serial_read_thread.stop()
        print("串口读取停止.")

    def Manual_Save_Csv(self):
        if self.dark_cali and self.light_cali:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = folder + f"CaliData_{timestamp}.csv"
            temp_data = np.concatenate((self.update, self.raw_data, self.dark_cur, self.light_cur), axis = 0)
            Save_Csv(filename, temp_data)
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = folder + f"RawData_{timestamp}.csv"
            Save_Csv(filename, self.raw_data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    stats = Stats()
    stats.show()
    sys.exit(app.exec_())
