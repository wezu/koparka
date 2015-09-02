from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *
from ast import literal_eval as astEval

def _pos2d(x,y):
    return Point3(x,0,-y)
    
def _rec2d(width, height):
    return (-width, 0, 0, height)
    
def _resetPivot(frame):
    size=frame['frameSize']    
    frame.setPos(-size[0], 0, -size[3])        
    frame.flattenLight()
    
class GuiHelper():
    def __init__(self, path="", theme='icon'):
        self.elements=[]
        self.path=path
        self.theme=theme
        
        self.font = DGG.getDefaultFont()
        self.font.setPixelsPerUnit(16)       
        #self.font.setOutline((0, 0, 0, 0.9), 1, 0.8)
        
        self.fontBig=self.font.makeCopy()        
        self.fontBig.setPixelsPerUnit(32)
        
        self.TopLeft=pixel2d.attachNewNode('TopLeft')
        self.TopRight=pixel2d.attachNewNode('TopRight')
        self.BottomRight=pixel2d.attachNewNode('BottomRight')
        self.BottomLeft=pixel2d.attachNewNode('BottomLeft')
        self.Top=pixel2d.attachNewNode('Top')
        self.Bottom=pixel2d.attachNewNode('Bottom')
        self.Left=pixel2d.attachNewNode('Left')
        self.Right=pixel2d.attachNewNode('Right')
        self.Center=pixel2d.attachNewNode('Center')
        self.updateBaseNodes()
        
        self.wait=DirectFrame(frameSize=_rec2d(512,256),
                                frameColor=(1,1,1, 1),
                                frameTexture=self.theme+'/dialog.png',
                                text='Please wait...',
                                text_scale=32,
                                text_wordwrap=15,
                                text_font=self.fontBig,
                                text_pos=(-256,160),
                                text_fg=(1,1,1,1),
                                text_align=TextNode.ACenter,
                                parent=self.Center)
        _resetPivot(self.wait)
        self.wait.setPos(_pos2d(-256, -128))        
        self.wait.setTransparency(TransparencyAttrib.MDual)
        self.wait.hide()
        
        self.dialog=DirectFrame(frameSize=_rec2d(512,256),
                                frameColor=(1,1,1, 1),
                                frameTexture=self.theme+'/dialog.png',
                                text='This is a dialog, no text was set! Alfa, beta, gamma, delta, tango, lambda, epsilon, omega, zeta.',
                                text_scale=32,
                                text_wordwrap=15,
                                text_font=self.fontBig,
                                text_pos=(-256,220),
                                text_fg=(1,1,1,1),
                                text_align=TextNode.ACenter,
                                parent=self.Center)
        _resetPivot(self.dialog)
        self.dialog.setPos(_pos2d(-256, -128))        
        self.dialog.setTransparency(TransparencyAttrib.MDual)
        self.dialogYes=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,1.0),  
                                    text="YES",
                                    text_scale=32,                                    
                                    frameTexture=self.theme+'/button.png',
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,1,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.dialog)
        _resetPivot(self.dialogYes)
        self.dialogYes.setPos(_pos2d(32,132))
        self.dialogYes.setTransparency(TransparencyAttrib.MDual)
        self.dialogNo=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,1.0),
                                    frameTexture=self.theme+'/button.png',
                                    text="NO",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(1,0,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.dialog)
        _resetPivot(self.dialogNo)
        self.dialogNo.setPos(_pos2d(352,132))
        self.dialogNo.setTransparency(TransparencyAttrib.MDual)
        self.dialogOk=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,1.0),  
                                    text="OK",
                                    frameTexture=self.theme+'/button.png',
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,0,1,1),
                                    state=DGG.NORMAL, 
                                    parent=self.dialog)
        _resetPivot(self.dialogOk)
        self.dialogOk.setPos(_pos2d(192,132))        
        self.dialogOk.setTransparency(TransparencyAttrib.MDual)
        self.dialog.hide()
        
        self.slider = DirectSlider(range=(0,100),
                                    value=50,
                                    pageSize=1,      
                                    thumb_relief=DGG.FLAT,
                                    frameTexture=self.theme+'/slider_back.png',
                                    thumb_frameTexture=self.theme+'/button.png',                                    
                                    scale=64,
                                    orientation=DGG.VERTICAL,
                                    thumb_frameSize=(0.2, -0.2, -0.1, 0.1),
                                    frameSize=(2.0, -2.0, -1, 1),
                                    #command=self.set_slider,
                                    #extraArgs=[self.slider],
                                    parent=pixel2d)  
        self.slider.setPos(_pos2d(32,64))
        self.slider['extraArgs']=[self.slider]
        self.slider.setTransparency(TransparencyAttrib.MDual)
        self.slider.hide()
        
    def yesNoDialog(self, text, command, arg=[]):
        self.dialog.show()
        self.dialogYes.show()
        self.dialogNo.show()
        self.dialogOk.hide()   
        self.dialog['text']=text        
        yes_arg=[True]+arg[:]
        no_arg=[False]+arg[:]
        self.dialogYes.bind(DGG.B1PRESS, command, yes_arg)
        self.dialogNo.bind(DGG.B1PRESS, command, no_arg)
        
    def string2value(self, text, fail_value):
        value=None
        try:
            value=astEval(text)
            if isinstance(value, basestring):
                value=fail_value
        except:
            value=fail_value    
        return value    
        
    def okDialog(self, text, command, arg=[]):
        self.dialog.show()
        self.dialogYes.hide()
        self.dialogNo.hide()
        self.dialogOk.show()        
        self.dialog['text']=text
        self.dialogOk.bind(DGG.B1PRESS, command, arg)
    
    def validateEntry(self,id, text=None): 
        if isinstance(id, basestring):
            id=text
        value=0.0
        if id<100:
            text=self.ConfigEntry[id].get()            
            try:
                value=float(text)
            except ValueError:
                value=0.0
        else:
            value=self.string2value(self.SkySeaEntry[id-100].get(), self.SkySeaOptions[id-100])            
        if id==0:#size                        
            value=min(50.0, max(0.1, value))
            self.ConfigOptions[id]=value
        elif id==1:#alpha   
            value=min(1.0, max(0.0, value))
            self.ConfigOptions[id]=value
        elif id in (2,3,4): #hpr    
            value=min(360.0, max(0.0, value))
            self.ConfigOptions[id]=value
        elif id==5:#grid tile
            value=min(512.0, max(0.0, value))
            self.ConfigOptions[id]=value
        elif id==6:#grid Z
            value=min(500.0, max(0.0, value))    
            self.ConfigOptions[id]=value
        elif id==7:#light
            value=min(23.0, max(0.0, value))    
            self.ConfigOptions[id]=value 
        elif id==8:#fog
            value=min(1.0, max(0.0, value))    
            self.ConfigOptions[id]=value    
        elif id==100:#Terrain Tile
            try:                    
                value=min(512.0, max(1.0,value))
            except:
                value=self.SkySeaOptions[0]
        elif id==101:#Terrain Scale
            try:                    
                value=min(500.0, max(1.0,value))
            except:
                value=self.SkySeaOptions[1]            
        elif id==102:#Sky Tile
            try:                    
                value=min(512.0, max(1.0,value))
            except:
                value=self.SkySeaOptions[2]
        elif id==103:#Cloud Speed
            try:                    
                value=min(1.0, max(0.0,value))
            except:
                value=self.SkySeaOptions[3]
        elif id==104:#Wave Tile
            try:                    
                value=min(64.0, max(0.1,value))
            except:
                value=self.SkySeaOptions[4]
        elif id==105:#Wave Height
            try:                    
                value=min(1.0, max(0.0,value))
            except:
                value=self.SkySeaOptions[5]
        elif id==106:#Wave XY Move
             #shoul be 2 element tuple/list            
            if len(value)!=2:
                value=self.SkySeaOptions[8]
            try:    
                final=[]    
                for item in value:
                    final.append(min(1.0, max(0.0, item)))
                value=final    
            except:
                value=self.SkySeaOptions[6] 
        elif id==107:#Water Tile
            try:                    
                value=min(100.0, max(0.001,value))
            except:
                value=self.SkySeaOptions[7]
        elif id==108:#Water Speed
            try:                    
                value=min(1.0, max(0.00,value))
            except:
                value=self.SkySeaOptions[8]        
        elif id==109:#Water Z
            try:                    
                value=min(500.0, max(-1.0,value))
            except:
                value=self.SkySeaOptions[9]         
        if id<100:    
            self.ConfigEntry[id].enterText(str(value))   
        else:
            self.SkySeaEntry[id-100].enterText(str(value))
            self.SkySeaOptions[id-100]=value

    def setSkySeaValues(self, data):
        TerrainTile=data[0]['TerrainTile']
        TerrainScale=data[0]['TerrainScale']
        SkyTile=data[0]['SkyTile']
        CloudSpeed=data[0]['CloudSpeed']
        WaveTile=data[0]['WaveTile']
        WaveHeight=data[0]['WaveHeight']
        WaveXYMove=[data[0]['WaveXYMove'][0],data[0]['WaveXYMove'][1]]
        WaterTile=data[0]['WaterTile']
        WaterSpeed=data[0]['WaterSpeed']
        WaterLevel=data[0]['WaterLevel']
        
        self.SkySeaEntry[0].set(str(TerrainTile))
        self.SkySeaEntry[1].set(str(TerrainScale))
        self.SkySeaEntry[2].set(str(SkyTile))
        self.SkySeaEntry[3].set(str(CloudSpeed))
        self.SkySeaEntry[4].set(str(WaveTile))
        self.SkySeaEntry[5].set(str(WaveHeight))
        self.SkySeaEntry[6].set(str(WaveXYMove))
        self.SkySeaEntry[7].set(str(WaterTile))
        self.SkySeaEntry[8].set(str(WaterSpeed))
        self.SkySeaEntry[9].set(str(WaterLevel))
        
        for i in range(10):
            self.validateEntry(id=i+100)
            
    def addSkySeaDialog(self, command=None):
        #this one done 'properly'        
        #ordered dict should be used here... but not in python 2.5
        #so the hack...well it looks like it won't be as 'propre' as advertised         
        #labels=['Sky Color:','Fog Color:','Cloud Color:','Cloud Tile:','Cloud Speed:','Horizont:','Water Tile:','Water Speed:', 'Water Wave:','Water Level:\n(-1 to disable)']
        labels=['Terrain Tile:', 'Terrain Scale:', 'Sky Tile:','Cloud Speed:', 'Wave Tile:','Wave Height:','Wave XY Move:' ,'Water Tile:','Water Speed:', 'Water Level:\n(-1 to disable)']
        self.SkySeaOptions=[16.0, 100.0,            8.0,       0.008,            6.0,         1.0,           [0.005, 0.002], 20.0,         0.01,            -1]
        text=""
        for item in labels:
            text+=item+'\n'
        self.SkySeaFrame=DirectFrame(frameSize=_rec2d(512,512),
                                    frameColor=(1,1,1, 1),
                                    text=text,
                                    text_scale=32,
                                    frameTexture=self.theme+'/sky_dialog.png',
                                    text_font=self.fontBig,
                                    text_pos=(-280,476),
                                    text_fg=(0.9,0.9,0.9,1), 
                                    text_align=TextNode.ARight,
                                    parent=self.Center)
        self.SkySeaFrame.hide()
        _resetPivot(self.SkySeaFrame)
        self.SkySeaFrame.setTransparency(TransparencyAttrib.MDual)
        self.SkySeaFrame.setPos(_pos2d(-256, -240)) 
        
        self.okButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,0),  
                                    text="OK",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,1,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.SkySeaFrame)
        _resetPivot(self.okButton)        
        self.okButton.setPos(_pos2d(352,400))
        
        self.cancelButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,0),  
                                    text="CANCEL",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-66,7),
                                    text_fg=(1,0,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.SkySeaFrame)
        _resetPivot(self.cancelButton)        
        self.cancelButton.setPos(_pos2d(32,400)) 
        
        self.okButton.bind(DGG.B1PRESS, self.validateAndExec, [command,2, 10, 100])        
        self.cancelButton.bind(DGG.B1PRESS, command, [False]) 
        
        self.SkySeaEntry=[]
        for item in self.SkySeaOptions:
            id=len(self.SkySeaEntry)
            entry=DirectEntry(  frameSize=_rec2d(250,30),
                                frameColor=(1,1,1, 0),
                                text = str(item),
                                text_scale=16,                                                                
                                text_pos=(-240,14),
                                text_fg=(1,1,1,1),
                                text_align=TextNode.ALeft,
                                initialText=str(item),
                                numLines = 1,
                                width=19,
                                focus=0,
                                suppressKeys=True,
                                parent=self.SkySeaFrame,
                                command=self.validateEntry,
                                extraArgs=[100+id],
                                focusOutCommand=self.validateEntry,
                                focusOutExtraArgs=[100+id])
            _resetPivot(entry)
            entry.setPos(_pos2d(250,32*id+12))                    
            self.SkySeaEntry.append(entry)    
        
        
    def addConfigDialog(self, command): 
        labels=['Brush Scale:','Brush Strength(Z):','Heading:','Pitch:','Roll:','Grid Size:','Grid Z:','Time(0-23h):', 'Fog density:']
        self.ConfigOptions=[1.0, 1.0, 0.0, 0.0, 0.0, 16, 0.05, 12.0 , 1.0]
                           # 0    1    2    3    4    5    6    7      8
                           #Scale A    H    P    R  Grid  GridZ Sun   Fog
        text=""
        for item in labels:
            text+=item+'\n'
        self.ConfigFrame=DirectFrame(frameSize=_rec2d(512,512),
                                    frameColor=(1,1,1, 1),
                                    text=text,
                                    text_scale=32,
                                    frameTexture=self.theme+'/config_dialog.png',
                                    text_font=self.fontBig,
                                    text_pos=(-230,476),
                                    text_fg=(0.9,0.9,0.9,1), 
                                    text_align=TextNode.ARight,
                                    parent=self.Center)
        self.ConfigFrame.hide()
        _resetPivot(self.ConfigFrame)
        self.ConfigFrame.setTransparency(TransparencyAttrib.MDual)
        self.ConfigFrame.setPos(_pos2d(-256, -240)) 
        
        self.okButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(0,0,1,0.0),  
                                    text="OK",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,1,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.ConfigFrame)
        _resetPivot(self.okButton)        
        self.okButton.setPos(_pos2d(352,314))
        
        self.cancelButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(0,0,1,0.0),  
                                    text="CANCEL",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-66,7),
                                    text_fg=(1,0,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.ConfigFrame)
        _resetPivot(self.cancelButton)        
        self.cancelButton.setPos(_pos2d(32,314)) 
        
        self.okButton.bind(DGG.B1PRESS, self.validateAndExec, [command,2, 8, 0])        
        self.cancelButton.bind(DGG.B1PRESS, command, [False]) 
        
        self.ConfigEntry=[]
        for item in self.ConfigOptions:
            id=len(self.ConfigEntry)
            entry=DirectEntry(  frameSize=_rec2d(200,30),
                                frameColor=(1,0,0, 0.0),
                                text = str(item),
                                text_scale=16,                                                                
                                text_pos=(-200,14),
                                text_fg=(1,1,1,1),
                                text_align=TextNode.ALeft,
                                initialText=str(item),
                                numLines = 1,
                                width=19,
                                focus=0,
                                suppressKeys=True,
                                parent=self.ConfigFrame,
                                command=self.validateEntry,
                                extraArgs=[id],
                                focusOutCommand=self.validateEntry,
                                focusOutExtraArgs=[id])
            _resetPivot(entry)
            entry.setPos(_pos2d(290,32*id+12))                    
            self.ConfigEntry.append(entry)    
        
    def validateAndExec(self, command, arg, max=7, offset=0, event=None):
        for i in range(max):
            self.validateEntry(id=i+offset)
        command(arg)
        
    def addSaveLoadDialog(self, save_command, load_command, cancel_command):
        #save/load 
        self.SaveLoadFrame=DirectFrame( frameSize=_rec2d(512,512),
                                        frameColor=(1,1,1, 1),
                                        frameTexture=self.theme+'/save_dialog.png',
                                        text="Directory:\nHeight:\nDetail:\nGrass:\nObjects:\nCollision:\nWalkMap:",
                                        text_scale=32,
                                        text_font=self.fontBig,
                                        text_pos=(-360,474),
                                        text_fg=(0.9,0.9,0.9,1), 
                                        text_align=TextNode.ARight,
                                        parent=self.Center)
        _resetPivot(self.SaveLoadFrame)
        self.SaveLoadFrame.setPos(_pos2d(-256, -256))        
        self.SaveLoadFrame.setTransparency(TransparencyAttrib.MDual)
        self.entry1 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = self.path+"save/default1",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText= self.path+"save/default1",
                        numLines = 2,
                        width=19,
                        focus=0,
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry1)
        self.entry1.setPos(_pos2d(160,16))
        
        self.entry2 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = "heightmap",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="heightmap",
                        numLines = 2,
                        width=19,
                        focus=0,
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry2)
        self.entry2.setPos(_pos2d(160,48))
        
        self.entry3 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = "detail",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="detail",
                        numLines = 2,
                        width=19,
                        focus=0,
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry3)
        self.entry3.setPos(_pos2d(160,80))        
        
        self.entry5 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text ="grass",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="grass",
                        numLines = 2,
                        width=19,
                        focus=0,
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry5)
        self.entry5.setPos(_pos2d(160,112))
        
        self.entry6 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = "objects",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="objects",
                        numLines = 2,
                        width=19,
                        focus=0,
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry6)
        self.entry6.setPos(_pos2d(160,144)) 
        
        self.entry7 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = "collision",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="collision",
                        numLines = 2,
                        width=19,
                        focus=0, 
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry7)
        self.entry7.setPos(_pos2d(160,176))
        
        self.entry8 = DirectEntry(frameSize=_rec2d(300,30),
                        frameColor=(1,1,1, 0.0),
                        text = "navmesh",
                        text_scale=16,
                        text_pos=(-300,14),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="navmesh",
                        numLines = 2,
                        width=19,
                        focus=0, 
                        suppressKeys=True,
                        parent=self.SaveLoadFrame
                        )
        _resetPivot(self.entry8)
        self.entry8.setPos(_pos2d(160,208))        
        
        self.check1=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check1)
        self.check1.setPos(_pos2d(464,48))
        self.check2=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check2)
        self.check2.setPos(_pos2d(464,80))
        self.check3=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check3)
        self.check3.setPos(_pos2d(464,112))
        
        self.check5=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check5)
        self.check5.setPos(_pos2d(464,144))
        self.check6=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check6)
        self.check6.setPos(_pos2d(464,176))
        
        self.check7=DirectFrame(frameSize=_rec2d(32,32),
                                frameColor=(1,1,1,0.99),                      
                                frameTexture=self.theme+'/yes.png',
                                state=DGG.NORMAL, 
                                parent=self.SaveLoadFrame)
        _resetPivot(self.check7)
        self.check7.setPos(_pos2d(464,208))
        
        self.check1.bind(DGG.B1PRESS, self.switchFlag, [0])
        self.check2.bind(DGG.B1PRESS, self.switchFlag, [1])
        self.check3.bind(DGG.B1PRESS, self.switchFlag, [2])
        
        self.check5.bind(DGG.B1PRESS, self.switchFlag, [4])
        self.check6.bind(DGG.B1PRESS, self.switchFlag, [5])
        self.check7.bind(DGG.B1PRESS, self.switchFlag, [6])
        
        self.checkers=[self.check1,self.check2,self.check3,None,self.check5,self.check6,self.check7]        
        self.flags=[]
        for check in self.checkers:
            self.flags.append(True)
        
        self.saveButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,0.0),  
                                    text="SAVE",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,1,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.SaveLoadFrame)
        _resetPivot(self.saveButton)
        self.saveButton.setPos(_pos2d(32,250))
        
        self.loadButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,0.0),  
                                    text="LOAD",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-70,7),
                                    text_fg=(0,0,1,1),
                                    state=DGG.NORMAL, 
                                    parent=self.SaveLoadFrame)
        _resetPivot(self.loadButton)
        self.loadButton.setPos(_pos2d(352,250))
        
        self.cancelButton=DirectFrame(frameSize=_rec2d(128,32),
                                    frameColor=(1,1,1,0.0),  
                                    text="CANCEL",
                                    text_scale=32,
                                    text_font=self.fontBig,
                                    text_pos=(-66,7),
                                    text_fg=(1,0,0,1),
                                    state=DGG.NORMAL, 
                                    parent=self.SaveLoadFrame)
        _resetPivot(self.cancelButton)
        self.cancelButton.setPos(_pos2d(192,250))
        
        self.saveButton.bind(DGG.B1PRESS, save_command, ["ASK"])
        self.loadButton.bind(DGG.B1PRESS, load_command)
        self.cancelButton.bind(DGG.B1PRESS, cancel_command)
        
        self.SaveLoadFrame.hide()
    
    def _setColor(self, frame, color):
        frame['frameColor']=color
        
    def blink(self, element, button=None):
        if button==None:
            frame=self.elements[element]['frame']        
        else:
            frame=self.elements[element]['buttons'][button]
        old_color=frame['frameColor']
        new_color=(1-old_color[0],1-old_color[1], 1-old_color[2], 1-old_color[3])
        Sequence(Func(self._setColor,frame,new_color), Wait(0.1),Func(self._setColor,frame,old_color)).start()
        
    def grayOutButtons(self, toolbar, from_to, but_not, on_color=(1,1,1, 1), off_color=(0.4,0.4,0.4, 1)):
        for i in range(from_to[0], from_to[1]):
            self.elements[toolbar]['buttons'][i]['frameColor']=off_color
        if but_not!=None:
            self.elements[toolbar]['buttons'][but_not]['frameColor']=on_color
            
    def switchFlag(self, flag_id, event=None):
        if self.flags[flag_id]:
            self.flags[flag_id]=False
            self.checkers[flag_id]['frameTexture']=self.theme+'/no.png'
        else:
            self.flags[flag_id]=True
            self.checkers[flag_id]['frameTexture']=self.theme+'/yes.png'
            
    def updateBaseNodes(self):
        wp=base.win.getProperties()
        winX = wp.getXSize()
        winY = wp.getYSize()    
            
        self.TopLeft.setPos(_pos2d(0,0))
        self.TopRight.setPos(_pos2d(winX,0))        
        self.BottomRight.setPos(_pos2d(winX,winY))
        self.BottomLeft.setPos(_pos2d(0,winY))
        self.Top.setPos(_pos2d(winX/2,0))
        self.Bottom.setPos(_pos2d(winX/2,winY))
        self.Left.setPos(_pos2d(0,winY/2))
        self.Right.setPos(_pos2d(winX,winY/2))
        self.Center.setPos(_pos2d(winX/2,winY/2))
    
    def hideElement(self, id):
        self.elements[id]['frame'].hide()
    
    def showElement(self, id):
        self.elements[id]['frame'].show()
    
    def addScrolledToolbar(self, parent, width, canvas_size, x_offset=0, y_offset=0, hover_command=False, color=(1,0,0, 0)):         
        wp=base.win.getProperties()        
        height=wp.getYSize()-y_offset-256
        frame=DirectScrolledFrame(canvasSize = _rec2d(canvas_size[0],canvas_size[1]),
                                  frameSize = _rec2d(width,height),                              
                                  verticalScroll_frameSize=_rec2d(16,height), 
                                  verticalScroll_frameColor=(0, 0, 1, 0),
                                  frameColor=color,
                                  manageScrollBars=False,
                                  autoHideScrollBars=False, 
                                  verticalScroll_thumb_frameColor=(1, 1, 1, 0.8),                              
                                  parent=parent                              
                                )         
        frame.verticalScroll['value']=0
        frame.verticalScroll['incButton_relief']=None
        frame.verticalScroll['incButton_state'] = DGG.DISABLED
        frame.verticalScroll['decButton_relief']=None
        frame.verticalScroll['decButton_state'] = DGG.DISABLED
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setX(frame, x_offset)
        frame.setZ(frame, -y_offset)
        if hover_command:
            frame['state']=DGG.NORMAL
            frame.bind(DGG.WITHOUT, hover_command,[False])  
            frame.bind(DGG.WITHIN, hover_command, [True]) 
        data={'size':canvas_size[1], 'frame':frame, 'buttons':[]}
        id=len(self.elements)
        self.elements.append(data)
        return id
        
    def addListButton(self, parent_id, text, command, arg=[], tooltip=None, tooltip_text=None):
        parent=self.elements[parent_id]['frame'].getCanvas()
        id=len(self.elements[parent_id]['buttons'])
        y_offset=self.elements[parent_id]['size']-20
        frame= DirectFrame( frameSize=_rec2d(174,20),
                        frameColor=(0,0,0,0.6),
                        state=DGG.NORMAL,                        
                        text=text,
                        text_scale=16,
                        text_pos=(-172,7),
                        text_fg=(1,1,1,1),
                        text_align=TextNode.ALeft,
                        parent=parent)
        #_resetPivot(frame)        
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setPos(_pos2d(-10,-y_offset+21*id))        
        self.elements[parent_id]['buttons'].append(frame)
        arg.append(id)
        frame.bind(DGG.B1PRESS, command, arg)        
        if tooltip:            
            frame.bind(DGG.WITHIN, self.setTooltip,[tooltip, tooltip_text])  
            frame.bind(DGG.WITHOUT, self.setTooltip,[tooltip, None])  
        
    def addPropPanel(self):   
        mainFrame=DirectFrame( frameSize=_rec2d(192,256),
                        frameColor=(0, 0, 0, 0.8),  
                        text=" GRID SNAP:\n\n         PROPERTIES:",
                        text_align=TextNode.ALeft,
                        text_scale=16,
                        text_pos=(-192,240),
                        text_fg=(1,1,1,1),                        
                        parent=self.BottomRight)
        _resetPivot(mainFrame)                
        mainFrame.setPos(_pos2d(-192, -256))
        frame=DirectScrolledFrame(canvasSize = _rec2d(192,500),
                                  frameSize = _rec2d(192,200),                              
                                  verticalScroll_frameSize=_rec2d(16,200), 
                                  verticalScroll_frameColor=(0, 0, 1, 0),
                                  frameColor=(0,0,0, 0.0),
                                  manageScrollBars=False,
                                  autoHideScrollBars=False, 
                                  verticalScroll_thumb_frameColor=(1, 1, 1, 0.8),                              
                                  parent=mainFrame                              
                                )         
        frame.verticalScroll['value']=0
        frame.verticalScroll['incButton_relief']=None
        frame.verticalScroll['incButton_state'] = DGG.DISABLED
        frame.verticalScroll['decButton_relief']=None
        frame.verticalScroll['decButton_state'] = DGG.DISABLED           
        _resetPivot(frame)
        frame.setZ(frame, -56)
        #frame.setX(frame, 16)
        snap = DirectEntry(frameSize=_rec2d(80,18),
                        frameColor=(1,1,1, 0.4),
                        text ="0.5",
                        text_scale=16,
                        text_pos=(-80,6),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText="0.5",
                        width=5,
                        focus=0,
                        suppressKeys=True,
                        parent=mainFrame
                        )    
        _resetPivot(snap)
        snap.setPos(_pos2d(112, 4))
        props = DirectEntry(frameSize=_rec2d(190,500),
                        frameColor=(1,1,1, 0.4),
                        text ="",
                        text_scale=16,
                        text_pos=(-190,484),
                        text_fg=(1,1,1,1),
                        initialText="",
                        numLines = 30,
                        width=11,
                        focus=0,
                        suppressKeys=True,
                        parent=frame.getCanvas()
                        )                    
        id=len(self.elements)
        self.elements.append({'frame':mainFrame, 'entry_props':props, 'entry_snap':snap})                    
        return id
                
    def addToolbar(self, parent, size, icon_size=32, x_offset=0, y_offset=0, hover_command=False, color=(1,0,0, 0)):         
        frame=DirectFrame( frameSize=_rec2d(size[0],size[1]),
                        frameColor=color,                        
                        state=DGG.NORMAL,   
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setX(frame, x_offset)
        frame.setZ(frame, -y_offset)
        if hover_command:
            frame.bind(DGG.WITHOUT, hover_command,[False])  
            frame.bind(DGG.WITHIN, hover_command, [True]) 
        data={'size':size[0], 'icon_size':icon_size, 'frame':frame, 'buttons':[]}
        id=len(self.elements)
        self.elements.append(data)
        return id
    
    def addEntry(self, toolbar, size_x, offset_x, offset_y=0, color=(1,1,1, 0.3)):
        size_y=self.elements[toolbar]['icon_size']
        parent=self.elements[toolbar]['frame']
        x=offset_x
        y=len(self.elements[toolbar]['buttons'])*size_y
        entry=DirectEntry(frameSize=_rec2d(size_x,size_y-2),
                            frameColor=color,
                            text = '1.0',
                            text_scale=16,
                            text_pos=(-size_x,12),
                            text_fg=(1,1,1,1),
                            initialText= '1.0',
                            numLines = 1,
                            width=19,
                            focus=0,
                            suppressKeys=True,
                            parent=parent
                            )
        _resetPivot(entry)
        entry.setTransparency(TransparencyAttrib.MDual)
        entry.setPos(_pos2d(x,y+offset_y+1))
        self.elements[toolbar]['buttons'].append(entry)
        
    def addButton(self, toolbar, icon, command, arg=[], tooltip=None, tooltip_text=None, back_icon=None):
        size=self.elements[toolbar]['icon_size']
        parent=self.elements[toolbar]['frame']
        max_x=self.elements[toolbar]['size']
        x=len(self.elements[toolbar]['buttons'])*size
        y=0
        while x>=max_x:
            y+=size
            x-=max_x
        if back_icon:
            back_icon=DirectFrame( frameSize=_rec2d(size,size),
                        frameColor=(1,1,1,1),
                        state=DGG.NORMAL,                        
                        frameTexture=back_icon,
                        parent=parent)
            _resetPivot(back_icon)
            back_icon.setTransparency(TransparencyAttrib.MDual)
            back_icon.setPos(_pos2d(x,y))
        frame= DirectFrame( frameSize=_rec2d(size,size),
                        frameColor=(1,1,1,1),
                        state=DGG.NORMAL,                        
                        frameTexture=icon,
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setPos(_pos2d(x,y))
        frame.bind(DGG.B1PRESS, command, arg)
        self.elements[toolbar]['buttons'].append(frame)
        if tooltip:            
            frame.bind(DGG.WITHIN, self.setTooltip,[tooltip, tooltip_text])  
            frame.bind(DGG.WITHOUT, self.setTooltip,[tooltip, None])          
            
    def addFloatingButton(self, parent_id, size, icon, pos, command, arg=[], tooltip=None, tooltip_text=None):  
        parent=self.elements[parent_id]['frame']
        frame= DirectFrame( frameSize=_rec2d(size[0],size[1]),
                        frameColor=(1,1,1,1),
                        state=DGG.NORMAL,                        
                        frameTexture=icon,
                        parent=parent)
        _resetPivot(frame)
        frame.setPos(_pos2d(pos[0],pos[1]))
        frame.setTransparency(TransparencyAttrib.MDual)        
        frame.bind(DGG.B1PRESS, command, arg)
        self.elements.append({'frame':frame})
        if tooltip:            
            frame.bind(DGG.WITHIN, self.setTooltip,[tooltip, tooltip_text])  
            frame.bind(DGG.WITHOUT, self.setTooltip,[tooltip, None]) 
        return frame
        
    def addInfoIcon(self, toolbar, icon, text, tooltip=None, tooltip_text=None, slider_cmd=None, slider_range=None):       
        parent=self.elements[toolbar]['frame']
        x=len(self.elements[toolbar]['buttons'])*64
          
        frame= DirectFrame( frameSize=_rec2d(64,64),
                        frameColor=(1,1,1,1),                   
                        frameTexture=icon,
                        text=text,
                        text_scale=16,
                        text_pos=(-32,16),
                        text_fg=(0,0,0,1),
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setPos(_pos2d(x,0))
        self.elements[toolbar]['buttons'].append(frame)
        if tooltip:  
            frame['state']=DGG.NORMAL
            frame.bind(DGG.WITHIN, self.setTooltip,[tooltip, tooltip_text])  
            frame.bind(DGG.WITHOUT, self.setTooltip,[tooltip, None])
        if slider_cmd:    
            frame.bind(DGG.B1PRESS, self.popupSlider, [frame, slider_cmd, slider_range])    
        return frame
        
    def popupSlider(self, parent, slider_cmd, slider_range, event=None):        
        if self.slider.isHidden():
            self.slider.show()
            self.slider['range']=(slider_range[0],slider_range[1])
            try:
                self.slider['value']=float(parent['text'])
            except:   
                self.slider['value']=float(parent['text'].split(": ")[1]) 
            self.slider['command']=slider_cmd            
            pos=parent.getPos(pixel2d)
            pos[0]+=32.0
            pos[2]+=64.0
            self.slider.setPos(pos)
        else:
            self.slider.hide()    
            pos=parent.getPos(pixel2d)
            pos[0]+=32.0
            pos[2]+=64.0
            if pos!=self.slider.getPos():                
                self.slider.setPos(pos)
                self.slider['range']=(slider_range[0],slider_range[1])
                try:
                    self.slider['value']=float(parent['text'])
                except:   
                    self.slider['value']=float(parent['text'].split(": ")[1])
                self.slider['command']=slider_cmd
                self.slider.show()    
                
    def setTooltip(self, tooltip, tooltip_text, guiEvent=None):
        if tooltip_text:
            tooltip.show()
            tooltip['text']=tooltip_text            
        else:    
            tooltip.hide()
            
    def addTooltip(self, parent,size, x_offset=0, y_offset=0):
        frame=DirectFrame( frameSize=_rec2d(size[0],size[1]),
                        frameColor=(0,0,0, 0.5),  
                        text="test",
                        text_scale=16,
                        text_align=TextNode.ALeft,
                        text_pos=(-size[0]+10,14),
                        text_fg=(1,1,1,1),                        
                        state=DGG.NORMAL,   
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setX(frame, x_offset)
        frame.setZ(frame, -y_offset)
        return frame
    
    def hideColorPicker(self, event=None):
        self.colorPickerFrame.hide()
        
    def showColorPicker(self, event=None):
        self.colorPickerFrame.show()
        
    def applyColor(self, command, event=None):
        self.colorPickerFrame.hide()
        command()        
    
    def overrideColor(self, event=None):
        color=str(self.colorEntry.get())
        try:
            pixel=astEval(color)  
            self.sample['frameColor']=(pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0, 1.0)            
        except:
            print "Unknown format!"
            
    def pickColor(self, event=None):        
        mpos=Vec2(event.getMouse()[0], event.getMouse()[1])                
        mpos+=(1, -1)
        mpos[0]*=base.win.getXSize()/2
        mpos[1]*=-1*base.win.getYSize()/2
        mpos[0]=max(1, mpos[0])
        mpos[1]=max(1, mpos[1])
        img=PNMImage('data/color_picker.png')
        try:            
            pixel=img.getPixel(int(mpos[0]), int(mpos[1]))
            pixel=[pixel[0],pixel[1], pixel[2]]
            self.colorEntry.set('{0}, {1}, {2}'.format(*pixel))
            self.sample['frameColor']=(pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0, 1.0)
        except:
            print "Pixel out of range, try again!"
            
    def addColorPicker(self, apply_command):
        self.colorPickerFrame=DirectFrame(frameSize=_rec2d(256,256+64),
                              frameColor=(1,1,1,0.99),
                              text='RGB=',
                              text_scale=16,          
                              text_pos=(-256,48),
                              text_align=TextNode.ALeft,
                              frameTexture=self.theme+'/color_picker.png',
                              text_fg=(1,1,1,1),
                              parent=pixel2d)   
        _resetPivot(self.colorPickerFrame)
        #self.colorPickerFrame.setPos(_pos2d(16,16))
        tex = loader.loadTexture('data/color_picker.png')
        tex.setFormat(Texture.F_srgb_alpha)
        picker=DirectFrame(frameSize=_rec2d(256,256),
                            frameColor=(1,1,1,1),
                            state=DGG.NORMAL,
                            frameTexture=tex,
                            parent=self.colorPickerFrame)
        _resetPivot(picker)
        picker.bind(DGG.B1PRESS, self.pickColor)
        self.sample=DirectFrame(frameSize=_rec2d(32,32),frameColor=(1,1,1,1),parent=self.colorPickerFrame)
        _resetPivot(self.sample)  
        self.sample.setPos(_pos2d(222, 258))
        self.colorEntry=DirectEntry(frameSize=_rec2d(128,22),
                        frameColor=(1,1,1, 0.0),
                        text = "255, 255, 255",
                        text_scale=16,
                        text_pos=(-128,8),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText= "255, 255, 255",
                        numLines = 1,                        
                        focus=1,
                        parent=self.colorPickerFrame,
                        command=self.overrideColor,                                
                        focusOutCommand=self.overrideColor,
                        )
        _resetPivot(self.colorEntry)
        self.colorEntry.setPos(_pos2d(48,258))
        self.colorOk=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.0),
                                 text='OK',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.colorPickerFrame)
        _resetPivot(self.colorOk)  
        self.colorOk.setPos(_pos2d(2, 292))
        self.colorOk.bind(DGG.B1PRESS, self.applyColor, [apply_command])
        self.colorCancel=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.0),
                                 text='Cancel',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.colorPickerFrame)
        _resetPivot(self.colorCancel)  
        self.colorCancel.setPos(_pos2d(124, 292))
        self.colorCancel.bind(DGG.B1PRESS, self.hideColorPicker)
        self.colorPickerFrame.hide()
