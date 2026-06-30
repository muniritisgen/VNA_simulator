#pyqt graph kullan direkt
#thread multithreading pyqt nin qthread 
#grafik kaydet png


import sys #only needed for access to command line arguments
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import Qt
import pyqtgraph as pg
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QVBoxLayout,
                              QHBoxLayout, QLabel, QLineEdit, QPushButton,
                              QComboBox, QTextEdit, QFileDialog)
from PyQt5.QtGui import QPixmap
import matplotlib.pyplot as plt
import pyvisa
import time
import numpy as np
import csv


class VNAInterface(QMainWindow):
    def __init__(self): #is the consturctor method, this clock of code tuns automatically the exact miliseconf this windoes is created
        super().__init__() #super looks at the parent we inherited from (qmainwindow) .__init__ tells the parent window to run its own bakground setup code

        self.setWindowTitle("VNA Controller") # we use self to change a setting on our specific window

        self.resize(800,600)

        self.setStyleSheet("""
                            QMainWindow{background-color: #1E1E1E;}
                            QLabel{color:#FFFFFF; font-family: 'Segoe UI', Arial; font-size:12px; font-weight:bold;}
                            QPushButton{background-color: #007ACC; color: white; border-radius: 4px; padding:8px; font-weight:bold;}
                            QPushButton:hover{background-color: #0098FF;}
                            QPushButton:disabled{background-color:#555555; color:#888888;}
                            QComboBox{padding: 5px; border: 1px solid #555555; border-radius: 3px; background-color: #333333; color:white;}
                           """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        #we create a vertical box layout and attach it to our canvar this layout will force anything we pout inside it to stack top to bottom
        main_layout = QVBoxLayout(central_widget)

        self.logo_label = QLabel()
        pixmap = QPixmap("tbtk.jpg")
        self.logo_label.setPixmap(pixmap.scaled(300,120, aspectRatioMode=1))
        

        connection_layout = QHBoxLayout()

        connection_layout.insertWidget(0, self.logo_label, alignment=Qt.AlignLeft)

        self.ip_label = QLabel("VNA IP Address:")

        self.ip_input = QLineEdit("30.1.49.77")

        self.connect_btn = QPushButton("Connect")

        self.connect_btn.clicked.connect(self.connect_to_vna)  #connect_to_vna is the function when we push connect_btn




        connection_layout.addWidget(self.ip_label)
        connection_layout.addWidget(self.ip_input)
        connection_layout.addWidget(self.connect_btn)
        
        self.rf_switch = QPushButton("RF OFF")
        self.rf_switch.setStyleSheet("background-color: red; color: white")
        self.rf_switch.setCheckable(True)
        self.rf_switch.clicked.connect(self.toggle_rf)

        self.sweep_btn = QPushButton("Run Sweep")
        self.sweep_btn.setEnabled(False)

        self.trans_norm_both_btn = QPushButton("Trans Norm Both")
        self.trans_norm_both_btn.setCheckable(True)
        self.trans_norm_both_btn.clicked.connect(self.tran_norm_both)

        self.continuous_btn = QPushButton("Start Continuous Sweep")
        self.continuous_btn.setEnabled(False)
        self.continuous_btn.clicked.connect(self.toggle_continuous)

        self.export_btn = QPushButton("Export Data (CSV)")
        self.export_btn.clicked.connect(self.export_data)

        settings_layout = QHBoxLayout()
        settings_layout = QHBoxLayout()


        self.s_param_dropdown = QComboBox()
        self.s_param_dropdown.addItems(["S11", "S21", "S12", "S22"])

        self.start_freq_input = QLineEdit("500")
        self.stop_freq_input = QLineEdit("1000")
        self.points_input = QLineEdit("201")


        settings_layout.addWidget(QLabel("Measurement:"))
        settings_layout.addWidget(self.s_param_dropdown)
        settings_layout.addWidget(QLabel("Start (MHz):"))
        settings_layout.addWidget(self.start_freq_input)
        settings_layout.addWidget(QLabel("Stop (MHz):"))
        settings_layout.addWidget(self.stop_freq_input)
        settings_layout.addWidget(QLabel("Points:"))
        settings_layout.addWidget(self.points_input)

        
        #wire the sweep button to the new sweep function
        self.sweep_btn.clicked.connect(self.run_sweep)
        self.sweep_timer = QTimer()
        self.sweep_timer.timeout.connect(self.run_sweep)
        
        main_layout.addLayout(connection_layout)
        main_layout.addLayout(settings_layout)
        
        main2_layout = QHBoxLayout()
        main2_layout.addWidget(self.sweep_btn)
        main2_layout.addWidget(self.rf_switch)
        main_layout.addLayout(main2_layout)

        
        main3_layout = QHBoxLayout()
        main3_layout.addWidget(self.continuous_btn)
        main3_layout.addWidget(self.export_btn)
        main_layout.addLayout(main3_layout)

        main4_layout = QHBoxLayout()
        main4_layout.addWidget(self.trans_norm_both_btn)
        main_layout.addLayout(main4_layout)

        plots_layout = QHBoxLayout()

        self.mag_plot = pg.PlotWidget(title = "Magnitude(dB)")
        self.mag_plot.setBackground('k')
        self.mag_plot.getAxis('bottom').setPen('w')
        self.mag_plot.getAxis('left').setPen('w')
        self.mag_plot.showGrid(x=True, y=True)
        self.mag_plot.setLabel('bottom', 'Frequency', units='Hz', color='k')

        self.phase_plot = pg.PlotWidget(title = "Phase (Degrees)")
        self.phase_plot.setBackground('k')
        self.phase_plot.getAxis('bottom').setPen('w')
        self.phase_plot.getAxis('left').setPen('w')
        self.phase_plot.showGrid(x=True, y=True)
        self.phase_plot.setLabel('bottom', 'Frequency', units = 'Hz', color='k')

        plots_layout.addWidget(self.mag_plot)
        plots_layout.addWidget(self.phase_plot)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setStyleSheet("background-color: black; color: #00FF00; font-family: Consolas; font-size: 12px;")
        self.log_console.setMaximumHeight(150)

        main_layout.addLayout(plots_layout)
        main_layout.addWidget(self.log_console)

        main_layout.setStretch(4,1)



        self.vna = None


    def log(self,message):
        self.log_console.append(message)
        print(message)

    def connect_to_vna(self):
        ip_address = self.ip_input.text()
        
        visa_address = f"TCPIP0::{ip_address}::5025::SOCKET"
        
        self.log(f"Attempting to connect to : {ip_address}")
        self.log(f"Attempting hardware connection to : {visa_address}")
        

        ###################################################




        try:
            rm = pyvisa.ResourceManager()

            self.vna = rm.open_resource(visa_address)

            self.vna.read_termination = '\n'
            self.vna.write_termination = '\n'
            self.vna.timeout = 20000

            self.log("--- Connecting to VNA ---")

            idn = self.vna.query("*IDN?")
            self.log(f"Hardware Detected :{idn}")
            #####################################################


            
            #unlock the sweep button if connection is succesful
            self.sweep_btn.setEnabled(True)
            self.continuous_btn.setEnabled(True)
            self.connect_btn.setText("Connected")
            self.connect_btn.setStyleSheet("background-color: lightgreen")
        except Exception as e:
            self.log(f"Connection failed: {e}")

        self.vna.write("OUTP OFF")

    def run_sweep(self):
        if not self.vna:
            self.log("Nor connected to VNA!")
            return
        
        CMD_START_FREQ = ":SENS:FREQ:START"
        CMD_STOP_FREQ = ":SENS:FREQ:STOP"
        CMD_POINTS = ":SENS:SWE:POIN"
        CMD_READ_DATA = ":CALC:DATA? SDATA"

        try:
            start_mhz = float(self.start_freq_input.text())
            stop_mhz = float(self.stop_freq_input.text())
            points = int(self.points_input.text())
        except ValueError:
            self.log("Error: Please enter valid numbers for frequencies and points.")
            return

        selected_s_param = self.s_param_dropdown.currentText()
        self.log(f"Measuring {selected_s_param}")

        start_hz = start_mhz * 1e6
        stop_hz = stop_mhz * 1e6

        self.vna.clear()##upd
        self.vna.write("*CLS")##upd

        self.log(f"\n---- Configurating VNA for {selected_s_param}---")

        self.vna.write(f"CALC:PAR:MEAS 'Trc1', '{selected_s_param}'")


        self.log(f"Setting Start Freq to {start_hz}")
        self.vna.write(f"{CMD_START_FREQ} {start_hz}")
        #time.sleep(0.5)

        self.log(f"Setting Stop Freq to {stop_hz}")
        self.vna.write(f"{CMD_STOP_FREQ} {stop_hz}")
        #time.sleep(0.5)

        self.log(f"Setting Sweep Points to {points}")
        self.vna.write(f"{CMD_POINTS} {points}")
        #time.sleep(1)

        self.vna.write("TRIG:SOUR IMM")
        self.vna.write("INIT:CONT OFF")
        self.vna.query(":INIT1:IMM; *OPC?")



        self.log("\n---Fetching Trace Data ---")
        raw_data = self.vna.query(f"{CMD_READ_DATA}")


        data_list = raw_data.split(',')
        self.real = np.array([float(x) for i, x in enumerate(data_list) if i%2==0])
        self.imag = np.array([float(x) for i, x in enumerate(data_list) if i%2 != 0])
        
        self.linear_mag = np.sqrt(self.real**2 + self.imag**2)
        self.mags_db = 20 * np.log10(self.linear_mag + 1e-12) #a microscopic line added so numpy would not crashes

        self.complex_data = self.real + 1j * self.imag
        self.phases_deg = np.angle(self.complex_data, deg=True)

        self.freqs_hz = np.linspace(start_hz, stop_hz, points)



        self.mag_plot.clear()
        self.mag_plot.plot(self.freqs_hz, self.mags_db, pen=pg.mkPen(color='r', width = 2))
        
        self.phase_plot.clear()
        self.phase_plot.plot(self.freqs_hz, self.phases_deg, pen=pg.mkPen(color='b', width = 2))
        
        self.log("Plot Updated")

    def toggle_rf(self):
        if not self.vna:
            self.log("Connect to VNA first")
            return
        
        if self.rf_switch.isChecked():
            self.vna.write("OUTP ON") #SCPI command to enable RF output
            self.rf_switch.setText("RF ON")
            self.rf_switch.setStyleSheet("background-color: green; color: white;")
            self.log("RF Power: ENABLED")
        else:
            self.vna.write("OUTP OFF") 
            self.rf_switch.setText("RF OFF")
            self.rf_switch.setStyleSheet("background-color: red; color: white;")
            self.log("RF Power: DISABLED")
    def toggle_continuous(self):
        if self.sweep_timer.isActive():
            self.sweep_timer.stop()
            self.continuous_btn.setText("Start Continuous Sweep")
            self.continuous_btn.setStyleSheet("")

            if self.vna:
                self.vna.write("INIT1:CONT ON")
            self.log("Continuous Sweep Stopped.")
        else:
            self.sweep_timer.start(3000)
            self.continuous_btn.setText("Stop Sweeping")
            self.continuous_btn.setStyleSheet("backgroun-color: lightcoral ; color: white;")
            self.log("Continuous Sweep Started.")
    def tran_norm_both(self):
        if not self.vna:
            self.log("Connect to VNA first")
            self.trans_norm_both_btn.setChecked(False)
            return
        if self.trans_norm_both_btn.isChecked():
            self.log("\n---Startin Trans Norm Both Calibration")

            self.log("Clearing VNA memory buffers and error queues")
            self.vna.write("*CLS")
            self.vna.write("INIT1:CONT OFF")
            time.sleep(0.2)

            self.vna.write("SENS1:CORR:COLL:METH:DEF 'AutoCal', FRTRans, 1, 2" )
            self.log("Measuring through connection")
            self.vna.query("SENS1:CORR:COLL:ACQ:SEL THRough, 1, 2; *OPC?")

            self.log("Applying Correction Data...")

            self.vna.query("SENS1:CORR:COLL:SAVE:SEL; *OPC?")

            self.trans_norm_both_btn.setText("Calibrated")
            self.trans_norm_both_btn.setStyleSheet("background-color: lightgreen; color:black;")
            self.log("Calibration Completed")

            if not self.sweep_timer.isActive():
                self.vna.write("INIT1:CONT ON")

        else:
            self.vna.write("SENS1:CORR:STAT OFF")
            self.trans_norm_both_btn.setText("Trans Norm Both")
            self.trans_norm_both_btn.setStyleSheet("")
            self.log("Calibration turned OFF. Showing raw data.")

    def export_data(self):
        if not hasattr(self,'mags_db') or not hasattr(self, 'phases_deg'):
            self.log("Error: No data to export! Run a sweep first.")
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save VNA Data", "vna_sweep_data.csv", "CSV Files (*.csv);;All Files (*)", options=options)

        if file_path:
            try:
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)

                    writer.writerow(["Data Point", "Magnitude", "Phase"])

                    for i in range(len(self.mags_db)):
                        writer.writerow([self.freqs_hz[i], self.mags_db[i], self.phases_deg[i]])

                print(f"SUCCES: The data is saved to {file_path}")

            except Exception as e:
                print(f"Error: Could not save because {e}")
if __name__ == "__main__":

    app = QApplication(sys.argv)
    #you need one and only one qapplication instance per application
    #pass in sys.argv to allow command line arguments for your app
    #If you know you won't use command line arguments QApplication([]) works too

    window = VNAInterface()
    window.show() #important !! windows are hidden by default

    sys.exit(app.exec()) #sys.exit is not mandatory but it ensures when we close the windoe python actually shuts down
