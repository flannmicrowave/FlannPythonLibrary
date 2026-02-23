import sys
import os

from configparser import ConfigParser

from qtpy import QtCore, QtWidgets, QtGui

from flann.vi.attenuator import Attenuator024, Attenuator625

class Color(QtWidgets.QWidget):
    def __init__(self, r,g,b):
        super().__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(r,g,b))
        self.setPalette(palette)

class MenuWindow(QtWidgets.QWidget):
    '''Settings window for the 024'''
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Menu")
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\FlannMicrowave.ico"))))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setFixedSize(QtCore.QSize(200, 300))

        self.attenuator = None
        self.attenuator_series = 'Attenuator'
        self.parser = ConfigParser()
        self.parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\attenuatorSettings.ini")))
        self.config = self.parser['GENERAL']

        '''User Interface'''

        self.layoutMain = QtWidgets.QVBoxLayout()

        self.layoutAddress = QtWidgets.QHBoxLayout()
        self.layoutAddress.addWidget(QtWidgets.QLabel("Address:"))
        self.addressLineEdit = QtWidgets.QLineEdit()
        self.addressLineEdit.setText(self.config['address'])
        self.layoutAddress.addWidget(self.addressLineEdit)
        self.layoutMain.addLayout(self.layoutAddress)

        self.layoutBaudRate = QtWidgets.QHBoxLayout()
        self.layoutBaudRate.addWidget(QtWidgets.QLabel("Baud Rate:"))
        self.baudRateLineEdit = QtWidgets.QLineEdit()
        self.baudRateLineEdit.setText(str(self.config['baudrate']))
        self.layoutBaudRate.addWidget(self.baudRateLineEdit)
        self.layoutMain.addLayout(self.layoutBaudRate)

        self.layoutTimeout = QtWidgets.QHBoxLayout()
        self.layoutTimeout.addWidget(QtWidgets.QLabel("Serial Timeout:"))
        self.timeoutLineEdit = QtWidgets.QLineEdit()
        self.timeoutLineEdit.setText(str(self.config['timeout']))
        self.layoutTimeout.addWidget(self.timeoutLineEdit)
        self.layoutMain.addLayout(self.layoutTimeout)

        self.layoutTcpPort = QtWidgets.QHBoxLayout()
        self.layoutTcpPort.addWidget(QtWidgets.QLabel("TCP Port:"))
        self.tcpPortLineEdit = QtWidgets.QLineEdit()
        self.tcpPortLineEdit.setText(str(self.config['tcp_port']))
        self.layoutTcpPort.addWidget(self.tcpPortLineEdit)
        self.layoutMain.addLayout(self.layoutTcpPort)

        self.layoutAppDelay = QtWidgets.QHBoxLayout()
        self.layoutAppDelay.addWidget(QtWidgets.QLabel("App Delay:"))
        self.appDelayLineEdit = QtWidgets.QLineEdit()
        self.appDelayLineEdit.setText(str(self.config['sleep']))
        self.layoutAppDelay.addWidget(self.appDelayLineEdit)
        self.layoutMain.addLayout(self.layoutAppDelay)

        self.connectButton = QtWidgets.QPushButton("Connect")
        self.connectButton.clicked.connect(lambda: self.connect_to_atten())
        self.layoutMain.addWidget(self.connectButton)

        self.nameLineEdit = QtWidgets.QTextEdit()
        self.nameLineEdit.setReadOnly(True)  # Read-only
        self.nameLineEdit.setStyleSheet("QTextEdit {background-color:white; color:black; border: 0px;}")
        self.nameLineEdit.setFixedHeight(40)
        self.layoutMain.addWidget(self.nameLineEdit)
        
        self.disconnectButton = QtWidgets.QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(lambda: self.disconnect_from_atten())
        self.layoutMain.addWidget(self.disconnectButton)

        self.positionToggle = QtWidgets.QCheckBox()
        self.positionToggle.setText("Set Position")
        self.layoutMain.addWidget(self.positionToggle)
        
        self.setLayout(self.layoutMain)

    def connect_to_atten(self):
        try:
            if self.attenuator is None and self.addressLineEdit.text().lower().startswith('com'):
                self.attenuator = Attenuator024(address=self.addressLineEdit.text(), 
                                                timeout=float(self.timeoutLineEdit.text()), 
                                                baudrate=int(self.baudRateLineEdit.text()), 
                                                timedelay=float(self.appDelayLineEdit.text()))
                self.attenuator_series = '024'
            else:
                self.attenuator = Attenuator625(address=self.addressLineEdit.text(), 
                                                tcp_port=int(self.tcpPortLineEdit.text()), 
                                                timedelay=float(self.appDelayLineEdit.text()))
                self.attenuator_series = '625'
            name = self.attenuator.id()
            self.nameLineEdit.setText(name)
            self.update_parser()
        except:
            print('Connection Error')

    def disconnect_from_atten(self):
        if self.attenuator is not None:
            self.attenuator.close()
            self.attenuator = None
            self.nameLineEdit.clear()
            self.update_parser()

    def update_parser(self):
        new_parser = ConfigParser()
        new_parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\attenuatorSettings.ini")))
        update_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\attenuatorSettings.ini")), 'w')
        new_parser['GENERAL']['address'] = str(self.addressLineEdit.text())
        new_parser['GENERAL']['baudrate'] = str(self.baudRateLineEdit.text())
        new_parser['GENERAL']['timeout'] = str(self.timeoutLineEdit.text())
        new_parser.write(update_file)
        update_file.close()
        

class MainWindow(QtWidgets.QMainWindow):
    '''Main attenuator control window insprired by the Flann 625'''
    def __init__(self):
        super().__init__()

        self._version = '1.2.0'

        self.setWindowTitle(f"Flann Attenuator {self._version}")
        self.setFixedSize(QtCore.QSize(260, 300))

        self.mWindow = MenuWindow()
        self.config = self.mWindow.config
        self.attenuator = self.mWindow.attenuator

        self.layoutMain = QtWidgets.QVBoxLayout()

        self.disableButtonGroup = QtWidgets.QButtonGroup()

        '''User Interface'''

        # Layout 1
        self.layout1 = QtWidgets.QHBoxLayout()

        self.menuButton = QtWidgets.QPushButton("Menu", checkable=True)
        self.menuButton.setFixedSize(QtCore.QSize(50, 50))
        self.menuButton.clicked.connect(lambda: self.toggle_menu_window())

        # Layout 1a
        self.layout1a = QtWidgets.QGridLayout()

        self.layout1a.addWidget(QtWidgets.QLabel("Actual:"), 0,0)
        self.attenReadLineEdit = QtWidgets.QLineEdit()
        self.attenReadLineEdit.setReadOnly(True)    # Read-only
        self.attenReadLineEdit.setFixedWidth(120)
        self.attenReadLineEdit.setStyleSheet("background-color: white")
        self.layout1a.addWidget(self.attenReadLineEdit, 0,1)
        self.layout1a.addWidget(QtWidgets.QLabel("dB"), 0,2)

        self.layout1a.addWidget(QtWidgets.QLabel("Entry:"), 1,0)
        self.attenEnterLineEdit = QtWidgets.QLineEdit()
        self.attenEnterLineEdit.returnPressed.connect(lambda: self.go_to_attenuation())
        self.attenEnterLineEdit.setFixedWidth(120)
        self.attenEnterLineEdit.setStyleSheet("background-color: white")
        self.layout1a.addWidget(self.attenEnterLineEdit, 1,1)
        self.layout1a.addWidget(QtWidgets.QLabel("dB"), 1,2)
        
        # Layout 2
        self.layout2 = QtWidgets.QHBoxLayout()
        
        # Layout 2a
        self.layout2a = QtWidgets.QGridLayout()
        self.keyboardButtonMap = {}
        keyboard = [['7', '8', '9'],
                    ['4', '5', '6'],
                    ['1', '2', '3'],
                    ['C', '0', '.']]
        for row, keys in enumerate(keyboard):
            for col, key in enumerate(keys):
                self.keyboardButtonMap[key] = QtWidgets.QPushButton(key)
                self.keyboardButtonMap[key].setFixedSize(QtCore.QSize(50, 50))
                self.keyboardButtonMap[key].setStyleSheet("background-color: lightgray")
                if key == 'C':
                    self.keyboardButtonMap[key].clicked.connect(self.clear_attenuation_entry)
                else:
                    self.keyboardButtonMap[key].clicked.connect(lambda _, key=key: self.append_attenuation_entry(key))
                self.layout2a.addWidget(self.keyboardButtonMap[key], row, col)

        # Layout 2b
        self.layout2b = QtWidgets.QVBoxLayout()

        self.incrementButton = QtWidgets.QPushButton("Inc +")
        self.incrementButton.clicked.connect(lambda: self.increment_attenuation())
        self.disableButtonGroup.addButton(self.incrementButton)
        self.incrementButton.setFixedHeight(76)
        self.layout2b.addWidget(self.incrementButton)
        self.decrementButton = QtWidgets.QPushButton("Dec -")
        self.decrementButton.clicked.connect(lambda: self.decrement_attenuation())
        self.disableButtonGroup.addButton(self.decrementButton)
        self.decrementButton.setFixedHeight(76)
        self.layout2b.addWidget(self.decrementButton)
        self.enterButton = QtWidgets.QPushButton("Goto")
        self.enterButton.clicked.connect(lambda: self.go_to_attenuation())
        self.disableButtonGroup.addButton(self.enterButton)
        self.enterButton.setFixedHeight(50)
        self.layout2b.addWidget(self.enterButton)

        '''Layout'''

        self.layout1.addWidget(self.menuButton)
        self.layout1.addLayout(self.layout1a)

        self.layout2.addLayout(self.layout2a)
        self.layout2.addLayout(self.layout2b)   

        self.layoutMain.addLayout(self.layout1)
        self.layoutMain.addLayout(self.layout2) 

        self.widgetMain = Color(132,181,141)
        self.widgetMain.setLayout(self.layoutMain)
        self.setCentralWidget(self.widgetMain)

    def toggle_menu_window(self):  # Currently this limits the main window interactions due to an inheritance coding error where the self.attenuator does not update when the settings are changed in the menu window
        if self.mWindow.isVisible():
            self.mWindow.hide()
            for button in self.disableButtonGroup.buttons():
                button.setEnabled(True)
            self.attenEnterLineEdit.setReadOnly(False)
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
            self.show()
        else:
            self.mWindow.show()
            for button in self.disableButtonGroup.buttons():
                button.setEnabled(False)
            self.attenEnterLineEdit.setReadOnly(True)
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            self.show()
        self.attenuator = self.mWindow.attenuator
        self.setWindowTitle(f'Flann {self.mWindow.attenuator_series}')

    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()

    def append_attenuation_entry(self, text):
        self.attenEnterLineEdit.setText(self.read_attenuation_entry() + text)
        self.attenEnterLineEdit.setFocus()

    def read_attenuation_entry(self):
        return self.attenEnterLineEdit.text()
    
    def clear_attenuation_entry(self):
        self.attenEnterLineEdit.clear()

    def get_current_attenuation(self):
        try:
            current_val = self.attenuator.attenuation()  # get the current attenuation value
            print(current_val)
        except ValueError:
            current_val = '-1'
            print("Error reading current attenuation value")
        
        return current_val
    
    def go_to_attenuation(self):
        newAttenuation = float(self.read_attenuation_entry())
        print(f"New attenuation: {newAttenuation}")
        self.clear_attenuation_entry()

        if self.attenuator == None:
            self.attenReadLineEdit.setText('Connection Error')
            print("No attenuator connected")
            return
        if self.mWindow.positionToggle.isChecked():
            try:
                self.attenuator.position = int(newAttenuation)  # set the position in steps
                self.attenReadLineEdit.setText(f'Position {newAttenuation}')
            except:
                print("Error setting position")
                self.attenReadLineEdit.setText('Position Error')
        else:
            try:
                self.attenuator.attenuation = newAttenuation  # set the attenuation value
                self.attenReadLineEdit.setText(str(self.get_current_attenuation()))
            except:
                print("Error setting attenuation")
                self.attenReadLineEdit.setText('dB Error')

    def increment_attenuation(self):
        increment = float(self.read_attenuation_entry())
        print(f"Increment: {increment}")
        try:
            self.attenuator.increment_store = increment  # set the increment value
            self.attenuator.increment_store()
            self.attenuator.increment()  # increment the attenuation
            self.attenReadLineEdit.setText(str(self.get_current_attenuation()))
        except:
            print("Error incrementing attenuation")
            self.attenReadLineEdit.setText('dB Error')

    def decrement_attenuation(self):
        decrement = float(self.read_attenuation_entry())
        print(f"Decrement: {decrement}")
        try:
            self.attenuator.increment_store = decrement
            self.attenuator.increment_store()
            self.attenuator.decrement()  # decrement the attenuation
            self.attenReadLineEdit.setText(str(self.get_current_attenuation()))
        except:
            print("Error decrementing attenuation")
            self.attenReadLineEdit.setText('dB Error')
            

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\FlannMicrowave.ico"))))
    window = MainWindow()
    window.setWindowFlag(QtCore.Qt.CustomizeWindowHint, True)
    window.show()

    app.exec()
