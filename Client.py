###Settings
#Host
IP = '91.125.115.127:80'
#Login Information
username = 'Admin'
password = ':::::'
mode = 'edit'#'play' or 'edit' (for making maps)




###Code
WIDTH = 640
HEIGHT = 640
GRIDSPACING = 20
##HOST = input('Host: ')

import socket
import tkinter
import threading
import time
import hashlib
import os
import math
import random
import zlib
version = 1

#Basic GUI Class
class Window():
    def __init__(self):
        self.root = tkinter.Tk()
        self.root.tk_setPalette('#000000')
        self.root.title('Gathering Storm III Version '+str(version))
    def mainloop(self):
        self.root.mainloop()


#Colour manipulation
class Graphics():
    def __init__(self):
        pass
    def col(self,rgb):#Converts (r,g,b) tuple to a hexadecimal format #rrggbb
        r,g,b = rgb
        out = '#'
        for c in [r,g,b]:
            c = abs(int(c))%256
            out += ('0'+str(hex(c)[2:]))[-2:]
        return out
    def shade(self,rgb,magnitude):#Shades a (r,g,b) tuple by magnitude
        r = int(r*magnitude)
        g = int(g*magnitude)
        b = int(b*magnitude)
        if r > 255:
            r = 255
        if g > 255:
            g = 255
        if b > 255:
            b = 255
        return (r,g,b)

#Create Graphics() object for later Graphics Utility
g = Graphics()




class ClientManager():
    def __init__(self,IP):
        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host,self.port = IP.split(':')
        self.port = int(self.port)
        self.s.connect((self.host,self.port))
    def timeStamp(self):
        return time.time()
    def send(self,header,data):
        self.s.sendall(str({'header':header,'data':data,'time':self.timeStamp()}).encode())
    def receive(self):
        msg = 'None'
        while True:
            try:
                msg = self.s.recv(2**30)
                msg = zlib.decompress(msg)
                msg = eval(msg.decode())
                print('[START|||',msg,'|||END]')
                if msg['header'] == 'update':
                    gamestate = msg['data']
                elif msg['header'] == 'login':
                    if msg['data'] == True:
                        print('Authentication Successful')
                        self.send('load',True)
                    else:
                        print('Authentication Failed')
                elif msg['header'] == 'map':
                    game.renderMap(msg['data'])
##                elif msg['header'] == 'entity':
##                    worldManager.
            except:
                print('[!] Invalid Server Request [!]')
                print('Please show this error report\nto the server administrator:')
                print(msg)
    def sendReq(self,event):
        if event.keysym in ['w','a','s','d']:
            self.send('move',{'w':(0,1),'a':(-1,0),'s':(0,-1),'d':(1,0)}[event.keysym])

class GameManager():#Deals with game's graphics
    def __init__(self):
        self.rendered_map = {}
        self.images = {}
        files = []
        for file in os.listdir():
            if file.endswith('.gif') or file.endswith('.ppm'):
                files.append(file)
        for f in files:
            self.images[f] = tkinter.PhotoImage(file=f)
        self.files = files
        self.c = tkinter.Canvas(win.root,width=640,height=640,bg='#000000')
        self.c.grid(row=0,column=0)
    def plot(self,x,y,z):
        return ((x*GRIDSPACING) + WIDTH/2,HEIGHT/2 - (y + z*3/4)*GRIDSPACING)
    def renderMap(self,mapdata):
        self.eraseCanvas()
        self.rendered_map = mapdata
        keys = mapdata.keys()
        self.c.update()
        for k in list(keys):
            try:
                self.c.create_polygon(self.plot(k[0],k[1],mapdata[k][0]),self.plot(k[0],k[1]+1,mapdata[k[0],k[1]+1][0]),self.plot(k[0]+1,k[1]+1,mapdata[k[0]+1,k[1]+1][0]),self.plot(k[0]+1,k[1],mapdata[k[0]+1,k[1]][0]),fill=g.col([mapdata[k][1],mapdata[k][2],mapdata[k][3]]),tags=('x'+str(k[0]),'y'+str(k[1]),'z'+str(mapdata[k][0]),[k[0],k[1],mapdata[k][0]],[k[0],k[1]]))
            except:
                pass
        game.processLayers(-40,40)
    def re_render(self):
        self.eraseCanvas()
        self.renderMap(self.rendered_map)
        self.processLayers(-80,80)
    def getCoords(self,cid):
        try:
            tags = self.c.gettags(cid)
            return eval(tags[3])
        except:
            pass
    def generateMap(self,w,h):
        z = 0
        mapdata = {}
        for x in range(-w//2,w//2):
            for y in range(-h//2,h//2):
                mapdata[x,y] = [0,x*6,y*6,math.sin((x+y)/5)*12]
        return mapdata
    def processLayers(self,fromy,toy):
        for y in range(toy,fromy,-1):
            self.c.lift('y'+str(y))
##            self.c.update()
        for z in range(-10,64,1):
            self.c.lift('z'+str(z))
    def move(self,tag,x,y):
        self.c.move(tag,x,y)
##    def create_poly(self,coords,fill='#00ff00',outline='',tags=()):
##        coords = tuple(coords)
##        return self.c.create_polygon(coords,fill=fill,outline=outline,tags=tags)
    def getCentreOfTile(self,x,y):
        targetID = self.c.find_withtag([x,y])[0]
        tCoords = self.c.coords(targetID)
        #Calculate centre using mean of corner coordinates
        return [(tCoords[0]+tCoords[4])/2,(tCoords[1]+tCoords[5])/2]
    def create_sprite(self,x,y,filename):
        return self.c.create_image(x,y,image=self.images[filename])
    def eraseCanvas(self):
        self.c.delete(tkinter.ALL)
    def raiseTile(self,cid,y):
        try:
            coords = self.getCoords(cid)
            colour = self.rendered_map[coords[0],coords[1]][1:]
            self.rendered_map[coords[0],coords[1]] = [coords[2]+y,colour[0],colour[1],colour[2]]
        except:
            pass
    def colourTile(self,cid,newcol):
        newcol = newcol.replace('X',str(random.randint(180,220))).split(',')
        coords = self.getCoords(cid)
        self.rendered_map[coords[0],coords[1]] = [coords[2],newcol[0],newcol[1],newcol[2]]
    def smartColour(self,flatcol,gradcol):
        mapdata = self.rendered_map
        keys = mapdata.keys()
        for k in list(keys):
            try:
                zTotal = mapdata[k[0],k[1]][0] + mapdata[k[0],k[1]+1][0] + mapdata[k[0]+1,k[1]+1][0] + mapdata[k[0]+1,k[1]][0]
                if zTotal/4 == mapdata[k[0],k[1]][0]:
                    col = flatcol.replace('X',str(random.randint(180,220))).split(',')
                else:
                    col = gradcol.replace('X',str(random.randint(180,220))).split(',')
                mapdata[k] = [mapdata[k][0],int(col[0]),int(col[1]),int(col[2])]
            except:
                pass
        self.rendered_map = mapdata


class InputManager():
    def __init__(self,canvas):
        self.selected = []
        self.cref = canvas
        self.colour = '0,X,0'
        self.selectedCoords = []
    def updateSelectedCoords(self):#Makes reference of tiles that were selected
        self.selectedCoords = []
        for s in self.selected:
            self.selectedCoords.append(game.getCoords(s))
    def restoreSelection(self):
        self.selected = []
        for s in self.selectedCoords:
            try:
                cid = self.cref.find_withtag([s[0],s[1]])[0]
                self.selected.append(cid)
                self.cref.itemconfig(cid,outline='#ffff00',width=2)
            except:
                pass
    def editColour(self,event):
        self.updateSelectedCoords()
        try:
            col = input('Colour:\nr,g,b (0-255)\nUse \'X\' for variance\n')
            for cid in self.selected:
                game.colourTile(cid,col)
            game.re_render()
        except:
            print('An Error Occured')
        self.restoreSelection()
    def loadExported(self,event):
        self.selected = []
        with open('exported_map.map','r') as file:
            try:
                mapdata = eval(file.read())
            except:
                print('Error loading map!')
        game.renderMap(mapdata)
    def selection(self,event,sel_size=4):
        tiles = self.cref.find_overlapping(event.x-sel_size,event.y-sel_size,event.x+sel_size,event.y+sel_size)
        if len(tiles) > 0:
            for t in tiles:
                if t not in self.selected:
                    self.selected.append(t)
                    self.cref.itemconfig(t,outline='#ffff00',width=2)
    def clearSelection(self,event=''):
        self.selected = []
        self.selectedCoords = []
        self.cref.itemconfig(tkinter.ALL,outline='',width=1)
    def raiseSelection(self,event):
        self.updateSelectedCoords()
        for cid in self.selected:
            game.raiseTile(cid,1)
        game.re_render()
        self.restoreSelection()
    def lowerSelection(self,event):
        self.updateSelectedCoords()
        for cid in self.selected:
            game.raiseTile(cid,-1)
        game.re_render()
        self.restoreSelection()
    def exportMap(self,event=''):
        with open('exported_map.map','w') as file:
            file.write(str(game.rendered_map))
        print('Map saved')
    def recentColour(self,event):
        self.updateSelectedCoords()
        try:
            col = self.colour
            for cid in self.selected:
                game.colourTile(cid,col)
            game.re_render()
        except:
            print('An Error Occured')
        self.restoreSelection()
    def smartColour(self,event):
        self.updateSelectedCoords()
        flatcol = input('Colour when flat:\nr,g,b (0-255)\nUse \'X\' for variance\n')
        gradcol = input('Colour when gradient:\nr,g,b (0-255)\nUse \'X\' for variance\n')
        game.smartColour(flatcol,gradcol)
        game.re_render()
        self.restoreSelection()
    def smallSelection(self,event):
        self.selection(event,sel_size=4)
    def largeSelection(self,event):
        self.selection(event,sel_size=20)


class Entity():
    def __init__(self,UUID,data,name=None):#Name is only for player Entities
        self.UUID = UUID
        #Default Stats
        self.data = {'map':'start','x':0,'y':0,'moveSpeed':1,'abilities':[],'xp':0,'gold':0,'jumpHeight':2,'sprite':'texture_default_character_new.gif'}
        #Overwrite with loaded data
        for k in data.keys():
            self.data[k] = data[k]
        self.photo = tkinter.PhotoImage()
        tx,ty = game.getCentreOfTile(self.data['x'],self.data['y'])
        self.cid = game.create_sprite(tx,ty,self.data['sprite'])
    def move(self,newx,newy):
        """Moves the Entity onto the tile at newx, newy"""
        self.data['x'] = newx
        self.data['y'] = newy
        tx,ty = game.getCentreOfTile(self.data['x'],self.data['y'])
        game.c.coords(self.cid,tx,ty)#Move Sprite onto Centre of Tile




win = Window()

game = GameManager()

inpManager = InputManager(game.c)




if mode == 'play':
    ##---[FOR CONNECTING TO SERVER]---
    #Connection Management
    client = ClientManager(IP)

    #Thread to receive messages
    threading.Thread(target=client.receive).start()

    #Send login details
    print('Authenticating...')
    client.send('login',[username,password])
    win.root.bind('w',client.sendReq)
    win.root.bind('a',client.sendReq)
    win.root.bind('s',client.sendReq)
    win.root.bind('d',client.sendReq)
    ##---------------------------------




if mode == 'edit':
    ##---[FOR MAP EDITING]---
    #Default
    game.renderMap(game.generateMap(30,30))

    #Selection Inputs
    win.root.bind('<Button-1>',inpManager.clearSelection)
    win.root.bind('<B1-Motion>',inpManager.smallSelection)

    win.root.bind('<Button-3>',inpManager.clearSelection)
    win.root.bind('<B3-Motion>',inpManager.largeSelection)

    #Operation Inputs
    win.root.bind('c',inpManager.editColour)
    win.root.bind('r',inpManager.raiseSelection)
    win.root.bind('l',inpManager.lowerSelection)
    win.root.bind('x',inpManager.exportMap)
    win.root.bind('p',inpManager.loadExported)
    win.root.bind('k',inpManager.recentColour)
    win.root.bind('s',inpManager.smartColour)
    ##------------------------


win.mainloop()

