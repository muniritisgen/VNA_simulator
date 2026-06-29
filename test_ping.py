import socket
print("Attempting to bypass PyVISA and connect directly")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5025))

    print("Connection succesful! Sending *IDN? command...")
    s.sendall(b"*IDN?\n")

    response = s.recv(1024).decode('utf-8')
    print(f"Server Responded: {response}")

    s.close()

except Exception as e:
    print(f"CRITICAL FAILIURE: {e}")