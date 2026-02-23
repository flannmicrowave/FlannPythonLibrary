import sys
import os

from configparser import ConfigParser

from qtpy import QtCore, QtWidgets, QtGui

from flann.vi.switch import Switch337


class MainWindow(QtWidgets.QMainWindow):
    '''Switch Counter Main Window'''
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Switch Counter")

        self.layoutMain = QtWidgets.QVBoxLayout()

        self.disableButtonGroup = QtWidgets.QButtonGroup()

        self.switch = None

        self.parser = ConfigParser()
        self.parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\switchCount.ini")))
        self.config = self.parser['GENERAL']
        self.counter = self.parser['COUNTER']['count']

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.switch_the_switch)

        if int(self.config['fullscreen']) == True:
            self.setWindowFlag(QtCore.Qt.FramelessWindowHint) 
            self.showFullScreen()

        '''User Interface'''

        # Layout 1

        self.layout1 = QtWidgets.QHBoxLayout()

        self.connectButton = QtWidgets.QPushButton("Connect")
        self.connectButton.setFixedSize(QtCore.QSize(100, 50))
        self.connectButton.setStyleSheet("color: white; background-color: lightgray")
        self.connectButton.clicked.connect(lambda: self.connect_switch())

        self.startButton = QtWidgets.QPushButton("Start")
        self.startButton.setFixedSize(QtCore.QSize(100, 50))
        self.startButton.setStyleSheet("color: white; background-color: lightgray")
        self.startButton.clicked.connect(lambda: self.start_counter())
        self.startButton.setEnabled(False)
        self.disableButtonGroup.addButton(self.startButton)

        self.stopButton = QtWidgets.QPushButton("Stop")
        self.stopButton.setFixedSize(QtCore.QSize(100, 50))
        self.stopButton.setStyleSheet("color: white; background-color: rgb(132,181,141)")
        self.stopButton.clicked.connect(lambda: self.stop_counter())
        self.stopButton.setEnabled(False)
        self.disableButtonGroup.addButton(self.stopButton)

        self.disconnectButton = QtWidgets.QPushButton("Disconnect")
        self.disconnectButton.setFixedSize(QtCore.QSize(100, 50))
        self.disconnectButton.setStyleSheet("color: white; background-color: lightgray")
        self.disconnectButton.clicked.connect(lambda: self.disconnect_switch())

        self.exitButton = QtWidgets.QPushButton("Exit")
        self.exitButton.setFixedSize(QtCore.QSize(100, 50))
        self.exitButton.setStyleSheet("color: white; background-color: gray")
        self.exitButton.clicked.connect(lambda: self.closeEvent(self))
        
        # LCD Display Layout

        self.lcdDisplay = QtWidgets.QLCDNumber(self.centralWidget())
        self.lcdDisplay.setDigitCount(len(str(self.counter)))
        self.lcdDisplay.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdDisplay.setStyleSheet("color: white; font-size: 50px; border: 0px;")
        self.lcdDisplay.display(int(self.counter))

        '''Layout'''
        self.layout1.addWidget(self.connectButton)
        self.layout1.addWidget(self.startButton)
        self.layout1.addWidget(self.stopButton)
        self.layout1.addWidget(self.disconnectButton)
        self.layout1.addWidget(self.exitButton)

        self.layoutMain.addLayout(self.layout1)
        self.layoutMain.addWidget(self.lcdDisplay)

        self.widgetMain = QtWidgets.QWidget(self)
        self.widgetMain.setAutoFillBackground(True)
        self.widgetMain.setStyleSheet("background-color: rgb(0,122,78);")
        self.widgetMain.setLayout(self.layoutMain)
        self.setCentralWidget(self.widgetMain)

    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()

    def connect_switch(self):
        try:
            if self.switch is None:
                self.switch = Switch337(switch=int(self.config['switch']), 
                                        address=str(self.config['address']), 
                                        timeout=float(self.config['timeout']), 
                                        baudrate=int(self.config['baudrate']))
            self.startButton.setStyleSheet("color: white; background-color: rgb(132,181,141)")    
            for button in self.disableButtonGroup.buttons():
                button.setEnabled(True)    
                
        except:
            print("Error: Unable to connect to the switch.")


    def disconnect_switch(self):
        if self.switch is not None:
            self.switch.close()
            self.switch = None
            self.startButton.setStyleSheet("color: white; background-color: lightgray")
        for button in self.disableButtonGroup.buttons():
            button.setEnabled(False)

    def update_parser(self):
        new_parser = ConfigParser()
        new_parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\switchCount.ini")))
        update_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\switchCount.ini")), 'w')
        new_parser['COUNTER']['count'] = str(self.counter)
        new_parser.write(update_file)
        update_file.close()

    def start_counter(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.timer.start(int(self.config['sleep']))  # Set the timer interval to the sleep time in milliseconds

    def stop_counter(self):
        self.startButton.setEnabled(True)
        self.stopButton.setEnabled(False)
        self.timer.stop()

    def switch_the_switch(self):
        self.counter = int(self.counter) + 1
        self.switch.toggle_all()  # Toggle all switches connected to the switch-box
        self.update_parser()
        print(self.counter)
        self.lcdDisplay.setDigitCount(len(str(self.counter)))  # Auto expand the display size
        self.lcdDisplay.display(int(self.counter))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\FlannMicrowave.ico"))))
    window = MainWindow()
    window.show()

    app.exec()
