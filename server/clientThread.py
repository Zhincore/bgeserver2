import socket
import json
import threading

class ClientThread(threading.Thread):
    def __init__(self, data, addr, cm):
        self.data = data
        self.addr = addr
        self.cm = cm
        self.msg = self.getMsg(self.data)
    
        threading.Thread.__init__(self) #init thread
        
    def run(self):
        response = False
        answer = "???"
    
        if self.msg[0] == "register":
            response,answer = self.cm.newClient(self.addr)
        elif self.msg[0] == "update":
            response,answer = self.cm.updateData(self.msg[1], self.addr)
        else:
            print("* Unknown operation:", self.msg)
        
        data = self.getData([response, answer])
        
        self.cm.sock.sendto(data, self.addr)            
    
    def getMsg(self, data):
        if data:
            msgRaw = data.decode("utf-8").strip("\r").strip("\n")
            try:
                msg = json.loads(msgRaw)
            except:
                raise Exception("Could not parse recieved data")
        else:
            msg = ""
            
        return msg
        
    def getData(self, msg):
        if msg:
            try:
                dataRaw = json.dumps(msg)
            except:
                raise Exception("Could not parse own data")
            data = dataRaw.encode("utf-8") # (json.dumps(msg)).encode("utf-8")
        else:
            data = bytes([0])
        
        return data
