import time
import socket


host = 'localhost'
port = 42068
user = 'test'
passwd = 'test'
message = 'msg|test - LOGGING IN!!'

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
    stream.connect((host, port))
    print(f"Connected to {host}:{port}")
    stream.send(f"{user}:{passwd}".encode())
    print(f"Sent Login Request {user}:{passwd}")
    stream.send("msg|test - test".encode())
    print(f"Sent:msg|test - test")

    time.sleep(0.01)

    data = stream.recv(1024).decode()

    if data:
        print(data)

print(f"Concluded Test of Ruckus Server [{host}:{port}] {user}:{passwd}")

