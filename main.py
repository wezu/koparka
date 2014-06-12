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
wp.setTitle("Koparka - Panda3D Level Editor")  
WindowProperties.setDefault(wp)

from panda3d.core import *
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from camcon import CameraControler
from buffpaint import BufferPainter
from guihelper import GuiHelper
from fxaa import makeFXAA
import os, sys
from random import uniform 

BUFFER_HEIGHT=0
BUFFER_ATR=1
BUFFER_COLOR=2
BUFFER_EXTRA=3 #used for grass (red)... maybe something extra in the future?

MODE_HEIGHT=0
MODE_TEXTURE=1
MODE_EXTRA=2
MODE_OBJECT=3

class Editor (DirectObject):
    def __init__(self):
    
        #fxaa, just the manager, the effect is created when the window is opened/resized
        self.fxaaManager=FilterManager(base.win, base.cam)
        
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
        #axis to help orient the scene
        self.axis=loader.loadModel('data/axis.egg')
        self.axis.reparentTo(render)
        self.axis.setLightOff()
        
        #store variables needed for diferent classes 
        self.mode=MODE_HEIGHT
        self.tempColor=1
        self.ignoreHover=False
        
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
        self.painter=BufferPainter(self.brushList, showBuff=False)
        #2 buffers should do, but painting in an alpha channel is strange, so I use 3 (+1 for grass)
        #BUFFER_HEIGHT
        self.painter.addCanvas() 
        #BUFFER_ATR
        self.painter.addCanvas() 
        #BUFFER_COLOR                              
        self.painter.addCanvas(size=2048,
                                default_tex='data/gray.png',
                                brush_shader=loader.loadShader('shaders/brush.cg'),
                                shader_inputs={'brushTex':loader.loadTexture(self.textureList[18]), 'brushSize':1.0})
        #BUFFER_EXTRA (grass for now)
        self.painter.addCanvas() 
        
        #GUI
        self.gui=GuiHelper(path)
        #tooltip bar
        self.tooltip=self.gui.addTooltip(self.gui.BottomLeft, (564, 32),y_offset=-96)
        self.tooltip.hide()
        #the toolbar_id here is just an int, not a 'toolbar object'!
        self.toolbar_id=self.gui.addToolbar(self.gui.TopLeft, (512, 32),hover_command=self.onToolbarHover)        
        id=0
        for brush in self.brushList:            
            self.gui.addButton(self.toolbar_id,brush, self.setBrush, [id],tooltip=self.tooltip, tooltip_text='Set Brush Shape')
            id+=1
        #texture palette    
        self.palette_id=self.gui.addToolbar(self.gui.TopRight, (160, 512), x_offset=-160, y_offset=22, hover_command=self.onToolbarHover)
        id=0
        for tex in self.textureList:            
            self.gui.addButton(self.palette_id, tex, self.setColorTexture, [id],tooltip=self.tooltip, tooltip_text='Set Brush Texture')
            id+=1
        #detail composer preview    
        self.composer_id=self.gui.addComposer(self.gui.BottomRight, self.updateComposer, hover_command=self.onToolbarHover, tooltip=self.tooltip)
        #save/load
        self.gui.addSaveLoadDialog(self.save, self.load, self.hideSaveMenu)
        
        #extra tools and info at the bottom
        self.statusbar=self.gui.addToolbar(self.gui.BottomLeft, (1024, 128), icon_size=64, y_offset=-64, hover_command=self.onToolbarHover)
        self.size_info=self.gui.addInfoIcon(self.statusbar, 'icon/resize.png', '1.0', tooltip=self.tooltip, tooltip_text='Brush Size:   [A]-Decrease    [D]-Increase')
        self.color_info=self.gui.addInfoIcon(self.statusbar, 'icon/color.png', '0.05',tooltip=self.tooltip, tooltip_text='Brush Strength:   [W]-Increase   [S]-Decrease')
        self.heading_info=self.gui.addInfoIcon(self.statusbar, 'icon/rotate.png', '0',tooltip=self.tooltip, tooltip_text='Brush Rotation:   [Q]-Left   [E]-Right')
        self.gui.addInfoIcon(self.statusbar, 'icon/blank.png', '')#empty space
        self.gui.addButton(self.statusbar, 'icon/hm_icon.png', self.setMode, [MODE_HEIGHT], self.tooltip, 'Paint Heightmap Mode [F1]')
        self.gui.addButton(self.statusbar, 'icon/tex_icon.png', self.setMode, [MODE_TEXTURE], self.tooltip, 'Paint Texture Mode [F2]')
        self.gui.addButton(self.statusbar, 'icon/grass.png', self.setMode, [MODE_EXTRA], self.tooltip, 'Paint Grass Mode [F3]')
        self.gui.addButton(self.statusbar, 'icon/place_icon.png', self.setMode, [MODE_OBJECT], self.tooltip, 'Paint Objects Mode [F4]')
        self.gui.addButton(self.statusbar, 'icon/save.png', self.showSaveMenu, tooltip=self.tooltip, tooltip_text='Save/Load [F5]')
        #gray out buttons
        self.gui.grayOutButtons(self.statusbar, (4,8), None)
        
        
        #terrain mesh
        self.mesh=loader.loadModel('data/mesh10k.egg')
        self.mesh.setTexture(self.painter.textures[BUFFER_COLOR], 1)
        gradient=loader.loadTexture('data/gradient.png')
        gradient.setWrapU(Texture.WMClamp)
        gradient.setWrapV(Texture.WMClamp  )
        self.mesh.reparentTo(render)
        self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f.glsl"))
        self.mesh.setShaderInput("height", self.painter.textures[BUFFER_HEIGHT]) 
        self.mesh.setShaderInput("atr", self.painter.textures[BUFFER_ATR]) 
        self.mesh.setShaderInput("gradient", gradient)
        #grass
        self.grass=render.attachNewNode('grass')
        self.CreateGrassTile(uv_offset=Vec2(0,0), pos=(0,0,0), parent=self.grass)
        self.CreateGrassTile(uv_offset=Vec2(0,0.5), pos=(0, 256, 0), parent=self.grass)
        self.CreateGrassTile(uv_offset=Vec2(0.5,0), pos=(256, 0, 0), parent=self.grass)
        self.CreateGrassTile(uv_offset=Vec2(0.5,0.5), pos=(256, 256, 0), parent=self.grass)  
               
        #light
        self.dlight = DirectionalLight('dlight') 
        self.dlight.setColor(VBase4(0.7, 0.7, 0.5, 1))     
        self.mainLight = render.attachNewNode(self.dlight)
        self.mainLight.setP(-60)       
        self.mainLight.setH(90)
        render.setLight(self.mainLight)
        
        self.dlight2 = DirectionalLight('dlight2') 
        self.dlight2.setColor(VBase4(0.6, 0.6, 0.8, 1))  
        self.Ambient = render.attachNewNode( self.dlight2)        
        self.Ambient.setPos(base.camera.getPos(render))
        self.Ambient.setP(-45)
        self.Ambient.wrtReparentTo(base.camera)
        render.setLight(self.Ambient)
        
        
        
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
        self.accept('f3', self.setMode,[MODE_EXTRA])        
        self.accept('f4', self.setMode,[MODE_OBJECT])        
        self.accept('f5',self.showSaveMenu)
        self.accept( 'window-event', self.windowEventHandler) 
        
        #make sure things have some/any starting value
        self.setMode(MODE_HEIGHT)
        self.setBrush(0)
        
        #tasks
        taskMgr.doMethodLater(0.1, self.update,'update_task')
        taskMgr.add(self.perFrameUpdate, 'perFrameUpdate_task')

   
    def onToolbarHover(self, hoverIn, guiEvent=None):        
        if self.ignoreHover:
            return
        if hoverIn:
            self.painter.hideBrushes()
        else:
            self.setMode(self.mode)
    
    def showSaveMenu(self, guiEvent=None):
        self.ignoreHover=True
        self.painter.hideBrushes()
        self.gui.SaveLoadFrame.show()
        self.ignore('mouse1-up')
        self.ignore('mouse1')
        
    def hideSaveMenu(self, guiEvent=None):
        self.ignoreHover=False
        self.gui.SaveLoadFrame.hide()
        self.setMode(self.mode)
        
    def CreateGrassTile(self, uv_offset, pos, parent, count=256):
        grass=loader.loadModel("data/grass_model")
        grass.reparentTo(parent)
        grass.setInstanceCount(count) 
        grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
        grass.node().setFinal(1)
        grass.setShader(Shader.load(Shader.SLGLSL, "shaders/grass_v.glsl", "shaders/grass_f.glsl"))
        grass.setShaderInput('height', self.painter.textures[BUFFER_HEIGHT]) 
        grass.setShaderInput('grass', self.painter.textures[BUFFER_EXTRA])
        grass.setShaderInput('uv_offset', uv_offset)   
        grass.setPos(pos)
        return grass
        
    def load(self, guiEvent=None):
        save_dir=path+self.gui.entry1.get()
        if self.gui.flags[0]:
            print "loading height map...",
            file=path+save_dir+"/"+self.gui.entry2.get()
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_HEIGHT].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"
        if self.gui.flags[1]:
            print "loading detail map...",
            file=path+save_dir+"/"+self.gui.entry3.get()
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_ATR].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"            
        if self.gui.flags[2]:
            print "loading color map...",
            file=path+save_dir+"/"+self.gui.entry4.get()
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_COLOR].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"            
            
        if self.gui.flags[3]:
            print "loading grass map...",
            file=path+save_dir+"/"+self.gui.entry5.get()
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_EXTRA].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"                       
        if self.gui.flags[4]:
            print "Object loading not implemented!"        
        print "Loading DONE!"        
        self.hideSaveMenu()
        
        
    def save(self, guiEvent=None):  
        save_dir=path+self.gui.entry1.get()        
        if os.path.exists(path+save_dir):
            print "ERROR:", save_dir, "already exists!"
            print "No files saved!"
            return    
        else:
            os.makedirs(Filename(path+save_dir).toOsSpecific())            
        if self.gui.flags[0]:
            print "saving height map...",
            self.painter.write(BUFFER_HEIGHT, path+save_dir+"/"+self.gui.entry2.get())
            print "done"
        if self.gui.flags[1]:
            print "saving detail map...",
            self.painter.write(BUFFER_ATR, path+save_dir+"/"+self.gui.entry3.get())  
            print "done"
        if self.gui.flags[2]:
            print "saving color map...",
            self.painter.write(BUFFER_COLOR, path+save_dir+"/"+self.gui.entry4.get())
            print "done"
        if self.gui.flags[3]:
            print "saving grass map...",
            self.painter.write(BUFFER_EXTRA, path+save_dir+"/"+self.gui.entry5.get())          
            print "done"
        if self.gui.flags[4]:
            print "Object saving not implemented!"        
        print "SAVING DONE!"       
        self.hideSaveMenu()
        
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
            self.gui.grayOutButtons(self.statusbar, (4,8), 4)
            #self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f1.glsl"))
            self.painter.brushes[BUFFER_HEIGHT].show()
            self.painter.brushes[BUFFER_HEIGHT].setColor(1, 1, 1, 0.05)
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_COLOR].hide()
            self.painter.brushes[BUFFER_EXTRA].hide()
            self.painter.brushAlpha=0.05
            self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.hideElement(self.composer_id)
            self.gui.hideElement(self.palette_id)
            #self.grass.hide()
        elif mode==MODE_TEXTURE:
            self.gui.grayOutButtons(self.statusbar, (4,8), 5)
            #self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f.glsl")) 
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].show()
            self.painter.brushes[BUFFER_EXTRA].hide()
            #self.painter.brushes[BUFFER_ATR].setColor(1,0,0,1.0)
            self.painter.brushes[BUFFER_COLOR].show()
            self.painter.brushes[BUFFER_COLOR].setColor(1, 1, 1, 1)
            self.painter.brushAlpha=1.0
            self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.accept('mouse1', self.paint)                
            self.ignore('mouse1-up')
            self.gui.showElement(self.composer_id)
            self.gui.showElement(self.palette_id)
            #self.grass.show()
        elif mode==MODE_EXTRA:
            self.gui.grayOutButtons(self.statusbar, (4,8), 6)
            #self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/ter_v.glsl", "shaders/ter_f.glsl")) 
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_COLOR].hide()
            self.painter.brushes[BUFFER_EXTRA].show()
            self.painter.brushes[BUFFER_EXTRA].setColor(1,0,0, 1)
            self.painter.brushAlpha=1.0
            self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.hideElement(self.composer_id)
            self.gui.hideElement(self.palette_id)
            #self.grass.show()
        elif mode==MODE_OBJECT:
            print "Not implemented!"
            return
        self.mode=mode
        
    def flipBrushColor(self):        
        if self.mode in (MODE_HEIGHT, MODE_EXTRA):
            print "TAB!"
            if self.tempColor==1:
                self.tempColor=0
            else:    
                self.tempColor=1
            c=self.tempColor
            #a=self.painter.brushes[BUFFER_HEIGHT].getColor()[3]
            self.painter.brushes[BUFFER_HEIGHT].setColor(c,c,c,self.painter.brushAlpha) 
            if self.mode==MODE_EXTRA:
                self.painter.brushes[BUFFER_EXTRA].setColor(c,0,0,self.painter.brushAlpha)
             
    def update(self, task):
        if self.mode==MODE_HEIGHT:
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_HEIGHT)
        elif self.mode==MODE_EXTRA:
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_EXTRA) 
                
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
        
    def perFrameUpdate(self, task): 
        time=globalClock.getFrameTime()    
        self.grass.setShaderInput('time', time)    
        return task.cont    
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            self.gui.updateBaseNodes()   
            #resizing the window breaks the filter manager, so I just make a new one
            self.fxaaManager.cleanup()
            self.fxaaManager=makeFXAA(self.fxaaManager)
app=Editor()
run()    
