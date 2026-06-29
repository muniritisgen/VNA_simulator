import pyvisa
import time

import matplotlib.pyplot as plt


CMD_START_FREQ = ":SENS:FREQ:START"
CMD_STOP_FREQ = ":SENS:FREQ:STOP"
CMD_POINTS = ":SENS:SWE:POIN"
CMD_READ_DATA = ":CALC:DATA? SDATA"

def run_tests():
    rm = pyvisa.ResourceManager()

    vna = rm.open_resource("TCPIP0::127.0.0.1::5025::SOCKET")

    vna.read_termination = '\n'
    vna.write_termination = '\n'

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

    data_list = raw_data.split(',')

    #exrtach magnitudes, notice that at the output, odd numbers are magnitudes and even indicies are the phases
    mags = [float(x) for i, x in enumerate(data_list) if i%2==0]
    phases = [float(x) for i, x in enumerate(data_list) if i%2 != 0]
    fig, ax1 = plt.subplots()

    ax1.plot(mags, 'b-', label = 'Magnitude (dB)') #b- : blue
    ax1.set_xlabel('points')
    ax1.set_ylabel('Magnitude (dB)', color = 'b')

    ax2 = ax1.twinx() #this allows us to plot two different units on the same graph
    ax2.plot(phases, 'r--', label = 'Phase (deg)')
    ax2.set_ylabel('Phase (Deg)', color = 'r')
    plt.title("Mock  VNA Plot")

    plt.show()


if __name__ == "__main__":
     run_tests()