import socket
import json

HOST = "192.168.2.100"
PORT = 8001

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print(f"Servidor escuchando en el puerto {PORT}")

while True:
    conn, addr = server.accept()
    print(f"Conexión desde {addr}")
    data = conn.recv(1024).decode()
    try:
        mensaje = json.loads(data)
        print("Recibido:", mensaje)
    except:
        print("Error al interpretar:", data)
    conn.close()
