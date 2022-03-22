import time
import socket

host = 'localhost'
# host = 'ruckusist.com'
port = 42069
user = 'RUCKUS NATION'
passwd = 'test'
message = f'chat|open|LOGGING IN!!'

stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
stream.connect((host, port))
print(f"Connected to {host}:{port}")
stream.send(f"{user}:{passwd}".encode())
print(f"Sent Login Request {user}:{passwd}")
data = stream.recv(1024).decode()
print(data)
time.sleep(1)
stream.send(message.encode())
print(f"Sent: {message}")

time.sleep(0.01)

data = stream.recv(1024).decode()

if data:
    print(data)

print(f"Concluded Test of Ruckus Server [{host}:{port}] {user}:{passwd}")