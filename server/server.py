#! /usr/bin/python3

import socket
import json
import threading
import clientManager
import clientThread
import os
import signal
import time

host = ""
port = 1311

class Server:
    run = True

    def __init__(self):
        print("Initializing server")
        signal.signal(signal.SIGINT, self.sig)
        signal.signal(signal.SIGTERM, self.sig)
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(10)
        self.sock.bind((self.host, self.port))
        print("Listening on ", self.host or "*", ":", self.port)
        print("Starting client manager")
        self.cm = clientManager.ClientManager(self.sock)
        print("Starting client updater")
        self.cu = clientManager.Updater(self.cm).start()
        print("Starting garbage collector")
        self.gc = clientManager.GrabageCollector(self.cm).start()
        print("! SERVER READY")

    def listen(self):
        while self.run: 
            try: 
                data, addr = self.sock.recvfrom(1024)
            except socket.timeout:
                continue
            if data:
                clientThread.ClientThread(data, addr, self.cm).start()
        
        print("Main loop stopped")
        self.exit()
    
    def sig(self, signum, frame):
        if not self.run:
            print("\n! Second signal recieved. Panic exit")
            self.exit(0)
            
        self.run = False
        print("\n")
        if signum == signal.SIGINT:
            print("! Keyboard exit command recieved")
        elif signum == signal.SIGTERM:
            print("! Server terminated")
        print("Waiting for main loop to exit")
        #time.sleep(11)
        #self.exit()
        
    def exit(self, code=0):
        self.sock.close()
        print("Socked closed")
        print("Exitting... code:", code)
        os._exit(0)
        
if __name__ == "__main__":
    Server().listen()
