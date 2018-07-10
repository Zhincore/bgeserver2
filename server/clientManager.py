import socket
import json
import threading
import time

class ClientManager:
    clients = {}
    clientsLock = threading.Lock()
    data = {}
    dataLock = threading.Lock()
    cid = 0

    def __init__(self, sock):
        self.sock = sock
        print("Client manager ready")        
        
    def newClient(self, addr):
        if self.clientsLock.acquire():
            cid = self.cid
            self.cid = self.cid+1
            self.clients[addr] = {"lastAccess": time.time(), "id": cid}
            print("+ New client added", addr, "id:", cid)
            self.clientsLock.release()
            return (True, {"id": cid})
        else:
            return (False,"internal error")
        
    def removeClient(self, addr, reason):
        if self.clientsLock.acquire():
            del self.clients[addr]
            print("- Client", addr, "removed: "+reason)
            self.clientsLock.release()
            
    def clientAccess(self, addr):
        self.clientsLock.acquire()
        if self.clients[addr]:
            self.clients[addr]["lastAccess"] = time.time()
            self.clientsLock.release()
            return True
        else:
            self.clientsLock.release()
            return False
    
    def updateData(self, newData, addr):
        if self.clientAccess(addr):
            if self.dataLock.acquire():
                for item in newData:
                    self.data[item] = newData[item]
                self.dataLock.release()
                return (True,"ok")
            else:
                return (False,"internal error")
        else:
            return (False,"not registered")
            
        
class GrabageCollector(threading.Thread):
    wait = 60
    timeout = 10

    def __init__(self, ClientManager):
        self.cm = ClientManager
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            time.sleep(self.wait)
            self.collect()
            
    def collect(self):
        timedout = []
        if self.cm.clientsLock.acquire():
            #print("Collecting garbage...")
            for addr in self.cm.clients:
                client = self.cm.clients[addr]
                if(time.time() - client["lastAccess"]) >= self.timeout:
                    timedout.append(addr)
            self.cm.clientsLock.release()
            
            for rem in timedout:
                self.cm.removeClient(rem, "timeout")
                
class Updater(threading.Thread):
    wait = 0.01
    
    def __init__(self, ClientManager):
        self.cm = ClientManager
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            time.sleep(self.wait)
            if self.cm.dataLock.acquire() and self.cm.clientsLock.acquire():
                for client in self.cm.clients:
                    self.cm.sock.sendto((json.dumps(["update", self.cm.data])).encode("utf-8"), client)
                    #print((json.dumps(["update", self.cm.data])).encode("utf-8"), client)
                self.cm.clientsLock.release()
                self.cm.dataLock.release()
                
