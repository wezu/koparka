from panda3d.core import loadPrcFileData
loadPrcFileData('','textures-power-2 None')#needed for fxaa
loadPrcFileData('','win-size 1024 768')

from direct.showbase.AppRunnerGlobal import appRunner
from panda3d.core import Filename
if appRunner: 
    path=appRunner.p3dFilename.getDirname()+'/'
else: 
    path=""

from panda3d.core import WindowProperties
wp = WindowProperties.getDefault() 
#wp.setFixedSize(True)  #needed for fxaa
wp.setOrigin(-2,-2)  
wp.setTitle("Simple Level Editor for Panda3D")  
WindowProperties.setDefault(wp)

from panda3d.core import *
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from camcon import CameraControler
from buffpaint import BufferPainter
from guihelper import GuiHelper
import os, sys

BUFFER_HEIGHT=0
BUFFER_ATR=1
BUFFER_COLOR=2

MODE_HEIGHT=0
MODE_TEXTURE=1
MODE_OBJECT=2

class Editor (DirectObject):
    def __init__(self):
    
        #make a grid
        cm = CardMaker("plane")
        cm.setFrame(0, 512, 0, 512)        
        self.grid=render.attachNewNode(cm.generate())
        self.grid.lookAt(0, 0, -1)
        self.grid.setTexture(loader.loadTexture('data/grid.png'))
        self.grid.setTransparency(TransparencyAttrib.MAlpha)
        self.grid.setTexScale(TextureStage.getDefault(), 16, 16, 1)
        self.grid.setZ(1)
        self.grid.setLightOff()
        self.grid.setColor(0,0,0,0.5)        
        self.axis=loader.loadModel('data/axis.egg')
        self.axis.reparentTo(render)
        self.axis.setLightOff()
        
        #store variables needed for diferent classes 
        self.mode=MODE_HEIGHT
        self.tempColor=1
        
        #camera control
        base.disableMouse()  
        controler=CameraControler()
        
        #painter        
        self.brushList=[]
        dirList=os.listdir(Filename(path+"brush/").toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('png', 'tga', 'dds'):
                self.brushList.append("brush/"+fname)
        self.textureList=[]
        dirList=os.listdir(Filename(path+"textures/").toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('png', 'tga', 'dds'):
                self.textureList.append("textures/"+fname)
        self.painter=BufferPainter(self.brushList)
        #2 buffers should do, but painting in an alpha channel is strange, so I use 3
        #BUFFER_HEIGHT
        self.painter.addCanvas() 
        #BUFFER_ATR
        self.painter.addCanvas() 
        #BUFFER_COLOR                              
        self.painter.addCanvas(size=2048,
                                default_tex='data/gray.png',
                                brush_shader=loader.loadShader('shaders/brush.cg'),
                                shader_inputs={'brushTex':loader.loadTexture(self.textureList[18])})
        
        
        #GUI
        self.gui=GuiHelper()
        #the toolbar_id here is just an int, not a 'toolbar object'!
        self.toolbar_id=self.gui.addToolbar(self.gui.TopLeft, 512)        
        id=0
        for brush in self.brushList:            
            self.gui.addButton(self.toolbar_id,brush, self.setBrush, [id])
            id+=1
        #texture palette    
        self.palette_id=self.gui.addToolbar(self.gui.TopRight, 160, x_offset=-160, y_offset=22)
        id=0
        for tex in self.textureList:            
            self.gui.addButton(self.palette_id, tex, self.setColorTexture, [id])
            id+=1
        #detail composer preview    
        self.composer_id=self.gui.addComposer(self.gui.BottomRight, self.updateComposer)
        
        #extra tools and info at the bottom
        self.statusbar=self.gui.addToolbar(self.gui.BottomLeft, 1024, icon_size=64, y_offset=-64)           
        self.size_info=self.gui.addInfoIcon(self.statusbar, 'icon/resize.png', '1.0')
        self.color_info=self.gui.addInfoIcon(self.statusbar, 'icon/color.png', '0.05')
        self.heading_info=self.gui.addInfoIcon(self.statusbar, 'icon/rotate.png', '0')
        self.gui.addInfoIcon(self.statusbar, 'icon/blank.png', '')#empty space
        self.gui.addButton(self.statusbar, 'icon/hm_icon.png', self.setMode, [MODE_HEIGHT])
        self.gui.addButton(self.statusbar, 'icon/tex_icon.png', self.setMode, [MODE_TEXTURE])
        self.gui.addButton(self.statusbar, 'icon/place_icon.png', self.setMode, [MODE_OBJECT])
        self.gui.addButton(self.statusbar, 'icon/save.png', self.save)
        
        #terrain mesh
        self.mesh=loader.loadModel('data/mesh10k.egg')
        self.mesh.setTexture(self.painter.textures[BUFFER_COLOR], 1)
        gradient=loader.loadTexture('data/gradient.png')
        gradient.setWrapU(Texture.WMClamp)
        gradient.setWrapV(Texture.WMClamp  )
        self.mesh.reparentTo(render)
        #shader
        self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f1.glsl"))
        self.mesh.setShaderInput("height", self.painter.textures[BUFFER_HEIGHT]) 
        self.mesh.setShaderInput("atr", self.painter.textures[BUFFER_ATR]) 
        self.mesh.setShaderInput("gradient", gradient)
        #light
        self.dlight = DirectionalLight('dlight') 
        self.dlight.setColor(VBase4(0.8, 0.8, 0.7, 1))     
        self.mainLight = render.attachNewNode(self.dlight)
        self.mainLight.setP(-45)       
        self.mainLight.setH(90)
        render.setLight(self.mainLight)   
        
        self.keyMap = {'paint': False,
                       'rotate_l':False, 
                       'rotate_r':False, 
                       'alpha_up':False,
                       'alpha_down':False,
                       'scale_up':False,
                       'scale_down':False}                       
        
        self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
        self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])        
        self.accept('e', self.keyMap.__setitem__, ['rotate_r', True])                
        self.accept('e-up', self.keyMap.__setitem__, ['rotate_r', False])
        self.accept('q', self.keyMap.__setitem__, ['rotate_l', True])                
        self.accept('q-up', self.keyMap.__setitem__, ['rotate_l', False])
        self.accept('d', self.keyMap.__setitem__, ['scale_up', True])                
        self.accept('d-up', self.keyMap.__setitem__, ['scale_up', False])
        self.accept('a', self.keyMap.__setitem__, ['scale_down', True])                
        self.accept('a-up', self.keyMap.__setitem__, ['scale_down', False])
        self.accept('w', self.keyMap.__setitem__, ['alpha_up', True])                
        self.accept('w-up', self.keyMap.__setitem__, ['alpha_up', False])
        self.accept('s', self.keyMap.__setitem__, ['alpha_down', True])                
        self.accept('s-up', self.keyMap.__setitem__, ['alpha_down', False])
        self.accept('tab', self.flipBrushColor)
        self.accept('f1', self.setMode,[MODE_HEIGHT])
        self.accept('f2', self.setMode,[MODE_TEXTURE])
        self.accept('f3', self.setMode,[MODE_OBJECT])        
        self.accept( 'window-event', self.windowEventHandler) 
        
        #make sure things have some/any starting value
        self.setMode(MODE_HEIGHT)
        self.setBrush(0)
        
        #tasks
        taskMgr.doMethodLater(0.1, self.update,'update_task')
    
    def save(self, guiEvent=None):
        self.painter.write(BUFFER_HEIGHT, "save/heightmap.png")
        self.painter.write(BUFFER_ATR, "save/atrmap.png")
        self.painter.write(BUFFER_COLOR, "save/colormap.png")
    
    def updateComposer(self):
        id =self.composer_id
        preview_geom=self.gui.elements[id]['geom']
        r_slider=self.gui.elements[id]['r_slider']
        g_slider=self.gui.elements[id]['g_slider']
        b_slider=self.gui.elements[id]['b_slider']
        color=Vec4(r_slider['value'],g_slider['value'],b_slider['value'],1.0 )
        preview_geom.setShaderInput('mix', color)
        self.painter.brushes[BUFFER_ATR].setColor(color)
    
    def setColorTexture(self, id, guiEvent=None):
        self.painter.brushes[BUFFER_COLOR].setShaderInput('brushTex', loader.loadTexture(self.textureList[id]))
    
    def setBrush(self, id, guiEvent=None):
        self.painter.setBrushTex(id)
        for button in self.gui.elements[0]['buttons']:
            button.setColor(0,0,0, 1)
        self.gui.elements[0]['buttons'][id].setColor(1,1,1, 1)
     
    def paint(self):
        self.painter.paint(BUFFER_ATR)
        self.painter.paint(BUFFER_COLOR)
        
    def setMode(self, mode, guiEvent=None):
        if mode==MODE_HEIGHT:
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f1.glsl"))
            self.painter.brushes[BUFFER_HEIGHT].show()
            self.painter.brushes[BUFFER_HEIGHT].setColor(1, 1, 1, 0.05)
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_COLOR].hide()
            self.painter.brushAlpha=0.05
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.hideElement(self.composer_id)
            self.gui.hideElement(self.palette_id)
        elif mode==MODE_TEXTURE:
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f.glsl")) 
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].show()
            self.painter.brushes[BUFFER_ATR].setColor(1,0,0,1.0)
            self.painter.brushes[BUFFER_COLOR].show()
            self.painter.brushes[BUFFER_COLOR].setColor(1, 1, 1, 1)
            self.painter.brushAlpha=1.0
            self.accept('mouse1', self.paint)                
            self.ignore('mouse1-up')
            self.gui.showElement(self.composer_id)
            self.gui.showElement(self.palette_id)
        elif mode==MODE_OBJECT:
            print "Not implemented!"
            return
        self.mode=mode
        
    def flipBrushColor(self):        
        if self.mode==MODE_HEIGHT:
            if self.tempColor==1:
                self.tempColor=0
            else:    
                self.tempColor=1
            c=self.tempColor
            a=self.painter.brushes[BUFFER_HEIGHT].getColor()[3]
            self.painter.brushes[BUFFER_HEIGHT].setColor(c,c,c,a)            
        
    def update(self, task):
        if self.mode==MODE_HEIGHT:            
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_HEIGHT)#, grayscale=True)            
        if self.keyMap['rotate_l']:
            self.painter.adjustBrushHeading(5)
            self.heading_info['text']='%.0f'%self.painter.brushes[0].getH()
        if self.keyMap['rotate_r']:
            self.painter.adjustBrushHeading(-5)    
            self.heading_info['text']='%.0f'%self.painter.brushes[0].getH()
        if self.keyMap['scale_up']:
            self.painter.adjustBrushSize(0.01)
            self.size_info['text']='%.2f'%self.painter.brushSize
        if self.keyMap['scale_down']:
            self.painter.adjustBrushSize(-0.01) 
            self.size_info['text']='%.2f'%self.painter.brushSize
        if self.keyMap['alpha_up']:
            self.painter.adjustBrushAlpha(0.01)  
            self.color_info['text']='%.2f'%self.painter.brushAlpha    
        if self.keyMap['alpha_down']:
            self.painter.adjustBrushAlpha(-0.01) 
            self.color_info['text']='%.2f'%self.painter.brushAlpha 
        return task.again 
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            self.gui.updateBaseNodes()   
            
app=Editor()
run()    
