from panda3d.core import loadPrcFileData
#loadPrcFileData('','show-frame-rate-meter  1')
loadPrcFileData('','win-size 1024 720')
loadPrcFileData('','sync-video 0')
#loadPrcFileData('','undecorated 1')
from panda3d.core import *
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles import Particles
from direct.particles import ForceGroup
#from panda3d.physics import BaseParticleRenderer
#from panda3d.physics import BaseParticleEmitter
from panda3d.physics import*
from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.gui.DirectGui import *
import json
from ast import literal_eval as astEval
from os import makedirs
from os.path import dirname
from direct.stdpy.file import listdir, exists

def clamp(x, min_val=0.0, max_val=1.0):
    return min(max_val, max(min_val, float(x))) 
    
def smootherstep(edge0, edge1, x): 
    if edge0==edge1:
        return edge0        
    x = clamp((x - edge0)/(edge1 - edge0), 0.0, 1.0)   
    # Evaluate polynomial
    #p=x*x*x*(x*(x*6.0 - 15.0) + 10.0)  #Ken Perlin? 
    p=x*x*(3.0 - 2.0*x)
    return p

def linstep(edge0, edge1, x):
    p=(edge0*x)+(edge1*(1.0-x))
    #print edge0, edge1, x, '->', p
    return p

    
def _pos2d(x,y):
    return Point3(x,0,-y)
    
def _rec2d(width, height):
    return (-width, 0, 0, height)
    
def _resetPivot(frame):
    size=frame['frameSize']    
    frame.setPos(-size[0], 0, -size[3])        
    frame.flattenLight()

class Editor (DirectObject):
    def __init__(self):
        #init ShowBase
        base = ShowBase.ShowBase()
        base.enableParticles()
        #set view
        #base.disableMouse()         
        #base.camera.setPos(30.0, -30.0, 10.0)
        #base.camera.lookAt((0.0, 0.0, -1.0))
        
        #make some background
        self.room=loader.loadModel('room')
        self.room.setScale(10)
        self.room.reparentTo(render)
        self.room.setBin("background", 11) 
        
        self.p=None
        self.values={}
        self.massDependant=[1,1,1,1,1]        
        self.root = NodePath("root")        
        self.saveDir="particle/effect"        
        i=0
        p=self.saveDir
        while(exists(p)):
            p=self.saveDir+str(i)
            i+=1
        self.saveDir=p
        self.currentColorGradient=loader.loadTexture("blank.png")
        self.currentSizeGradient=loader.loadTexture("blank.png")
        self.currentShapeGradient=loader.loadTexture("blank.png")
        self.currentSizeGradient.setWrapU(Texture.WMClamp)        
        self.currentSizeGradient.setWrapV(Texture.WMClamp)
        self.currentShapeGradient.setWrapU(Texture.WMClamp)
        self.currentShapeGradient.setWrapV(Texture.WMClamp)       
        #self.restartParticles()
       
        #gui
        font = DGG.getDefaultFont()
        font.setPixelsPerUnit(16)         
        font.setMinfilter(Texture.FTNearest )
        font.setMagfilter(Texture.FTNearest )
        
        offset=(base.win.getXSize()/2)-(16*32/2)
        self.current_id=0
        self.activeColors=[]
        self.activeAlphas=[]
        self.activeSizes=[]
        #size over time
        sizeFrame=DirectFrame(frameSize=_rec2d(base.win.getXSize(),130),
                              frameColor=(0,0,0,0.6),
                              text='Size:',
                              text_scale=16,          
                              text_pos=(-base.win.getXSize(),64),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)
        _resetPivot(sizeFrame)
        sizeFrame.setPos(_pos2d(0, base.win.getYSize()-128-16)) 
        self.sizeButtons=[]
        for i in range(64):
            f=DirectFrame(frameSize=_rec2d(8,128),frameColor=(1,1,1,1),state=DGG.NORMAL, parent=sizeFrame,frameTexture='no_size.png')
            _resetPivot(f)
            f.setPos(_pos2d(offset+i*8, 0))
            f.setShader(Shader.load(Shader.SLGLSL, "size_v.glsl","size_f.glsl"), 1)
            f.setShaderInput('size', 0.5)
            f.bind(DGG.B1PRESS, self.sizeSetup,[i])
            self.sizeButtons.append(f)
        sizeHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=sizeFrame)
        _resetPivot(sizeHide)
        sizeHide.setTransparency(TransparencyAttrib.MAlpha)
        sizeHide.setPos(_pos2d(base.win.getXSize()-32, 54))               
        sizeHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.sizeButtons,sizeFrame,None])     
        #color over time        
        colorFrame=DirectFrame(frameSize=_rec2d(base.win.getXSize(),34),
                              frameColor=(0,0,0,0.6),
                              text='Color:',
                              text_scale=16,          
                              text_pos=(-base.win.getXSize(),16),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)
        _resetPivot(colorFrame)
        colorFrame.setPos(_pos2d(0, base.win.getYSize()-65-96-16)) 
        self.colorButtons=[]
        for i in range(64):
            f=DirectFrame(frameSize=_rec2d(8,32),frameColor=(1,1,1,1),state=DGG.NORMAL,parent=colorFrame, frameTexture='no_mark.png')
            _resetPivot(f)
            f.setPos(_pos2d(offset+i*8, 1))            
            f.setShader(Shader.load(Shader.SLGLSL, "mark_v.glsl","mark_f.glsl"), 1)
            f.setShaderInput('glsl_color', Vec4(1.0,1.0,1.0,1.0))
            f.bind(DGG.B1PRESS, self.colorSetup,[i])
            self.colorButtons.append(f)
        colorsHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=colorFrame)
        _resetPivot(colorsHide)
        colorsHide.setTransparency(TransparencyAttrib.MAlpha)
        colorsHide.setPos(_pos2d(base.win.getXSize()-32, 1))               
        colorsHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.colorButtons, colorFrame,None])        
        #alpha over time
        alphaFrame=DirectFrame(frameSize=_rec2d(base.win.getXSize(),34),
                              frameColor=(0,0,0,0.6),
                              text='Alpha:',
                              text_scale=16,          
                              text_pos=(-base.win.getXSize(),16),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)
        _resetPivot(alphaFrame)
        alphaFrame.setPos(_pos2d(0, base.win.getYSize()-98-96-16))
        self.alphaButtons=[]
        for i in range(64):
            f=DirectFrame(frameSize=_rec2d(8,32),frameColor=(1,1,1,1),state=DGG.NORMAL,parent=alphaFrame,frameTexture='no_mark.png')
            _resetPivot(f)
            f.setPos(_pos2d(offset+i*8, 1))
            f.setShader(Shader.load(Shader.SLGLSL, "mark_v.glsl","mark_f.glsl"), 1)
            f.setShaderInput('glsl_color', Vec4(1.0,1.0,1.0,1.0))
            f.bind(DGG.B1PRESS, self.alphaSetup,[i])
            self.alphaButtons.append(f)
        alphaHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=alphaFrame)
        _resetPivot(alphaHide)
        alphaHide.setTransparency(TransparencyAttrib.MAlpha)
        alphaHide.setPos(_pos2d(base.win.getXSize()-32, 1))               
        alphaHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.alphaButtons, alphaFrame,None])  
           
        #shape over time
        shapeFrame=DirectFrame(frameSize=_rec2d(base.win.getXSize(),64),
                              frameColor=(0,0,0,0.6),
                              text='Shape:',
                              text_scale=16,          
                              text_pos=(-base.win.getXSize(),30),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)
        _resetPivot(shapeFrame)
        shapeFrame.setPos(_pos2d(0, base.win.getYSize()-130-96-31-16))
        self.shapeButtons=[]
        for i in range(8):
            f=DirectFrame(frameSize=_rec2d(64,64),frameColor=(1,1,1,1),state=DGG.NORMAL,parent=shapeFrame, frameTexture='blank.png')
            _resetPivot(f)
            f.setPos(_pos2d(offset+i*64, -1))
            f.bind(DGG.B1PRESS, self.shapeSetup,[i])
            self.shapeButtons.append(f)
        shapeHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=shapeFrame)
        _resetPivot(shapeHide)        
        shapeHide.setTransparency(TransparencyAttrib.MAlpha)
        shapeHide.setPos(_pos2d(base.win.getXSize()-32, 16))               
        shapeHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.shapeButtons,shapeFrame,None])    
        #save
        saveFrame=DirectFrame(frameSize=_rec2d(base.win.getXSize(),16),
                              frameColor=(0,0,0,0.6),
                              text='Save as:',
                              text_scale=16,          
                              text_pos=(-base.win.getXSize(),4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)
        _resetPivot(saveFrame)
        saveFrame.setPos(_pos2d(0, base.win.getYSize()-16))
        self.saveEntry=DirectEntry(frameSize=_rec2d(256,15),
                              frameColor=(1,1,1, 0.5),
                              text = self.saveDir,
                              text_scale=16,
                              text_pos=(-256,4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              initialText= self.saveDir,
                              numLines = 1,                        
                              focus=0,
                              parent=saveFrame)
        _resetPivot(self.saveEntry)
        self.saveEntry.setPos(_pos2d(offset,0))  
        self.saveButton=DirectFrame(frameSize=_rec2d(256,16),
                              frameColor=(0.5,0.5,0.5,0.5),
                              text='Click here to save!',
                              text_scale=16,          
                              text_pos=(-200,4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              state=DGG.NORMAL,
                              parent=saveFrame)
        _resetPivot(self.saveButton)
        self.saveButton.setPos(_pos2d(offset+256, 0))
        self.saveButton.bind(DGG.B1PRESS, self.export)
        #particle config 
        self.configFrame=DirectFrame(frameSize=_rec2d(256,128),
                                 frameColor=(0,0,0,0.6),
                                 text='Emiter:\nPool:\nBirth Rate:\nLitter:                 +/-\nLife:                    +/-\nMass:                  +/-\nBlend:',
                                 text_scale=16,          
                                 text_pos=(-256,128-16),
                                 text_align=TextNode.ALeft,
                                 text_fg=(1,1,1,1),
                                 parent=pixel2d)
        _resetPivot(self.configFrame)  
        self.configEntries=[]    
        configHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=self.configFrame)
        _resetPivot(configHide)
        configHide.setTransparency(TransparencyAttrib.MAlpha)
        configHide.setPos(_pos2d(256-32, 128-32))               
        configHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.configEntries, self.configFrame, (224, 0, -96)])
        
        cfg=[('100', 90, 17), ('0.03', 90, 33), ('10', 48, 50), ('5', 140, 50),('1.0', 48, 67), ('0.5', 140, 67),('1.0', 48, 84), ('0.5', 140, 84)]
        for item in cfg:
            entry=DirectEntry(frameSize=_rec2d(64,15),
                              frameColor=(1,1,1, 0.5),
                              text = item[0],
                              text_scale=16,
                              text_pos=(-64,4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              initialText= item[0],
                              numLines = 1,                        
                              focus=0,
                              focusOutCommand=self.getValues,
                              command=self.getValues,
                              parent=self.configFrame)
            _resetPivot(entry)
            entry.setPos(_pos2d(item[1],item[2]))
            self.configEntries.append(entry)
        #blend options
        # A+(1-A)  ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOneMinusIncomingAlpha)
        self.colorBlendOptions=DirectOptionMenu(scale=16, 
                                                items=["blend","add"],
                                                initialitem=0,
                                                popupMarker_scale=1,
                                                parent=self.configFrame
                                                )        
        self.colorBlendOptions.setPos(_pos2d(52,116))
        self.EmitterOptions=DirectOptionMenu(scale=16, 
                                                items=["BoxEmitter","DiscEmitter","LineEmitter","PointEmitter","RectangleEmitter","RingEmitter","SphereSurfaceEmitter","SphereVolumeEmitter","TangentRingEmitter"],
                                                initialitem=1,
                                                popupMarker_scale=1,
                                                command=self.setEmiter,
                                                parent=self.configFrame
                                                )        
        self.EmitterOptions.setPos(_pos2d(58,12))
        #emiter props
        self.propFrame=DirectFrame(frameSize=_rec2d(512,128),
                                 frameColor=(0,0,0,0.5),
                                 text='Velocity:                                                           x:                   +/-\n    Inner:                                                    Outer:\nMin:                                                              Max:\nRadius:                                                            +/-\nAngle:\n    Inner:                                                    Outer:',
                                 text_scale=16,          
                                 text_pos=(-512,128-16),
                                 text_align=TextNode.ALeft,
                                 text_fg=(1,1,1,1),
                                 parent=pixel2d)
        _resetPivot(self.propFrame)
        self.propFrame.setPos(_pos2d(256,0))
        self.propsEntries=[]
        props=[("1.0", 70, 4),("1.0", 135, 4),("1.0", 200, 4), ("1.0", 318, 4),("0.0", 418, 4),
              ("1.0", 70, 20),("1.0", 318, 20),
              ("1.0", 70, 36),("1.0", 135, 36),("1.0", 200, 36),("1.0", 318, 36),("1.0", 383, 36),("1.0", 448, 36),
              ("1.0", 70, 52),("1.0", 318, 52),
              ("1.0", 70, 68),
              ("1.0", 70, 84),("1.0", 318, 84)]
        for item in props:
            entry=DirectEntry(frameSize=_rec2d(64,15),
                              frameColor=(1,1,1, 0.5),
                              text = item[0],
                              text_scale=16,
                              text_pos=(-64,4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              initialText= item[0],
                              numLines = 1,                        
                              focus=0,
                              focusOutCommand=self.getValues,
                              command=self.getValues,
                              parent=self.propFrame)
            _resetPivot(entry)
            entry.setPos(_pos2d(item[1],item[2]))
            self.propsEntries.append(entry)
        self.propsEntries.append(DirectFrame(frameSize=_rec2d(128,20),
                                             frameColor=(0,0,0,0.5),
                                             state=DGG.NORMAL,
                                             text="[Explicit]",
                                             text_scale=16,          
                                             text_pos=(-96,8),
                                             text_align=TextNode.ALeft,
                                             text_fg=(1,1,1,1),
                                             parent=self.propFrame)) 
        _resetPivot(self.propsEntries[-1])
        self.propsEntries[-1].setPos(_pos2d(56,104))
        self.propsEntries[-1].bind(DGG.B1PRESS, self.setMode, [3])
        self.propsEntries.append(DirectFrame(frameSize=_rec2d(128,20),
                                             state=DGG.NORMAL,
                                             frameColor=(0,0,0,0.5),
                                             text="[Radiate]",
                                             text_scale=16,          
                                             text_pos=(-96,8),
                                             text_align=TextNode.ALeft,
                                             text_fg=(1,1,1,1),
                                             parent=self.propFrame)) 
        _resetPivot(self.propsEntries[-1])
        self.propsEntries[-1].setPos(_pos2d(192,104))
        self.propsEntries[-1].bind(DGG.B1PRESS, self.setMode, [2])
        self.propsEntries.append(DirectFrame(frameSize=_rec2d(128,20),
                                             state=DGG.NORMAL,
                                             frameColor=(0,0,0,0.5),
                                             text="[Custom]",
                                             text_scale=16,          
                                             text_pos=(-96,8),
                                             text_align=TextNode.ALeft,
                                             text_fg=(1,1,1,1),
                                             parent=self.propFrame)) 
        _resetPivot(self.propsEntries[-1])
        self.propsEntries[-1].setPos(_pos2d(328,104))
        self.propsEntries[-1].bind(DGG.B1PRESS, self.setMode, [1])
        
        propsHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=self.propFrame)
        _resetPivot(propsHide)
        propsHide.setTransparency(TransparencyAttrib.MAlpha)
        propsHide.setPos(_pos2d(512-32, 128-32))               
        propsHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.propsEntries, self.propFrame, (0, 0, -98)])
        
        #forces
        forceFrame=DirectFrame(frameSize=_rec2d(256,300),
                                 frameColor=(0,0,0,0.5),
                                 text='Vector Force:   x:\nXYZ:\n\nJitter Force:     x:\n\nSink Force:        x:\nXYZ:\nRadius:                 Falloff:\n\nSource Force:   x:\nXYZ:\nRadius:                 Falloff:\n\nVortex Force:    x:\nRadius:                 Length:\nCoef:',
                                 text_scale=16,          
                                 text_pos=(-250,300-16),
                                 text_align=TextNode.ALeft,
                                 text_fg=(1,1,1,1),
                                 parent=pixel2d)
        _resetPivot(forceFrame)
        self.forceEntries=[]
        forceFrame.setPos(_pos2d(base.win.getXSize()-256, 0))
        force_cfg=[("0.0",140,4),
                   ("0.0",61,20),("0.0",126,20),("0.0",191,20),
                   ("0.0",140,52),
                   ("0.0",140,84),
                   ("0.0",61,100),("0.0",126,100),("0.0",191,100),
                   ("0.0",61,116),("0.0",191,116),
                   ("0.0",140,147),
                   ("0.0",61,163),("0.0",126,163),("0.0",191,163),
                   ("0.0",61,179),("0.0",191,179),
                   ("0.0",140,211),
                   ("0.0",61,227),("0.0",191,227),
                   ("0.0",61,243)]
        for item in force_cfg:
            entry=DirectEntry(frameSize=_rec2d(64,15),
                              frameColor=(1,1,1, 0.5),
                              text = item[0],
                              text_scale=16,
                              text_pos=(-64,4),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              initialText= item[0],
                              numLines = 1,                        
                              focus=0,
                              focusOutCommand=self.getValues,
                              command=self.getValues,
                              parent=forceFrame)
            _resetPivot(entry)
            entry.setPos(_pos2d(item[1],item[2]))
            self.forceEntries.append(entry)
        self.forceEntries.append(DirectFrame(frameSize=_rec2d(16,16),
                                             frameColor=(1,1,1,1),
                                             frameTexture="weight.png",
                                             state=DGG.NORMAL,
                                             parent=forceFrame)) 
        _resetPivot(self.forceEntries[-1])
        self.forceEntries[-1].setTransparency(TransparencyAttrib.MAlpha)
        self.forceEntries[-1].setPos(_pos2d(220,3))
        self.forceEntries[-1].bind(DGG.B1PRESS, self.setMassFlag, [0, self.forceEntries[-1]])
        self.forceEntries.append(DirectFrame(frameSize=_rec2d(16,16),
                                             frameColor=(1,1,1,1),
                                             frameTexture="weight.png",
                                             state=DGG.NORMAL,
                                             parent=forceFrame)) 
        _resetPivot(self.forceEntries[-1])
        self.forceEntries[-1].setTransparency(TransparencyAttrib.MAlpha)
        self.forceEntries[-1].setPos(_pos2d(220,51))
        self.forceEntries[-1].bind(DGG.B1PRESS, self.setMassFlag, [1, self.forceEntries[-1]])
        self.forceEntries.append(DirectFrame(frameSize=_rec2d(16,16),
                                             frameColor=(1,1,1,1),
                                             frameTexture="weight.png",
                                             state=DGG.NORMAL,
                                             parent=forceFrame)) 
        _resetPivot(self.forceEntries[-1])
        self.forceEntries[-1].setTransparency(TransparencyAttrib.MAlpha)
        self.forceEntries[-1].setPos(_pos2d(220,83))
        self.forceEntries[-1].bind(DGG.B1PRESS, self.setMassFlag, [2, self.forceEntries[-1]])
        self.forceEntries.append(DirectFrame(frameSize=_rec2d(16,16),
                                             frameColor=(1,1,1,1),
                                             frameTexture="weight.png",
                                             state=DGG.NORMAL,
                                             parent=forceFrame)) 
        _resetPivot(self.forceEntries[-1])
        self.forceEntries[-1].setTransparency(TransparencyAttrib.MAlpha)
        self.forceEntries[-1].setPos(_pos2d(220,146))
        self.forceEntries[-1].bind(DGG.B1PRESS, self.setMassFlag, [3, self.forceEntries[-1]])
        self.forceEntries.append(DirectFrame(frameSize=_rec2d(16,16),
                                             frameColor=(1,1,1,1),
                                             frameTexture="weight.png",
                                             state=DGG.NORMAL,
                                             parent=forceFrame)) 
        _resetPivot(self.forceEntries[-1])
        self.forceEntries[-1].setTransparency(TransparencyAttrib.MAlpha)
        self.forceEntries[-1].setPos(_pos2d(220,210))
        self.forceEntries[-1].bind(DGG.B1PRESS, self.setMassFlag, [4, self.forceEntries[-1]]) 
        
        forceHide=DirectFrame(frameSize=_rec2d(32,32),  
                               frameTexture='eye.png',
                               frameColor=(1,1,1,1),
                               state=DGG.NORMAL,
                               parent=forceFrame)
        _resetPivot(forceHide)
        forceHide.setTransparency(TransparencyAttrib.MAlpha)
        forceHide.setPos(_pos2d(0, 268))               
        forceHide.bind(DGG.B1PRESS, self.hideShowButtons,[self.forceEntries, forceFrame, (-224, 0, -268)])
        
        #popup window for selecting a color        
        self.colorPickerFrame=DirectFrame(frameSize=_rec2d(256,256+64),
                              frameColor=(0,0,0,1),
                              text='RGB=',
                              text_scale=16,          
                              text_pos=(-256,48),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)   
        _resetPivot(self.colorPickerFrame)
        #self.colorPickerFrame.setPos(_pos2d(16,16))
        picker=DirectFrame(frameSize=_rec2d(256,256),
                            frameColor=(1,1,1,1),
                            state=DGG.NORMAL,
                            frameTexture='color_picker.png',
                            parent=self.colorPickerFrame)
        _resetPivot(picker)
        picker.bind(DGG.B1PRESS, self.pickColor)
        self.sample=DirectFrame(frameSize=_rec2d(32,32),frameColor=(1,1,1,1),parent=self.colorPickerFrame)
        _resetPivot(self.sample)  
        self.sample.setPos(_pos2d(222, 258))
        self.colorEntry=DirectEntry(frameSize=_rec2d(128,22),
                        frameColor=(1,1,1, 0.5),
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
                                 frameColor=(1,1,1,0.5),
                                 text='Set Color',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.colorPickerFrame)
        _resetPivot(self.colorOk)  
        self.colorOk.setPos(_pos2d(2, 292))
        self.colorOk.bind(DGG.B1PRESS, self.setColor)
        self.colorCancel=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.5),
                                 text='Remove Color',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.colorPickerFrame)
        _resetPivot(self.colorCancel)  
        self.colorCancel.setPos(_pos2d(124, 292))
        self.colorCancel.bind(DGG.B1PRESS, self.cancelColor)
        self.colorPickerFrame.hide()
        
        #popup window for selecting alpha
        self.alphaPickerFrame=DirectFrame(frameSize=_rec2d(256,128),
                              frameColor=(0,0,0,1),
                              text='Alpha=',
                              text_scale=16,          
                              text_pos=(-256,48),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)   
        _resetPivot(self.alphaPickerFrame)
        #self.colorPickerFrame.setPos(_pos2d(16,16))
        a_picker=DirectFrame(frameSize=_rec2d(256,64),
                            frameColor=(1,1,1,1),
                            state=DGG.NORMAL,
                            frameTexture='alpha_picker.png',
                            parent=self.alphaPickerFrame)
        _resetPivot(a_picker)
        a_picker.bind(DGG.B1PRESS, self.pickAlpha)    
        self.alphaEntry=DirectEntry(frameSize=_rec2d(128,22),
                        frameColor=(1,1,1, 0.5),
                        text = "0.5",
                        text_scale=16,
                        text_pos=(-128,8),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText= "0.5",
                        numLines = 1,                        
                        focus=1,
                        parent=self.alphaPickerFrame,
                        )
        _resetPivot(self.alphaEntry)
        self.alphaEntry.setPos(_pos2d(56,66))
        self.alphaOk=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.5),
                                 text='Set Alpha',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.alphaPickerFrame)
        _resetPivot(self.alphaOk)  
        self.alphaOk.setPos(_pos2d(2, 96))
        self.alphaOk.bind(DGG.B1PRESS, self.setAlpha)
        self.alphaCancel=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.5),
                                 text='Remove Alpha',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.alphaPickerFrame)
        _resetPivot(self.alphaCancel)  
        self.alphaCancel.setPos(_pos2d(124, 96))
        self.alphaCancel.bind(DGG.B1PRESS, self.cancelAlpha)
        self.alphaPickerFrame.hide()
        
        #popup window for selecting size
        self.sizePickerFrame=DirectFrame(frameSize=_rec2d(256,128),
                              frameColor=(0,0,0,1),
                              text='Size=',
                              text_scale=16,          
                              text_pos=(-256,48),
                              text_align=TextNode.ALeft,
                              text_fg=(1,1,1,1),
                              parent=pixel2d)   
        _resetPivot(self.sizePickerFrame)  
        self.slider = DirectSlider(range=(0.1,19.8),
                                    value=10.0,
                                    pageSize=5,      
                                    thumb_relief=DGG.FLAT,
                                    scale=120,
                                    command=self.getSliderVal,
                                    parent=self.sizePickerFrame) 
       # _resetPivot(self.slider)
        self.slider.setPos(_pos2d(124,32))
        self.sizeEntry=DirectEntry(frameSize=_rec2d(128,22),
                        frameColor=(1,1,1, 0.5),
                        text = "1.0",
                        text_scale=16,
                        text_pos=(-128,8),
                        text_align=TextNode.ALeft,
                        text_fg=(1,1,1,1),
                        initialText= "1.0",
                        numLines = 1,                        
                        focus=1,
                        parent=self.sizePickerFrame,
                        )
        _resetPivot(self.sizeEntry)
        self.sizeEntry.setPos(_pos2d(56,64))
        self.sizeOk=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.5),
                                 text='Set Size',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.sizePickerFrame)
        _resetPivot(self.sizeOk)  
        self.sizeOk.setPos(_pos2d(2, 96))
        self.sizeOk.bind(DGG.B1PRESS, self.setSize)
        self.sizeCancel=DirectFrame(frameSize=_rec2d(120,24),
                                 frameColor=(1,1,1,0.5),
                                 text='Remove Size',
                                 text_scale=16,          
                                 text_pos=(-60,10),
                                 text_align=TextNode.ACenter,
                                 text_fg=(1,1,1,1),
                                 state=DGG.NORMAL,
                                 parent=self.sizePickerFrame)
        _resetPivot(self.sizeCancel)  
        self.sizeCancel.setPos(_pos2d(124, 96))
        self.sizeCancel.bind(DGG.B1PRESS, self.cancelSize)
        self.sizePickerFrame.hide()
        #popup with shapes
        self.shapePickerFrame=DirectFrame(frameSize=_rec2d(512,512),
                              frameColor=(0,0,0,0.5),
                              parent=pixel2d)   
        _resetPivot(self.shapePickerFrame)
        self.shapePickerFrame.setPos(_pos2d(base.win.getXSize()/2-256, 0))
        self.shapePickerButtons=[]
        self.shapeTex=[]
        dirList=listdir(Filename("tex/").toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('png', 'tga', 'dds'):
                self.shapeTex.append("tex/"+fname)
        k=0
        for i in range(8):
            for j in range(8):                
                f=DirectFrame(frameSize=_rec2d(64,64),
                              frameColor=(1,1,1,1),
                              state=DGG.NORMAL,
                              parent=self.shapePickerFrame,
                              frameTexture=self.shapeTex[k])
                _resetPivot(f)
                f.setPos(_pos2d(i*64, j*64))
                f.bind(DGG.B1PRESS, self.setShape,[k])
                self.shapePickerButtons.append(f)
                k+=1          
        self.shapePickerFrame.hide()  
        
        self.getValues()
        self.setMode(3)
        #self.restartParticles()

    def export(self, event=None):
        self.saveDir=self.saveEntry.get()
        dir=dirname(self.saveDir)
        print dir
        if not exists(dir):
           makedirs(dir)   
        self.values['color_gradient']=self.saveDir+"_color.png"
        self.values['size_gradient']=self.saveDir+"_size.png"
        self.values['shape_gradient']=self.saveDir+"_shape.png"
        self.values['distortion']=0.0
        self.currentColorGradient.write(self.saveDir+"_color.png")
        self.currentSizeGradient.write(self.saveDir+"_size.png")
        self.currentShapeGradient.write(self.saveDir+"_shape.png")
        with open(self.saveDir+".json", 'w') as outfile:
            json.dump(self.values, outfile, indent=4, separators=(',', ': '), sort_keys=True)
        if self.saveButton['text']=="Saved!":
            self.saveButton['text']="Saved Again!"
        else:
            self.saveButton['text']="Saved!"
           
        
    def setMassFlag(self, id, button, event=None):
        if self.massDependant[id]==1:
            self.massDependant[id]=0
            button['frameColor']=(0.5, 0.5, 0.5, 1)
        else:
            self.massDependant[id]=1
            button['frameColor']=(1, 1, 1, 1)
    
    def getValues(self, event=None):
        self.values["pool"]=self.configEntries[0].get()
        self.values["birthRate"]=self.configEntries[1].get()
        self.values["litter"]=self.configEntries[2].get()
        self.values["litterSpread"]=self.configEntries[3].get()
        self.values["life"]=self.configEntries[4].get()
        self.values["lifeSpread"]=self.configEntries[5].get()
        self.values["mass"]=self.configEntries[6].get()
        self.values["massSpread"]=self.configEntries[7].get()
        self.values["emiter"]=self.EmitterOptions.get()
        self.values["colorBlend"]=self.colorBlendOptions.get()
        self.values["offsetForce"]=[self.propsEntries[0].get(),self.propsEntries[1].get(),self.propsEntries[2].get()]
        self.values["amplitude"]=self.propsEntries[3].get()
        self.values["amplitudeSpread"]=self.propsEntries[4].get()
        self.values["innerMagnitude"]=self.propsEntries[5].get()
        self.values["outerMagnitude"]=self.propsEntries[6].get()
        self.values["min"]=[self.propsEntries[7].get(),self.propsEntries[8].get(),self.propsEntries[9].get()]
        self.values["max"]=[self.propsEntries[10].get(),self.propsEntries[11].get(),self.propsEntries[12].get()]
        self.values["radius"]=self.propsEntries[13].get()
        self.values["radiusSpread"]=self.propsEntries[14].get()
        self.values["angle"]=self.propsEntries[15].get()
        self.values["innerAngle"]=self.propsEntries[16].get()
        self.values["outerAngle"]=self.propsEntries[17].get()
        self.values["forceVector"]=[self.forceEntries[1].get(),self.forceEntries[2].get(),self.forceEntries[3].get(),self.forceEntries[0].get(),self.massDependant[0]]
        self.values["forceJitter"]=[self.forceEntries[4].get(),self.massDependant[1]]
        self.values["forceSink"]=[self.forceEntries[6].get(),self.forceEntries[7].get(),self.forceEntries[8].get(),self.forceEntries[10].get(),self.forceEntries[9].get(), self.forceEntries[5].get(),self.massDependant[2]]
        self.values["forceSource"]=[self.forceEntries[12].get(),self.forceEntries[13].get(),self.forceEntries[14].get(),self.forceEntries[16].get(),self.forceEntries[14].get(), self.forceEntries[11].get(),self.massDependant[3]]
        self.values["forceVertex"]=[self.forceEntries[18].get(),self.forceEntries[19].get(),self.forceEntries[20].get(), self.forceEntries[17].get(),self.massDependant[4]]
        
        #corect the values if the user put someting stupid in
        try:
            self.values["pool"]=int(self.values["pool"])
            if self.values["pool"]<1:
                self.values["pool"]=1
        except:
            self.values["pool"]=100
        try:
            self.values["birthRate"]=round(float(self.values["birthRate"]), 5)
        except:
            self.values["birthRate"]=0.033
        try:
            self.values["litter"]=int(self.values["litter"])
        except:
            self.values["litter"]=10
        try:
            self.values["litterSpread"]=int(self.values["litterSpread"])
        except:
            self.values["litterSpread"]=1
        try:
            self.values["life"]=float(self.values["life"])
        except:
            self.values["life"]=1.0
        try:
            self.values["lifeSpread"]=float(self.values["lifeSpread"])
        except:
            self.values["lifeSpread"]=0.0
        try:
            self.values["mass"]=float(self.values["mass"])
            if self.values["mass"]<=0.0:
                self.values["mass"]=0.01
            if self.values["mass"]>self.values["massSpread"]:
                self.values["massSpread"]=0.0                
        except:
            self.values["mass"]=1.0
        try:
            self.values["massSpread"]=float(self.values["massSpread"])
            if self.values["massSpread"]>=self.values["mass"]-0.01:
                self.values["massSpread"]=self.values["mass"]-0.01
        except:
            self.values["massSpread"]=0.0
        try:
            self.values["offsetForce"][0]=float(self.values["offsetForce"][0])
            self.values["offsetForce"][1]=float(self.values["offsetForce"][1])
            self.values["offsetForce"][2]=float(self.values["offsetForce"][2])            
        except:
            self.values["offsetForce"]=[0.0, 0.0, 0.0]
        try:
            self.values["amplitude"]=float(self.values["amplitude"])
        except:
            self.values["amplitude"]=1.0
        try:
            self.values["amplitudeSpread"]=float(self.values["amplitudeSpread"])
        except:
            self.values["amplitudeSpread"]=0.0
        try:
            self.values["innerMagnitude"]=float(self.values["innerMagnitude"])
        except:
            self.values["innerMagnitude"]=1.0
        try:
            self.values["outerMagnitude"]=float(self.values["outerMagnitude"])
        except:
            self.values["outerMagnitude"]=1.0
        try:
            self.values["min"][0]=float(self.values["min"][0])
            self.values["min"][1]=float(self.values["min"][1])
            self.values["min"][2]=float(self.values["min"][2])
        except:
            self.values["min"]=[0.0, 0.0, 0.0]
        try:
            self.values["max"][0]=float(self.values["max"][0])
            self.values["max"][1]=float(self.values["max"][1])
            self.values["max"][2]=float(self.values["max"][2])
        except:
            self.values["max"]=[0.0, 0.0, 1.0]    
        try:
            self.values["radius"]=float(self.values["radius"])
        except:
            self.values["radius"]=1.0
        try:
            self.values["radiusSpread"]=float(self.values["radiusSpread"])
        except:
            self.values["radiusSpread"]=1.0            
        try:
            self.values["angle"]=float(self.values["angle"])
        except:
            self.values["angle"]=1.0
        try:
            self.values["innerAngle"]=float(self.values["innerAngle"])
        except:
            self.values["innerAngle"]=1.0
        try:
            self.values["outerAngle"]=float(self.values["outerAngle"])
        except:
            self.values["outerAngle"]=1.0
        try:
            self.values["forceVector"][0]=float(self.values["forceVector"][0])
            self.values["forceVector"][1]=float(self.values["forceVector"][1])
            self.values["forceVector"][2]=float(self.values["forceVector"][2])
            self.values["forceVector"][3]=float(self.values["forceVector"][3])
        except:
            self.values["forceVector"]=[0.0, 0.0, 0.0, 1.0, 0]
        try:
            self.values["forceJitter"][0]=float(self.values["forceJitter"][0])
        except:
            self.values["forceJitter"]=[0.0, 0]    
        try:
            self.values["forceSink"][0]=float(self.values["forceSink"][0])
            self.values["forceSink"][1]=float(self.values["forceSink"][1])
            self.values["forceSink"][2]=float(self.values["forceSink"][2])
            self.values["forceSink"][3]=int(self.values["forceSink"][3])
            if self.values["forceSink"][3] not in (0,1,2):
                self.values["forceSink"][3]=1
            self.values["forceSink"][4]=float(self.values["forceSink"][4])
            self.values["forceSink"][5]=float(self.values["forceSink"][5])
        except:
            self.values["forceSink"]=[0.0, 0.0, 0.0, 1, 1.0, 0.0, 1]    
        try:
            self.values["forceSource"][0]=float(self.values["forceSource"][0])
            self.values["forceSource"][1]=float(self.values["forceSource"][1])
            self.values["forceSource"][2]=float(self.values["forceSource"][2])
            self.values["forceSource"][3]=int(self.values["forceSource"][3])
            if self.values["forceSource"][3] not in (0,1,2):
                self.values["forceSource"][3]=1
            self.values["forceSource"][4]=float(self.values["forceSource"][4])
            self.values["forceSource"][5]=float(self.values["forceSource"][5])
        except:
            self.values["forceSource"]=[0.0, 0.0, 0.0, 1, 1.0, 0.0, 1]            
        try:
            self.values["forceVertex"][0]=float(self.values["forceVertex"][0])
            self.values["forceVertex"][1]=float(self.values["forceVertex"][1])
            self.values["forceVertex"][2]=float(self.values["forceVertex"][2])
            self.values["forceVertex"][3]=float(self.values["forceVertex"][3])
        except:
            self.values["forceVertex"]=[1.0, 1.0, 1.0, 1.0, 1] 
                
        #for key in self.values:
        #    print key, self.values[key]
            
        #put back the values
        self.configEntries[0].set(str(self.values["pool"]))
        self.configEntries[1].set(str(self.values["birthRate"]))
        self.configEntries[2].set(str(self.values["litter"]))
        self.configEntries[3].set(str(self.values["litterSpread"]))
        self.configEntries[4].set(str(self.values["life"]))
        self.configEntries[5].set(str(self.values["lifeSpread"]))
        self.configEntries[6].set(str(self.values["mass"]))
        self.configEntries[7].set(str(self.values["massSpread"]))
        #self.values["emiter"]=self.EmitterOptions.get()
        #self.values["colorBlend"]=self.colorBlendOptions.get()
        self.propsEntries[0].set(str(self.values["offsetForce"][0]))
        self.propsEntries[1].set(str(self.values["offsetForce"][1]))
        self.propsEntries[2].set(str(self.values["offsetForce"][2]))
        self.propsEntries[3].set(str(self.values["amplitude"]))
        self.propsEntries[4].set(str(self.values["amplitudeSpread"]))
        self.propsEntries[5].set(str(self.values["innerMagnitude"]))
        self.propsEntries[6].set(str(self.values["outerMagnitude"]))        
        self.propsEntries[7].set(str(self.values["min"][0]))
        self.propsEntries[8].set(str(self.values["min"][1]))
        self.propsEntries[9].set(str(self.values["min"][2]))        
        self.propsEntries[10].set(str(self.values["max"][0]))
        self.propsEntries[11].set(str(self.values["max"][1]))
        self.propsEntries[12].set(str(self.values["max"][2]))
        self.propsEntries[13].set(str(self.values["radius"]))
        self.propsEntries[14].set(str(self.values["radiusSpread"]))
        self.propsEntries[15].set(str(self.values["angle"]))        
        self.propsEntries[16].set(str(self.values["innerAngle"]))
        self.propsEntries[17].set(str(self.values["outerAngle"]))        
        self.forceEntries[1].set(str(self.values["forceVector"][0]))
        self.forceEntries[2].set(str(self.values["forceVector"][1]))
        self.forceEntries[3].set(str(self.values["forceVector"][2]))
        self.forceEntries[0].set(str(self.values["forceVector"][3]))
        self.forceEntries[4].set(str(self.values["forceJitter"][0]))        
        self.forceEntries[6].set(str(self.values["forceSink"][0]))
        self.forceEntries[7].set(str(self.values["forceSink"][1]))
        self.forceEntries[8].set(str(self.values["forceSink"][2]))
        self.forceEntries[10].set(str(self.values["forceSink"][3]))
        self.forceEntries[9].set(str(self.values["forceSink"][4]))
        self.forceEntries[5].set(str(self.values["forceSink"][5]))        
        self.forceEntries[12].set(str(self.values["forceSource"][0]))
        self.forceEntries[13].set(str(self.values["forceSource"][1]))
        self.forceEntries[14].set(str(self.values["forceSource"][2]))
        self.forceEntries[16].set(str(self.values["forceSource"][3]))
        self.forceEntries[14].set(str(self.values["forceSource"][4]))
        self.forceEntries[11].set(str(self.values["forceSource"][5]))       
        self.forceEntries[18].set(str(self.values["forceVertex"][0]))
        self.forceEntries[19].set(str(self.values["forceVertex"][1]))
        self.forceEntries[20].set(str(self.values["forceVertex"][2]))
        self.forceEntries[17].set(str(self.values["forceVertex"][3]))   
        if  'mode' in  self.values:        
            self.restartParticles()
            #with open(self.saveDir+"/effect.json", 'w') as outfile:
            #    json.dump(self.values, outfile, indent=4, separators=(',', ': '), sort_keys=True)
            
    def setEmiter(self, arg=None):
        self.setMode(3)
        
    def setMode(self, mode, event=None):        
        self.propsEntries[-mode]['frameColor']=(1,1,1, 0.5)
        self.propsEntries[-mode]['state']='disabled'
        
        emiter_mode=self.EmitterOptions.get()
        #what options to hide
        # 0=offsetForce x
        # 1=offsetForce y
        # 2=offsetForce z
        # 3=amplitude
        # 4=amplitudeSpread
        # 5=innerMagnitude
        # 6=outerMagnitude
        # 7=min x
        # 8=min y
        # 9=min z
        # 10=max x
        # 11=max y
        # 12=max z
        # 13=radius
        # 14=radiusSpread
        # 15=angle
        # 16=outerAngle
        # 17=outerAngle
        #would be easier to list what to show.. well, too late now
        what_to_hide={"BoxEmitter":[(5,6,13,14,15,16,17),(5,6,13,14,15,16,17),(5,6,13,14,15,16,17)],
                      "DiscEmitter":[(7,8,9,10,11,12,14,15),(5,6,7,8,9,10,11,12,14,15,16,17),(5,6,7,8,9,10,11,12,14,15,16,17)],
                      "LineEmitter":[(5,6,13,14,15,16,17),(5,6,13,14,15,16,17),(5,6,13,14,15,16,17)],
                      "PointEmitter":[(5,6,7,8,9,10,11,12,13,14,15,16,17),(5,6,7,8,9,10,11,12,13,14,15,16,17),(5,6,7,8,9,10,11,12,13,14,15,16,17)],
                      "RectangleEmitter":[(5,6,13,14,15,16,17),(5,6,13,14,15,16,17),(5,6,13,14,15,16,17)],
                      "RingEmitter":[(5,6,7,8,9,10,11,12,16,17),(5,6,7,8,9,10,11,12,15,16,17),(5,6,7,8,9,10,11,12,15,16,17)],
                      "SphereSurfaceEmitter":[(5,6,7,8,9,10,11,12,14,15,16,17),(5,6,7,8,9,10,11,12,14,15,16,17),(5,6,7,8,9,10,11,12,14,15,16,17)],
                      "SphereVolumeEmitter":[(5,6,7,8,9,10,11,12,14,15,16,17),(5,6,7,8,9,10,11,12,14,15,16,17),(5,6,7,8,9,10,11,12,14,15,16,17)],
                      "TangentRingEmitter":[(5,6,7,8,9,10,11,12,15,16,17),(5,6,7,8,9,10,11,12,15,16,17),(5,6,7,8,9,10,11,12,15,16,17)]
                     }
        for i in range(18):
            if i in what_to_hide[emiter_mode][mode-1]:
                self.propsEntries[i].hide()
            else:
                self.propsEntries[i].show()
        if mode  ==3: #Explicit
            self.values["mode"]=0
            self.propsEntries[-2]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-2]['state']='normal'
            self.propsEntries[-1]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-1]['state']='normal'
        elif mode==2: #Radiate
            self.values["mode"]=1
            self.propsEntries[-3]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-3]['state']='normal'
            self.propsEntries[-1]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-1]['state']='normal'
        elif mode==1: #Custom   
            self.values["mode"]=2
            self.propsEntries[-2]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-2]['state']='normal'
            self.propsEntries[-3]['frameColor']=(0,0,0, 0.5)
            self.propsEntries[-3]['state']='normal'   
        #self.restartParticles()
        self.getValues()
        
    def hideShowButtons(self, buttonList, frame=None, pos=None, event=None):
        if buttonList[0].isHidden():
            for button in buttonList:
                button.show()  
            if frame:
                if pos==None:
                    pos=(base.win.getXSize()-32, 0,0)
                frame.setPos(frame, pos)    
        else:        
            for button in buttonList:
                button.hide()
            if frame:
                if pos==None:
                   pos=[base.win.getXSize()-32, 0,0]                   
                pos=Vec3(-pos[0], 0,-pos[2]) 
                frame.setPos(frame, pos)    
                
    def setShape(self, texID, event=None):
        self.shapePickerFrame.hide()
        self.shapeButtons[self.current_id]['frameTexture']=self.shapeTex[texID]
        img=PNMImage(512, 64, 3)
        for i in range(8):
            new= PNMImage()    
            new.read(self.shapeButtons[i]['frameTexture']) 
            img.copySubImage(new, 64*i, 0, 0, 0, 64, 64)
            
        #img.write(self.saveDir+'/shape.png')
        tex = Texture()
        tex.load(img)  
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        loader.unloadTexture(self.currentShapeGradient)
        #self.currentShapeGradient=loader.loadTexture(self.saveDir+'/shape.png')
        #self.currentShapeGradient.setWrapU(Texture.WMClamp)
        #self.currentShapeGradient.setWrapV(Texture.WMClamp) 
        self.currentShapeGradient=tex
        #self.values["shape_gradient"]='shape.png'
        #self.p.cleanup()            
        self.restartParticles(shape_gradient=tex)
        
        
    def makeSizeGradient(self, event=None):
        img=PNMImage(64,1,1)
        if len(self.activeSizes)==0:
            img.fill(1.0)            
        elif len(self.activeSizes)==1:
            a=self.sizeButtons[self.activeSizes[0]]['frameColor'][0]
            img.fill(a)
            for button in self.sizeButtons:
                button['frameColor']=(a, a, a, 1.0)
                button.setShaderInput('size', a) 
        else:
            active=sorted(self.activeSizes)
            current=active[0]
            next=active[1]
            id=2
            for i in range(64):
                if i<=current:           
                    color=self.sizeButtons[current]['frameColor']
                    self.sizeButtons[i]['frameColor']=color
                    self.sizeButtons[i].setShaderInput('size', color[0])                    
                    img.setXel(i, 0, color[0])
                elif i==next:
                    current=next
                    if len(active)>id:
                        next=active[id]
                        id+=1                        
                    color=self.sizeButtons[current]['frameColor']
                    self.sizeButtons[i]['frameColor']=color
                    self.sizeButtons[i].setShaderInput('size', color[0])
                    img.setXel(i, 0, color[0])
                elif i<next:
                    color1=self.sizeButtons[current]['frameColor']
                    color2=self.sizeButtons[next]['frameColor']                    
                    distance=1.0-(float(i-current)/float(next-current))                    
                    a=linstep(color1[0], color2[0], distance)
                    self.sizeButtons[i]['frameColor']=color                      
                    self.sizeButtons[i].setShaderInput('size', a)
                    img.setXel(i, 0, a)
                elif i>next:
                    color=self.sizeButtons[next]['frameColor']
                    self.sizeButtons[i]['frameColor']=color
                    self.sizeButtons[i].setShaderInput('size', color[0])
                    img.setXel(i, 0, color[0])    
        #img.write(self.saveDir+'/size.png')
        tex = Texture()
        tex.load(img)
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        loader.unloadTexture(self.currentSizeGradient)
        #self.currentSizeGradient=loader.loadTexture(self.saveDir+'/size.png')
        #self.currentSizeGradient.setWrapU(Texture.WMClamp)
        #self.currentSizeGradient.setWrapV(Texture.WMClamp) 
        #self.values["size_gradient"]='size.png'
        self.currentSizeGradient=tex
        #self.p.cleanup()            
        self.restartParticles(None, tex)
        
    def makeGradient(self, event=None):
        img=PNMImage(64,1,4)        
        #color
        if len(self.activeColors)==0:
            color=(1,1,1,1)
            img.fill(1.0, 1.0, 1.0) 
            for button in self.colorButtons:
                button['frameColor']=color                
                button.setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0)) 
        elif len(self.activeColors)==1:
            color=self.colorButtons[self.activeColors[0]]['frameColor']
            img.fill(color[0], color[1], color[2])
            for button in self.colorButtons:
                button['frameColor']=color
                button.setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0)) 
        else:
            active=sorted(self.activeColors)
            current=active[0]
            next=active[1]
            id=2            
            for i in range(64):
                if i<=current:           
                    color=self.colorButtons[current]['frameColor']
                    self.colorButtons[i]['frameColor']=color
                    self.colorButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setXel(i, 0, color[0], color[1], color[2])
                elif i==next:
                    current=next
                    if len(active)>id:
                        next=active[id]
                        id+=1                        
                    color=self.colorButtons[current]['frameColor']
                    self.colorButtons[i]['frameColor']=color
                    self.colorButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setXel(i, 0, color[0], color[1], color[2])
                elif i<next:
                    color1=self.colorButtons[current]['frameColor']
                    color2=self.colorButtons[next]['frameColor']
                    #distance=float(next-i)/float(next)  
                    distance=1.0-(float(i-current)/float(next-current))                    
                    color=(linstep(color1[0], color2[0], distance),
                           linstep(color1[1], color2[1], distance),
                           linstep(color1[2], color2[2], distance),
                            1.0)                    
                    self.colorButtons[i]['frameColor']=color                      
                    self.colorButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setXel(i, 0, color[0], color[1], color[2])
                elif i>next:
                    color=self.colorButtons[next]['frameColor']
                    self.colorButtons[i]['frameColor']=color
                    self.colorButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setXel(i, 0, color[0], color[1], color[2])
        #alpha
        if len(self.activeAlphas)==0:
            img.alphaFill(1.0)            
        elif len(self.activeAlphas)==1:
            a=self.alphaButtons[self.activeAlphas[0]]['frameColor'][0]
            img.alphaFill(a)
            for button in self.alphaButtons:
                button['frameColor']=color
                button.setShaderInput('glsl_color', Vec4(a, a, a, 1.0)) 
        else:
            active=sorted(self.activeAlphas)
            current=active[0]
            next=active[1]
            id=2
            for i in range(64):
                if i<=current:           
                    color=self.alphaButtons[current]['frameColor']
                    self.alphaButtons[i]['frameColor']=color
                    self.alphaButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setAlpha(i, 0, color[0])
                elif i==next:
                    current=next
                    if len(active)>id:
                        next=active[id]
                        id+=1                        
                    color=self.alphaButtons[current]['frameColor']
                    self.alphaButtons[i]['frameColor']=color
                    self.alphaButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setAlpha(i, 0, color[0])
                elif i<next:
                    color1=self.alphaButtons[current]['frameColor']
                    color2=self.alphaButtons[next]['frameColor']
                    #distance=float(next-i)/float(next) 
                    distance=1.0-(float(i-current)/float(next-current))    
                    a=linstep(color1[0], color2[0], distance)
                    self.alphaButtons[i]['frameColor']=color                      
                    self.alphaButtons[i].setShaderInput('glsl_color', Vec4(a, a, a, 1.0))
                    img.setAlpha(i, 0, a)
                elif i>next:
                    color=self.alphaButtons[next]['frameColor']
                    self.alphaButtons[i]['frameColor']=color
                    self.alphaButtons[i].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))
                    img.setAlpha(i, 0, color[0])    
        #img.write(self.saveDir+'/color.png')
        tex = Texture()
        tex.load(img)
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        loader.unloadTexture(self.currentColorGradient)        
        self.currentColorGradient=tex
        #self.currentColorGradient=loader.loadTexture(self.saveDir+'/color.png')
        #self.currentColorGradient.setWrapU(Texture.WMClamp)
        #self.currentColorGradient.setWrapV(Texture.WMClamp) 
        #self.values["color_gradient"]='color.png'        
        #self.p.cleanup()            
        self.restartParticles(tex)  
    
    def getSliderVal(self, event=None):
        v=float(self.slider['value'])
        self.sizeEntry.set(str(round(v, 3)))
    
    def cancelSize(self, event=None):
        self.sizePickerFrame.hide()
        self.sizeButtons[self.current_id].setShaderInput('size', 0.5)
        self.sizeButtons[self.current_id]['frameTexture']='no_size.png'
        if self.current_id in self.activeSizes:
            self.activeSizes.pop(self.activeSizes.index(self.current_id))
        self.makeSizeGradient()
       
    def setSize(self, event=None):
        s=1.0
        try:
            s=float(self.sizeEntry.get())/20.0
        except:
            s=0.5
        s=clamp(s)
        self.sizeButtons[self.current_id]['frameColor']=(s, s, s, 1.0)
        self.sizeButtons[self.current_id]['frameTexture']='size.png'
        self.sizePickerFrame.hide()        
        self.sizeButtons[self.current_id].setShaderInput('size', s)
        if self.current_id not in self.activeSizes:
            self.activeSizes.append(self.current_id)
        self.makeSizeGradient()
        
    def cancelAlpha(self, event=None):                
        self.alphaPickerFrame.hide()
        self.alphaButtons[self.current_id]['frameTexture']='no_mark.png'
        if self.current_id in self.activeAlphas:
            self.activeAlphas.pop(self.activeAlphas.index(self.current_id))
        self.makeGradient()
            
    def setAlpha(self, event=None):        
        a=float(self.alphaEntry.get())
        self.alphaButtons[self.current_id]['frameTexture']='mark.png'
        self.alphaButtons[self.current_id]['frameColor']=(a, a, a, 1.0)
        self.alphaPickerFrame.hide()        
        self.alphaButtons[self.current_id].setShaderInput('glsl_color', Vec4(a, a, a, 1.0))
        if self.current_id not in self.activeAlphas:
            self.activeAlphas.append(self.current_id)
        self.makeGradient()

    
    def cancelColor(self, event=None):                
        self.colorPickerFrame.hide()
        self.colorButtons[self.current_id]['frameTexture']='no_mark.png'
        if self.current_id in self.activeColors:
            self.activeColors.pop(self.activeColors.index(self.current_id))
        self.makeGradient()
            
    def setColor(self, event=None):        
        self.colorButtons[self.current_id]['frameTexture']='mark.png'
        self.colorButtons[self.current_id]['frameColor']=self.sample['frameColor']
        color=self.sample['frameColor']                    
        self.colorButtons[self.current_id].setShaderInput('glsl_color', Vec4(color[0], color[1], color[2], 1.0))        
        self.colorPickerFrame.hide()
        if self.current_id not in self.activeColors:
            self.activeColors.append(self.current_id)
        self.makeGradient()    
        
    def overrideColor(self, text=None):
        color=str(self.colorEntry.get())
        try:
            pixel=astEval(color)  
            self.sample['frameColor']=(pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0, 1.0)            
        except:
            print "Unknown format!" 
            
    def pickAlpha(self, event=None):        
        mpos=Vec2(event.getMouse()[0], event.getMouse()[1])                
        mpos+=(1, -1)
        mpos[0]*=base.win.getXSize()/2
        mpos[1]*=-1*base.win.getYSize()/2
        mpos[0]=max(1, mpos[0])
        mpos[1]=max(1, mpos[1])
        img=PNMImage('alpha_picker.png')
        try:
            pixel=img.getPixel(int(mpos[0]), int(mpos[1]))
            pixel=float(pixel[0])
            self.alphaEntry.set(str(round(pixel/255.0, 3)))
        except:
            print "Pixel out of range, try again!"
    
    def pickColor(self, event=None):        
        mpos=Vec2(event.getMouse()[0], event.getMouse()[1])                
        mpos+=(1, -1)
        mpos[0]*=base.win.getXSize()/2
        mpos[1]*=-1*base.win.getYSize()/2
        mpos[0]=max(1, mpos[0])
        mpos[1]=max(1, mpos[1])
        img=PNMImage('color_picker.png')
        try:            
            pixel=img.getPixel(int(mpos[0]), int(mpos[1]))
            pixel=[pixel[0],pixel[1], pixel[2]]
            self.colorEntry.set('{0}, {1}, {2}'.format(*pixel))
            self.sample['frameColor']=(pixel[0]/255.0, pixel[1]/255.0, pixel[2]/255.0, 1.0)
        except:
            print "Pixel out of range, try again!"
            
    def shapeSetup(self, id, event=None):    
        self.shapePickerFrame.show()
        self.current_id=id
        
    def alphaSetup(self, id, event=None):    
        self.alphaPickerFrame.show() 
        self.current_id=id
        
    def colorSetup(self, id, event=None):    
        self.colorPickerFrame.show() 
        self.current_id=id
        
    def sizeSetup(self, id, event=None):    
        self.sizePickerFrame.show() 
        self.current_id=id  
        
    def restartParticles(self, color_gradient=None, size_gradient=None, shape_gradient=None):
        if self.p:
            self.p.cleanup()   
        if color_gradient==None:
            color_gradient=self.currentColorGradient
        if size_gradient==None:
            size_gradient=self.currentSizeGradient
        if shape_gradient==None:
            shape_gradient=self.currentShapeGradient 
            
        self.p = ParticleEffect()
        self.loadValues() 
        for geom in self.p.findAllMatches('**/+GeomNode'):
            geom.setDepthWrite(False)
            geom.setBin("transparent", 31)
            geom.setShader(Shader.load(Shader.SLGLSL, "vfx_v.glsl","vfx_f.glsl"), 1)
            geom.setShaderInput('distortion',0.51)
            geom.setShaderInput("fog",  Vec4(0.4, 0.4, 0.4, 0.002))
            geom.setShaderInput("color_gradient",  color_gradient)          
            geom.setShaderInput("size_gradient",  size_gradient)            
            geom.setShaderInput("shape_gradient",  shape_gradient)  
            geom.setShaderInput("blend_gradient", loader.loadTexture("blend.png", minfilter=Texture.FTNearest, magfilter=Texture.FTNearest))            
        self.p.start(parent=self.root, renderParent = render) 
       
    
    def loadValues(self, v=None):
        if v==None:
            v=self.values
        p0 = Particles.Particles('particles-1') #const.
        # Particles parameters
        p0.setFactory("PointParticleFactory") #const.
        p0.setRenderer("SpriteParticleRenderer")#const.
        p0.setEmitter(v["emiter"])
        p0.setPoolSize(v["pool"])
        p0.setBirthRate(v["birthRate"])
        p0.setLitterSize(v["litter"])
        p0.setLitterSpread(v["litterSpread"])        
        p0.setLocalVelocityFlag(1)#const.
        p0.setSystemGrowsOlderFlag(0)#const.
        # Factory parameters
        p0.factory.setLifespanBase(v["life"])
        p0.factory.setLifespanSpread(v["lifeSpread"])
        p0.factory.setMassBase(v["mass"])
        p0.factory.setMassSpread(v["massSpread"])
        p0.factory.setTerminalVelocityBase(100.0000) #has no effect?
        p0.factory.setTerminalVelocitySpread(0.0000) #has no effect?           
        # Renderer parameters
        #p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAIN)
        #p0.renderer.setUserAlpha(1.00)
        # Sprite parameters
        p0.renderer.addTextureFromFile('../particle/smoke1.png') #some default must be added or it bugs out
        p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
        p0.renderer.setXScaleFlag(0)
        p0.renderer.setYScaleFlag(0)
        p0.renderer.setAnimAngleFlag(0)
        p0.renderer.setNonanimatedTheta(180.0000) #?
        p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PRALPHANONE)
        p0.renderer.setAlphaDisable(0)
        p0.renderer.setColorBlendMode(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOneMinusIncomingAlpha)#TODO!
        p0.renderer.getColorInterpolationManager().addLinear(0.0,1.0,Vec4(0.0,0.0,0.0,1.0),Vec4(1.0,1.0,1.0,1.0),True)
        # Emitter parameters
        p0.emitter.setEmissionType(v["mode"])
        p0.emitter.setAmplitude(v["amplitude"])
        p0.emitter.setAmplitudeSpread(v["amplitudeSpread"])
        p0.emitter.setOffsetForce(Vec3(v["offsetForce"][0], v["offsetForce"][1], v["offsetForce"][2]))
        p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
        p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
        if v['emiter']=='BoxEmitter':
            p0.emitter.setMaxBound(Point3(v['max'][0],v['max'][1],v['max'][2])) 
            p0.emitter.setMinBound(Point3(v['min'][0],v['min'][1],v['min'][2])) 
        elif v['emiter']=='DiscEmitter':
            p0.emitter.setRadius(v["radius"])
            p0.emitter.setInnerAngle(v["innerAngle"])
            p0.emitter.setInnerMagnitude(v["innerMagnitude"])
            p0.emitter.setOuterAngle(v["outerAngle"])
            p0.emitter.setOuterMagnitude(v["outerMagnitude"]) 	
        elif v['emiter']=='LineEmitter':
            p0.emitter.setEndpoint1(Point3(v['max'][0],v['max'][1],v['max'][2])) 
            p0.emitter.setEndpoint2(Point3(v['min'][0],v['min'][1],v['min'][2]))         	
        elif v['emiter']=='PointEmitter':
            pass #no options here
        elif v['emiter']=='RectangleEmitter':
            p0.emitter.setMaxBound(Point3(v['max'][0],v['max'][1],v['max'][2])) 
            p0.emitter.setMinBound(Point3(v['min'][0],v['min'][1],v['min'][2])) 
        elif v['emiter']=='RingEmitter':  
            p0.emitter.setAngle(v["angle"])
            p0.emitter.setRadius(v["radius"])
            p0.emitter.setRadiusSpread(v["radiusSpread"])
        elif v['emiter']=='SphereSurfaceEmitter':            
            p0.emitter.setRadius(v["radius"])
        elif v['emiter']=='SphereVolumeEmitter':            
            p0.emitter.setRadius(v["radius"])
        elif v['emiter']=='TangentRingEmitter':         
            p0.emitter.setRadius(v["radius"])
            p0.emitter.setRadiusSpread(v["radiusSpread"])
        self.p.addParticles(p0)
        f0 = ForceGroup.ForceGroup('default')
        # Force parameters
        if v["forceVector"][3]>0.0:
            force0 = LinearVectorForce(Vec3(v["forceVector"][0],v["forceVector"][1],v["forceVector"][2]), v["forceVector"][3], v["forceVector"][4])
            force0.setVectorMasks(1, 1, 1)
            force0.setActive(1)
            f0.addForce(force0)
        if v["forceJitter"][1]>0:    
            force1 = LinearJitterForce(v["forceJitter"][0], v["forceJitter"][1])
            force1.setVectorMasks(1, 1, 1)
            force1.setActive(1)
            f0.addForce(force1)
        if v["forceSink"][5]>0:        
            force2 = LinearSinkForce(Point3(v["forceSink"][0], v["forceSink"][1], v["forceSink"][2]), v["forceSink"][3], v["forceSink"][4], v["forceSink"][5], v["forceSink"][6])
            force2.setVectorMasks(1, 1, 1)
            force2.setActive(1)
            f0.addForce(force2)
        if v["forceSource"][5]>0:    
            force3 = LinearSourceForce(Point3(v["forceSource"][0], v["forceSource"][1], v["forceSource"][2]), v["forceSource"][3], v["forceSource"][4], v["forceSource"][5], v["forceSource"][6])
            force3.setVectorMasks(1, 1, 1)
            force3.setActive(1)
            f0.addForce(force3)
        if v["forceVertex"][3]>0:    
            force4 = LinearCylinderVortexForce(v["forceSource"][0], v["forceSource"][1], v["forceSource"][2], v["forceSource"][3], v["forceSource"][4])
            force4.setVectorMasks(1, 1, 1)
            force4.setActive(1)
            f0.addForce(force4)    
        self.p.addForceGroup(f0)
app=Editor()
base.run()        
        
