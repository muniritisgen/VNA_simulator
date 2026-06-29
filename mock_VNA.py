import socket

start_freq_mhz = 100.0
stop_freq_mhz = 3000.0
points = 201



def process_scpi_command(command):
    global start_freq_mhz,stop_freq_mhz,points

    cmd = command.strip().upper()
    #strip remowes hidden newline chars. upper makes it case sensitive

    if cmd == "*IDN?":
        return "munirvna, mun2004, series21, M.1.0\n"
    
    elif cmd.startswith(":SENS:FREQ:START"):
        start_freq_mhz = float(cmd.split()[1])
        #split grabs the number after the space
        return None
    
    elif cmd.startswith(":SENS:SWE:POIN"):
        points = int(cmd.split()[1])
        return None
    
    elif cmd == ":CALC:DATA? SDATA":
        #asks the VNA to send back the actual measured RF data
        trace_data = []

        for i in range(points):
            mock_db = -5 -(i%16)*4
            mock_phase = (i*4) - 90.0
            if mock_phase > 180.0: mock_phase -=360.0
            trace_data.append(f"{mock_db: .3f}, {mock_phase: .3f}")
        return ",".join(trace_data) + "\n"
    return None

def run_mock_vna():
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #AF is address family, INET:IPv4
    #SOCK_STREAM means TCP (transmission control protocol)

    server.bind(('127.0.0.1',5025))
    server.listen(1)

    print(f"Mock VNA is running and listenning on port 5025...")

    #infinite loop to keep the server running all the time
    while True:
        conn, addr = server.accept()
        print(f"\n[+] PyVISA connected from {addr}")

        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                print(f"Received:{data.strip()}")

                response = process_scpi_command(data)

                if response:
                    conn.sendall(response.encode("utf-8"))

            except ConnectionResetError:
                break
        print("[-] PyVISA Disconnected")
        conn.close()

if __name__ == "__main__":
    run_mock_vna()