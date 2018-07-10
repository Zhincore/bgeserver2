import socket
import json
import threading
import bge
import sys

## CONFIG
host = ""
server = ""
port = 1311 # server port

## BGE GLOBALS
scen = bge.logic.getCurrentScene()
cont = bge.logic.getCurrentController()
own = cont.owner

## REMEMBERED GLOBALS
own["init"] = False
own["id"] = None
own["port"] = None # our port
own["data"] = {}
own["dataLock"] = threading.Lock()
own["sock"] = None
own["syncObjs"] = {}

class Main:
    def __init__(self):
        if not own["init"]:
            Listener().start()
        else:   
            if own["id"] != None:
                Sender().send()
                Setter().set()
       
           
        
        
class Listener(threading.Thread):
    def __init__(self):
        self.id = None
        self.host = host or "" # get host
        self.port = own["port"] or 0 # get our port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # prepare socket
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        own["sock"] = self.sock
        own["init"] = True
        
        threading.Thread.__init__(self) #init thread
    
    def run(self):
        sock = self.sock
        sock.bind((self.host, self.port))
        self.port = sock.getsockname()[1] # redefine port in case we got it from system
        own["port"] = self.port
        Sender("register").register()
        print("Waiting for data on ", self.host or "*", ":", self.port)
        
        while True:
            data, addr = sock.recvfrom(4096)
            self.process(data)
        
    def process(self, input):
        if input:
            dataRaw = input.decode("utf-8").strip("\r").strip("\n")
            try:
                data = json.loads(dataRaw)
            except:
                raise Exception("Could not parse recieved data")
            
            #print(data)
            
            if own["id"] == None: # expect registration
                if data[0] == True and data[1]["id"] != None:
                    self.id = data[1]["id"]
                    print("Successfuly registered with id", self.id)
                    own["id"] = self.id
            elif data[0] != True and data[0] != False: 
                if data[0] == "update":  
                    if own["dataLock"].acquire(False):
                        own["data"] = data[1]
                        own["dataLock"].release()
                
class Sender:
    def __init__(self, typ="update"):   
        self.host = server or "" # get target host
        self.port = port # get server port
        self.sock = own["sock"]
        self.typ = typ
        self.reg = (json.dumps(["register", own["port"]])).encode("utf-8")
        
    def send(self):
        self.data = self.getData()
        self.sock.sendto(self.data, (self.host, self.port))
        
    def getData(self):
        if own["dataLock"].acquire():
            data = [self.typ, Getter().getData()]
            
            try:
                output = (json.dumps(data)).encode("utf-8")
            except:
                raise Exception("Could not parse own data")
                
            own["dataLock"].release()
            return output
            
    def register(self):
        print("Registering to server at ", self.host or "localhost", ":", self.port)
        self.sock.sendto(self.reg, (self.host, self.port))
        
class Getter:
    def getData(self):
        data = {}
        
        pos = scen.objects["Player"].worldPosition
        rot = scen.objects["Player"].worldOrientation
        
        data["id"] = own["id"]
        data["pos"] = [
            pos.x,
            pos.y,
            pos.z
        ]
        data["rot"] = [
            [rot[0].x, rot[0].y, rot[0].z],
            [rot[1].x, rot[1].y, rot[1].z],
            [rot[2].x, rot[2].y, rot[2].z]
        ]
        
        return {data["id"]: data}

class Setter:
    def set(self):
        if own["dataLock"].acquire(False):
            data = own["data"]
            own["dataLock"].release()
            
            for name in data:
                obj = data[name]
                if str(name) != str(own["id"]):
                    if not "Player"+name in own["syncObjs"]:
                        newObj = scen.addObject("PlayerTemplate", "Spawn")
                        own["syncObjs"]["Player"+name] = newObj.name
                        
                    scen.objects[own["syncObjs"]["Player"+name]].worldPosition = obj["pos"]
                    scen.objects[own["syncObjs"]["Player"+name]].worldOrientation = obj["rot"]
                        
        
