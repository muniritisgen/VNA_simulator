#pyqt graph kullan direkt

import sys #only needed for access to command line arguments
import PyQt5.QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton)
import matplotlib.pyplot as plt
import pyvisa
import time


class VNAInterface(QMainWindow):
    def __init__(self): #is the consturctor method, this clock of code tuns automatically the exact miliseconf this windoes is created
        super().__init__() #super looks at the parent we inherited from (qmainwindow) .__init__ tells the parent window to run its own bakground setup code

        self.setWindowTitle("VNA Controller") # we use self to change a setting on our specific window

        self.resize(800,600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #we create a vertical box layout and attach it to our canvar this layout will force anything we pout inside it to stack top to bottom
        main_layout = QVBoxLayout(central_widget)

        connection_layout = QHBoxLayout()

        self.ip_label = QLabel("VNA IP Address:")

        self.ip_input = QLineEdit("127.0.0.1")

        self.connect_btn = QPushButton("Connect")

        self.connect_btn.clicked.connect(self.connect_to_vna)  #connect_to_vna is the function when we push connect_btn




        connection_layout.addWidget(self.ip_label)
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)   

        self.sweep_btn = QPushButton("Run Sweep")
        self.sweep_btn.setEnabled(False)

        #placeholder for future plot
        self.graph_placeholder = QLabel("Matplotlib Graph")

        self.graph_placeholder.setStyleSheet("background-color: lightgray; font-size: 20px;")


        main_layout.addLayout(connection_layout)
        main_layout.addWidget(self.sweep_btn)



        self.plot_widget = pg.PlotWidget()

        self.plot_widget.setBackground('w')
        self.plot_widget.setTitle("VNA Sweep Data", color="k", size="15pt")
        self.plot_widget.setLabel('left', 'Magnitude', units='dB', color='k')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz', color='k')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.addLegend()

        main_layout.addWidget(self.plot_widget)
        main_layout.setStretch(2,1)

        mags = [float(x) for i, x in enumerate(data_list) if i%2==0]
        phases = [float(x) for i, x in enumerate(data_list) if i%2 != 0]
        data_list = raw_data.split(',')
        self.plot_widget.plot(phases, mags, name="S11", pen=pg.mkPen(color='b', width = 2))


    def connect_to_vna(self):
        ip_address = self.ip_input.text()
        
        visa_address = f"TCPIP0::{ip_address}::5025::SOCKET"
        
        print(f"Attempting to connect to : {ip_address}")
        print(f"Attempting hardware connection to : {visa_address}")
        

        ###################################################

        CMD_START_FREQ = ":SENS:FREQ:START"
        CMD_STOP_FREQ = ":SENS:FREQ:STOP"
        CMD_POINTS = ":SENS:SWE:POIN"
        CMD_READ_DATA = ":CALC:DATA? SDATA"

        rm = pyvisa.ResourceManager()

        vna = rm.open_resource(visa_address)

        vna.read_termination = '\n'
        vna.write_termination = '\n'
        self.vna_timeout = 5000

        print("--- Connecting to VNA ---")

        idn = vna.query("*IDN?")
        print(f"Hardware Detected :{idn}")


        print("\n--- Configurating VNA ---")

        print("Setting Start Freq to 500 MHz...")
        vna.write(f"{CMD_START_FREQ} 500")
        time.sleep(0.5)

        print("Setting Sweep Points to 5...")
        vna.write(f"{CMD_POINTS} 201")
        time.sleep(0.5)

        print("\n--- Fetching Trace Data ---")

        raw_data = vna.query(f"{CMD_READ_DATA}")
        print(f"Raw String Receiver: \n{raw_data}")

        vna.close()







        #####################################################


        
        #unlock the sweep button if connection is succesful
        self.sweep_btn.setEnabled(True)
        self.connect_btn.setText(Connected)
        self.connect_btn.setStyleSheet("background-color: lightgreen")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    #you need one and only one qapplication instance per application
    #pass in sys.argv to allow command line arguments for your app
    #If you know you won't use command line arguments QApplication([]) works too

    window = VNAInterface()
    window.show() #important !! windows are hidden by default

    sys.exit(app.exec()) #sys.exit is not mandatory but it ensures when we close the windoe python actually shuts down
