#Server Settings
PORT = 80
MAX_CONNS = 10


import socket
from threading import *
import time
import hashlib
import os
import zlib

def timeStamp():
    return time.time()

class LoginManager():
    def __init__(self,loginFile,userFile):
        self.loginFile = loginFile
        self.userFile = userFile
        self.loginFileFlag = False
        self.loginData = self.loadLoginData()
        self.userData = self.loadUserData()
    def hash_algorithm(self,password):
        """Obtain a hexadecimal digest for the password provided"""
        return hashlib.sha224(password.encode()).hexdigest()
    def clearLogins(self):
        """Reset the login file"""
        with open(self.loginFile,'w') as file:
            file.write('{}')
        self.loginData = {}
    def loadLoginData(self):
        """Returns data in the login file"""
        with open(self.loginFile,'r') as file:
            data = eval(file.read())
        return data
    def saveLoginData(self):
        """Saves the login data to file"""
        with open(self.loginFile,'w') as file:
            file.write(str(self.loginData))
    def login(self,username,password):
        """Returns True if passwords match, and False if they do not or login does not exist"""
        if username in list(self.loginData.keys()):
            if self.loginData[username] == self.hash_algorithm(password):
                return True
            else:
                return False
        else:
            return False
    def addLogin(self,username,password):
        """Add a new login and password combination (automatically hashes)"""
        if username in list(self.loginData.keys()):
            return False
        else:
            self.loginData[username] = self.hash_algorithm(password)
            return True
    def deleteLogin(self,username):
        """Deletes the login"""
        del self.loginData[username]
    def getHashes(self):
        """Returns dictionary of all registered logins and their hashes"""
        return self.loginData
    def getUsers(self):
        """Returns list of all registered users (from the login file)"""
        return list(self.loginData.keys())
    def clearUserData(self):
        """Resets the user data save file"""
        with open(self.userFile,'w') as file:
            file.write('{}')
    def loadUserData(self):
        """Returns the contents of the user data save file"""
        with open(self.userFile,'r') as file:
            return eval(file.read())
    def saveUserData(self):
        """Saves to the user data save file"""
        with open(self.userFile,'w') as file:
            file.write(str(self.userData))
    def addUser(self,username):
        """Adds a new user, and gives them an empty dictionary"""
        if username not in list(self.userData.keys()):
            self.userData[username] = {'map':'start','x':0,'y':0}
            return True
        else:
            return False
    def deleteUser(self,username):
        """Removes a user and their user data"""
        if username in list(self.userData.keys()):
            del self.userData[username]

class ServerManager():
    def __init__(self,port,max_conns):
        self.port, self.max_conns = port, max_conns
        self.ip = socket.gethostbyname(socket.gethostname())
        print('Server ip\n',self.ip,':',self.port,sep='')
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.conns = []
        try:
            self.s.bind((self.ip,self.port))
        except:
            print('[!] Socket failed to bind port')
        self.s.listen(self.max_conns)
        print('Server launched successfully')
    def send(self,conn,header,data):
        """Send data to one connection"""
        try:
            conn.sendall(self.packet(header,data))
        except:
            return False
    def connection(self,conn,addr):
        """To be called as separate threads, keeps track of one connection"""
        loginCheck = False
        while loginCheck == False:
            try:
                msg = conn.recv(2**16)
            except:
                print('Connection lost with',addr[0],':',addr[1])
                conn.close()
                break
            try:
                msg = eval(msg.decode())
                if msg['header'] == 'login':
                    un,pw = msg['data']
                    if loginManager.login(un,pw) == True:
                        loginCheck = True
                        print(addr[0],':',addr[1],'authenticated')
                        self.send(conn,'login',True)
                    else:
                        self.send(conn,'login',False)
            except:
                print('Login Error')
        if loginCheck == True:
            entity = worldManager.addObj(loginManager.userData[un])
            while True:#RECV LOOP
                try:
                    msg = eval(conn.recv(2**16).decode())
                    print(msg)
                    if msg['header'] == 'load':
                        self.send(conn,'map',worldManager.getMapData(entity.data['map']))
                        self.send(conn,'entity',worldManager.getEntitiesInMap(entity.data['map']))
                except:
                    conn.close()
                    print('[!] Connection with',addr,'Terminated')
                    break
    def mainloop(self):
        """Accepts connections and assigns new threads to each"""
        while True:
            conn, addr = self.s.accept()
            self.conns.append(conn)
            print('Connected with {0}:{1}'.format(addr[0],str(addr[1])))
            Thread(target=self.connection, args=(conn,addr,)).start()
    def packet(self,header,data):
        """Puts data into format ready for sending"""
        return zlib.compress(str({'header':header,'time':timeStamp(),'data':data}).encode())
##        return str({'header':header,'time':timeStamp(),'data':data}).encode()
    def broadcast(self,header,data):
        """Send data to all connections"""
        for c in self.conns:
            self.send(c,header,data)

class WorldManager():
    def __init__(self):
        self.objs = {}
        self.maps = []
        self.UUID = 0
        self.allMapData = {}
        for file in os.listdir():
            if file.endswith('.map'):
                self.maps.append(file[0:-4])
                print(file[0:-4])
        for m in self.maps:
            self.allMapData[m] = self.loadMap(m)
    def addObj(self,data):
        """Add an Entity() to keep track of"""
        self.objs[self.UUID] = Entity(self.UUID,data)
        self.UUID += 1
        return self.objs[self.UUID-1]
    def loadMap(self,mapname):
        """Load a map from a file"""
        with open(mapname+'.map','r') as file:
            mapdata = file.read()
        return eval(mapdata)
    def getMapData(self,mapname):
        return self.allMapData[mapname]
    def getEntitiesInMap(self,mapname):
        entities = []
        for e in self.objs:
            if self.objs[e].data['map'] == mapname:
                entities.append([self.objs[e].UUID,self.objs[e].data])
        return entities

class Entity():
    def __init__(self,UUID,data,name=None):#Name is only for player Entities
        self.UUID = UUID
        #Default Stats
        self.data = {'map':'start','x':0,'y':0,'moveSpeed':1,'abilities':[],'xp':0,'gold':0,'jumpHeight':2,'sprite':'texture_default_character_new.gif'}
        #Overwrite with loaded data
        for k in data.keys():
            self.data[k] = data[k]
    def initClient(self):
        """Returns the complete data for the client to use to set up their own copy"""
        return {'UUID':self.UUID,'data':self.data}
    def move(self,x,y):
        """Moves the Entity, after performing validation checks"""
        if (x**2 + y**2)**.5 <= self.data['moveSpeed']:
            target = self.data['x']+x,self.data['y']+y
            try:
                height_diff = worldManager.allMapData[self.data['map']][self.data['x'],self.data['y']][0] - worldManager.allMapData[self.data['map']][self.target[0],self.target[1]][0]
                if abs(height_diff) <= self.data['jumpHeight']:#Cannot go up or down by a height more than two
                    self.data['x'] = targetx
                    self.data['y'] = targety
                    self.data['z'] = worldManager.allMapData[self.data['map']][0]
            except:#Trying to walk off the map will cause an index error
                pass
    def save(self):
        loginManager.userData[self.name] = self.data



#Create the login manager
loginManager = LoginManager('login_hashes.txt','user_data.txt')

#Create the worldManager
worldManager = WorldManager()

#Setup the Server
socketServer = ServerManager(PORT,MAX_CONNS)

#Launch Server
socketServer.mainloop()



