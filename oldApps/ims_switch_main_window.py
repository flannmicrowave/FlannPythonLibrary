from operator import index
import sys
import os

from configparser import ConfigParser
from time import sleep

from qtpy import QtCore, QtWidgets, QtGui

from flann.vi.switch import Switch337
from flann.vi.attenuator import Attenuator024, Attenuator625


class MenuWindow(QtWidgets.QWidget):
    '''Settings window for the 024'''
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Menu")
        self.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\FlannMicrowave.ico"))))
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.setFixedSize(QtCore.QSize(200, 300))

        self.switches = []
        self.switches_names = []
        self.parser = ConfigParser()
        self.parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\imsSwitchSettings.ini")))
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
        self.connectButton.clicked.connect(lambda: self.connect_to_com_switches())
        self.layoutMain.addWidget(self.connectButton)

        self.nameLineEdit = QtWidgets.QTextEdit()
        self.nameLineEdit.setReadOnly(True)  # Read-only
        self.nameLineEdit.setStyleSheet("QTextEdit {background-color:white; color:black; border: 0px;}")
        self.nameLineEdit.setFixedHeight(40)
        self.layoutMain.addWidget(self.nameLineEdit)
        
        self.disconnectButton = QtWidgets.QPushButton("Disconnect")
        self.disconnectButton.clicked.connect(lambda: self.disconnect_from_switches())
        self.layoutMain.addWidget(self.disconnectButton)
        
        self.setLayout(self.layoutMain)

    def connect_to_com_switches(self):
        try:
            switchPortList = self.addressLineEdit.text().split(',')
            for address in switchPortList:
                print(address)
                if address.lower().startswith('com'):
                    switch = Switch337(switch=1,
                                       address=address, 
                                       timeout=float(self.timeoutLineEdit.text()), 
                                       baudrate=int(self.baudRateLineEdit.text()), 
                                       timedelay=float(self.appDelayLineEdit.text()))
                    print(switch.id())
                    self.switches.append(switch)
                    self.switches_names.append(switch.id())
                    
                else:
                    print('ethernet not supported')
            self.nameLineEdit.setText(str(self.switches_names)[1:-1])
            self.update_parser()
        except:
            print('Connection Error')

    def disconnect_from_switches(self):
        if self.switches:
            self.switches = []
            self.switches_names = []
            self.update_parser()
        self.nameLineEdit.clear()

    def update_parser(self):
        new_parser = ConfigParser()
        new_parser.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\imsSwitchSettings.ini")))
        update_file = open(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\imsSwitchSettings.ini")), 'w')
        new_parser['GENERAL']['address'] = str(self.addressLineEdit.text())
        new_parser['GENERAL']['baudrate'] = str(self.baudRateLineEdit.text())
        new_parser['GENERAL']['timeout'] = str(self.timeoutLineEdit.text())
        new_parser.write(update_file)
        update_file.close()


class MainWindow(QtWidgets.QMainWindow):
    '''Switch Counter Main Window'''
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Switch Demo")
        self.setFixedWidth(400)

        self.mWindow = MenuWindow()
        self.config = self.mWindow.config
        self.switches = self.mWindow.switches
        self.switches_names = self.mWindow.switches_names

        self.layoutMain = QtWidgets.QVBoxLayout()

        self.disableButtonGroup = QtWidgets.QButtonGroup()

        '''DEMO'''

        self.timer = QtCore.QTimer(self)  # Timer for demo
        self.timer.timeout.connect(self.running_demo)

        self.demoConfig = ConfigParser()
        self.demoConfig.read(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\imsSwitchSettings.ini")))

        self.attenuator024 = None
        self.attenuator625 = None

        self.demoAttenuationList = [int(i) for i in self.demoConfig['DEMO']['attenuation'].split(',')]
        self.demoAttenuationIndex = 0
        self.demoSwitchBool = False

        '''User Interface'''

        # Layout 1
        self.layout1 = QtWidgets.QHBoxLayout()

        self.menuButton = QtWidgets.QPushButton("Menu", self, checkable=True)
        self.menuButton.setFixedSize(QtCore.QSize(50, 50))
        self.menuButton.setStyleSheet("QPushButton {background-color:rgb(218,233,221); color:black;}")
        self.menuButton.clicked.connect(lambda: self.toggle_menu_window())
        
        self.toggleAllSwitchesButton = QtWidgets.QPushButton("Toggle\nAll")
        self.toggleAllSwitchesButton.setFixedSize(QtCore.QSize(75, 50))
        self.toggleAllSwitchesButton.setStyleSheet("QPushButton {background-color:rgb(218,233,221); color:black;}")
        self.disableButtonGroup.addButton(self.toggleAllSwitchesButton)
        self.toggleAllSwitchesButton.clicked.connect(lambda: self.toggle_all_switches())

        self.whereIsSwitchesButton = QtWidgets.QPushButton("Position?")
        self.whereIsSwitchesButton.setFixedSize(QtCore.QSize(75, 50))
        self.whereIsSwitchesButton.setStyleSheet("QPushButton {background-color:rgb(218,233,221); color:black;}")
        self.whereIsSwitchesButton.clicked.connect(lambda: self.where_are_switches())

        self.connectToAttenuatorButton = QtWidgets.QPushButton("Connect\nAttenuators", self, checkable=True)
        self.connectToAttenuatorButton.setFixedSize(QtCore.QSize(100, 50))
        self.connectToAttenuatorButton.clicked.connect(lambda: self.connect_to_attenuator())
        self.connectToAttenuatorButton.setStyleSheet("""
                                                     QPushButton {background-color:rgb(0,58,34); color:lightgray;}
                                                     QPushButton::hover {background-color:rgb(0,58,34); color:black;}
                                                     """)

        self.demoButton = QtWidgets.QPushButton("Demo", self, checkable=True)
        self.demoButton.setFixedSize(QtCore.QSize(50, 50))
        self.demoButton.setStyleSheet("""
                                      QPushButton {background-color:rgb(0,58,34); color:lightgray;} 
                                      QPushButton::hover {background-color:rgb(0,58,34); color:black;}
                                      """)
        self.demoButton.clicked.connect(lambda: self.demo())

        ## Layout 2
        self.layout2 = QtWidgets.QGridLayout()
        self.switchButtonMap = {}

        # Layout 3
        self.layout3 = QtWidgets.QHBoxLayout()
        
        self.layout3.addWidget(QtWidgets.QLabel("Message:"))
        self.messageLineEdit = QtWidgets.QTextEdit()
        self.messageLineEdit.setStyleSheet("QTextEdit {background-color:white; color:black; border: 0px;}")
        self.messageLineEdit.setFixedHeight(25)
        self.messageLineEdit.setReadOnly(True)  # Read-only

        '''Layout'''

        self.layout1.addWidget(self.menuButton)
        self.layout1.addWidget(self.toggleAllSwitchesButton)
        self.layout1.addWidget(self.whereIsSwitchesButton)
        self.layout1.addWidget(self.connectToAttenuatorButton)
        self.layout1.addWidget(self.demoButton)

        self.layout3.addWidget(self.messageLineEdit)

        self.layoutMain.addLayout(self.layout1)
        self.layoutMain.addLayout(self.layout2)
        self.layoutMain.addLayout(self.layout3)

        self.widgetMain = QtWidgets.QWidget(self)
        self.widgetMain.setAutoFillBackground(True)
        self.widgetMain.setLayout(self.layoutMain)
        self.widgetMain.setStyleSheet("background-color: rgb(132,181,141);")
        self.setCentralWidget(self.widgetMain)
    
    def toggle_menu_window(self):  # Currently this limits the main window interactions due to an inheritance coding error where the self.attenuator does not update when the settings are changed in the menu window
        if self.mWindow.isVisible():
            self.mWindow.hide()
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, True)
            self.show()
            self.switches = self.mWindow.switches
            self.switches_names = self.mWindow.switches_names

            switchButtonLabels = [['Toggle\n1', 'Toggle\n2', 'Toggle\nBoth'],] * len(self.switches)

            for s in range(len(self.switches)):
                switchLabel = QtWidgets.QTextEdit(f'{self.switches_names[s]}')
                switchLabel.setReadOnly(True)  # Read-only
                switchLabel.setStyleSheet("QTextEdit {background-color:white; color:black; border: 0px; border-radius:2px}")
                switchLabel.setFixedSize(QtCore.QSize(100, 40))
                switchLabel.setAlignment(QtCore.Qt.AlignCenter)
                self.layout2.addWidget(switchLabel, s, 0)

            for row, keys in enumerate(switchButtonLabels):
                for col, key in enumerate(keys):
                    self.switchButtonMap[f'{row}'+key] = QtWidgets.QPushButton(key)
                    self.switchButtonMap[f'{row}'+key].setFixedSize(QtCore.QSize(75, 50))
                    self.switchButtonMap[f'{row}'+key].setStyleSheet("QPushButton {background-color:lightgray; color:black;}")
                    if key == 'Toggle\n1':
                        self.switchButtonMap[f'{row}'+key].clicked.connect(lambda _, row=row: self.toggle_selected_switch(row, 1))
                    elif key == 'Toggle\n2':
                        self.switchButtonMap[f'{row}'+key].clicked.connect(lambda _, row=row: self.toggle_selected_switch(row, 2))
                    elif key == 'Toggle\nBoth':
                        self.switchButtonMap[f'{row}'+key].clicked.connect(lambda _, row=row: self.switches[row].toggle_all())
                        self.switchButtonMap[f'{row}'+key].clicked.connect(lambda _, row=row: self.messageLineEdit.setText(f'Toggling {self.switches_names[row]} Switch 1 and 2'))
                    self.layout2.addWidget(self.switchButtonMap[f'{row}'+key], row, col+1)
        else:
            self.mWindow.show()
            self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
            self.show()
            self.remove_switch_buttons()

    def closeEvent(self, event):
        QtWidgets.QApplication.closeAllWindows()

    def toggle_selected_switch(self, switch_driver_number, switch_number):
        if self.switches:
            selected_switch = self.switches[switch_driver_number]
            selected_switch.switch = switch_number
            selected_switch.toggle()
            self.messageLineEdit.setText(f'Toggling {self.switches_names[switch_driver_number]} Switch {switch_number}')
        else:
            self.messageLineEdit.setText('No switches connected.')

    def toggle_all_switches(self):
        if self.switches:
            self.messageLineEdit.setText('Toggling all switches')
            for switch in self.switches:
                switch.toggle_all()
        else:
            self.messageLineEdit.setText('No switches connected.')

    def where_are_switches(self):
        positionList = []
        if self.switches:
            for switch in self.switches:
                switch.switch = 1
                positionList.append(switch.position)
                switch.switch = 2
                positionList.append(switch.position)
            print(positionList)
            pop_up = QtWidgets.QMessageBox(self)
            pop_up.setWindowTitle("Switch Position")
            pop_up.setText(f'Switches positions:\n{'\n'.join(positionList)}')
            pop_up.setStandardButtons(QtWidgets.QMessageBox.Ok)
            pop_up.setIcon(QtWidgets.QMessageBox.Information)
            pop_up.setStyleSheet("QMessageBox {background-color: rgb(132,181,141); color:black;}")
            pop_up.exec()
        else:
            self.messageLineEdit.setText('No switches connected.')

    def remove_switch_buttons(self):
        while self.layout2.count():
            item = self.layout2.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()

    def connect_to_attenuator(self):
        if self.connectToAttenuatorButton.isChecked():
            try:
                if self.attenuator024 is None:
                    self.attenuator024 = Attenuator024(address=self.demoConfig['DEMO024']['address'], 
                                                    timeout=float(self.demoConfig['DEMO024']['timeout']), 
                                                    baudrate=int(self.demoConfig['DEMO024']['baudrate']), 
                                                    timedelay=float(self.demoConfig['DEMO024']['sleep']))
                    print('Attenuator 024 connected')
                if self.attenuator625 is None:
                    self.attenuator625 = Attenuator625(address=self.demoConfig['DEMO625']['address'], 
                                                    tcp_port=int(self.demoConfig['DEMO625']['tcp_port']), 
                                                    timedelay=float(self.demoConfig['DEMO625']['sleep']))
                    print('Attenuator 625 connected')
            except:
                print('Connection Error')
                self.messageLineEdit.setText(f'Connection Error {self.attenuator024} {self.attenuator625} {self.switches}')
                self.connectToAttenuatorButton.setChecked(False)
                return
            self.messageLineEdit.setText('Attenuators connected')
        
        else:
            if self.attenuator024 is not None:
                self.attenuator024.close()
                self.attenuator024 = None
                print('Attenuator 024 disconnected')
            if self.attenuator625 is not None:
                self.attenuator625.close()
                self.attenuator625 = None
                print('Attenuator 625 disconnected')
            self.messageLineEdit.setText('Attenuators disconnected')

    def demo(self):
        if self.demoButton.isChecked():
            self.demoButton.setText("Stop")
            self.start_demo()
        else:
            self.stop_demo()
            self.demoButton.setText("Demo")

    def start_demo(self):
        self.messageLineEdit.setText('Starting demo')

        if any([self.attenuator024 is None, self.attenuator625 is None, not self.switches]):
            self.messageLineEdit.setText(f'Connection Error {self.attenuator024} {self.attenuator625} {self.switches}')
            self.demoButton.setChecked(False)
            self.demoButton.setText("Demo")
            return
        
        self.timer.start(int(self.demoConfig['DEMO']['sleep']))  # Set the timer interval to the sleep time in milliseconds

    def stop_demo(self):
        self.messageLineEdit.setText('Stopping demo')
        self.timer.stop()
        self.messageLineEdit.setText('Demo stopped')

    def running_demo(self):
        print(self.demoSwitchBool)
        self.demoSwitchBool = not self.demoSwitchBool
        if self.demoSwitchBool:
            self.messageLineEdit.setText('Toggling demo switches')
            self.switches[int(self.demoConfig['DEMO']['attenuator_switch_index'])].toggle_all()
        else:
            index = self.demoAttenuationIndex % len(self.demoAttenuationList)
            attenuation = self.demoAttenuationList[index]
            self.messageLineEdit.setText(f'Setting attenuation to {attenuation} dB')
            self.attenuator024.attenuation = attenuation
            self.attenuator625.attenuation = attenuation
            self.demoAttenuationIndex += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__), ".\\FlannMicrowave.ico"))))
    window = MainWindow()
    window.show()

    app.exec()