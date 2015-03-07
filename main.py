from panda3d.core import loadPrcFileData
loadPrcFileData('','textures-power-2 None')#needed for fxaa
loadPrcFileData('','win-size 1024 768')
loadPrcFileData('','show-frame-rate-meter  1')
loadPrcFileData('','sync-video 0')
loadPrcFileData('','framebuffer-srgb true')
loadPrcFileData('','default-texture-color-space sRGB')
#loadPrcFileData('','gl-check-errors #t')
#loadPrcFileData('','show-buffers 1')
#loadPrcFileData('','undecorated 1')
#loadPrcFileData('','win-size 854 480')
#loadPrcFileData("", "dump-generated-shaders 1")
from direct.showbase.AppRunnerGlobal import appRunner
from panda3d.core import Filename
if appRunner: 
    path=appRunner.p3dFilename.getDirname()+'/'
else: 
    path=""

from panda3d.core import WindowProperties
wp = WindowProperties.getDefault() 
wp.setOrigin(-2,-2)  
#wp.setUndecorated(True) 
wp.setTitle("Koparka - Panda3D Level Editor")  
WindowProperties.setDefault(wp)

from panda3d.core import *
#import direct.directbase.DirectStart
from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from camcon import CameraControler
from buffpaint import BufferPainter
from guihelper import GuiHelper
#from fxaa import makeFXAA moved into code
from collisiongen import GenerateCollisionEgg
from navmeshgen import GenerateNavmeshCSV
from objectpainter import ObjectPainter
from jsonloader import SaveScene, LoadScene
import os, sys
import random
import re
 
#helper function
def sort_nicely( l ):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )
    
BUFFER_HEIGHT=0
BUFFER_ATR=1
BUFFER_GRASS=2 
BUFFER_WALK=3 
BUFFER_ATR2=4

MODE_HEIGHT=0
MODE_TEXTURE=1
MODE_GRASS=2
MODE_OBJECT=3
MODE_WALK=4

OBJECT_MODE_ONE=0
OBJECT_MODE_MULTI=1
OBJECT_MODE_WALL=2
OBJECT_MODE_SELECT=3
OBJECT_MODE_ACTOR=4
OBJECT_MODE_COLLISION=5
OBJECT_MODE_PICKUP=6

HEIGHT_MODE_UP=0
HEIGHT_MODE_DOWN=1
HEIGHT_MODE_LEVEL=2

WALK_MODE_NOWALK=0
WALK_MODE_WALK=1

GRASS_MODE_PAINT=1
GRASS_MODE_REMOVE=0

MASK_WATER=BitMask32.bit(1)
MASK_SHADOW=BitMask32.bit(2)

class Editor (DirectObject):
    def __init__(self):
        #init ShowBase
        base = ShowBase.ShowBase()
        
        #manager for post process filters (fxaa, soft shadows, dof)
        manager=FilterManager(base.win, base.cam)        
       
        self.filters=self.setupFilters(manager)
        
        #make a grid
        cm = CardMaker("plane")
        cm.setFrame(0, 512, 0, 512)        
        self.grid=render.attachNewNode(cm.generate())
        self.grid.lookAt(0, 0, -1)
        self.grid.setTexture(loader.loadTexture('data/grid.png'))
        self.grid.setTransparency(TransparencyAttrib.MDual)
        self.grid.setTexScale(TextureStage.getDefault(), 16, 16, 1)
        self.grid.setZ(25.5)        
        self.grid.setLightOff()
        self.grid.setColor(0,0,0,0.5) 
        self.grid_z=25.5
        self.grid_scale=16
        self.grid.hide(MASK_WATER)
        self.grid.hide(MASK_SHADOW)
        #self.grid.hide()
        #axis to help orient the scene
        self.axis=loader.loadModel('data/axis.egg')
        self.axis.reparentTo(render)
        self.axis.setLightOff()
        self.axis.hide(MASK_WATER)
        self.axis.hide(MASK_SHADOW)
        
        #store variables needed for diferent classes 
        self.mode=MODE_HEIGHT
        self.height_mode=HEIGHT_MODE_UP
        self.tempColor=1
        self.tempAlpha=0.05
        self.ignoreHover=False
        self.collision_mesh=None
        self.winsize=[0,0]
        self.object_mode=OBJECT_MODE_ONE
        self.hpr_axis='H: '
        self.last_model_path=''
        self.lastUpdateTime=0.0
        self.curent_textures=[0,1,2,3,4,5]
        self.textures_diffuse=[]
        self.textures_normal=[]
       
        #camera control
        base.disableMouse()  
        self.controler=CameraControler()
        self.controler.cameraNode.setZ(25.5)
        render.setShaderInput('camera', base.cam)
        #emptyPlane = render.attachNewNode(PlaneNode("emptyPlane", Plane(Vec3(0, 0, 1), Point3(0, 0, -100))))
        #basecamtmpNP = NodePath("basecamtmpNP")
        #render.setClipPlane(emptyPlane)
        #basecamtmpNP.setAttrib(ColorScaleAttrib.make(Vec4(1.0, 0.0, 0.0, 1.0)))
        #base.cam.node().setInitialState(basecamtmpNP.getState())
        
        
        #painter        
        self.brushList=[]
        dirList=os.listdir(Filename(path+"brush/").toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('png', 'tga', 'dds'):
                self.brushList.append("brush/"+fname)
        self.painter=BufferPainter(self.brushList, showBuff=False)
        #2 buffers should do, but painting in an alpha channel is strange, so I use 3 (+1 for grass)
        #BUFFER_HEIGHT
        self.painter.addCanvas(default_tex='data/def_height.png') 
        #BUFFER_ATR
        self.painter.addCanvas(default_tex='data/atr_def.png')
        #BUFFER_GRASS
        self.painter.addCanvas(brush_shader=loader.loadShader('shaders/brush_a_to_g.cg')) 
        #BUFFER_WALK =3
        self.painter.addCanvas(size=128,  brush_shader=loader.loadShader('shaders/brush3.cg'))   
        #BUFFER_ATR2=4
        self.painter.addCanvas()
        
        #GUI
        self.gui=GuiHelper(path)
        #tooltip bar
        self.tooltip=self.gui.addTooltip(self.gui.BottomLeft, (564, 32),y_offset=-96)
        self.tooltip.hide()
        #the toolbar_id here is just an int, not a 'toolbar object'!
        self.toolbar_id=self.gui.addToolbar(self.gui.TopLeft, (864, 32),hover_command=self.onToolbarHover, color=(1,1,1, 0.8))        
        id=0
        for brush in self.brushList:            
            self.gui.addButton(self.toolbar_id,brush, self.setBrush, [id],tooltip=self.tooltip, tooltip_text='Set Brush Shape')
            id+=1
        #texture palette    
        self.palette_id=self.gui.addToolbar(self.gui.TopRight, (80, 512),icon_size=80, x_offset=-80, y_offset=0, hover_command=self.onToolbarHover)
        dirList=os.listdir(Filename(path+"tex/diffuse").toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('dds'):
                self.textures_diffuse.append(fname)
                self.textures_normal.append(fname)   
        #sort them, we want 0,1,2,3,4,5 as default textures        
        sort_nicely(self.textures_diffuse)        
        sort_nicely(self.textures_normal)
        for tex in self.textures_diffuse:
            id=self.textures_diffuse.index(tex)
            self.textures_diffuse[id]="tex/diffuse/"+tex
        for tex in self.textures_normal:
            id=self.textures_normal.index(tex)
            self.textures_normal[id]="tex/normal/"+tex              
        
        self.gui.addButton(self.palette_id, self.textures_diffuse[0], self.setAtrMapColor, [(1.0, 0.0, 0.0, 1.0),(0.0, 0.0, 0.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        self.gui.addButton(self.palette_id, self.textures_diffuse[1], self.setAtrMapColor, [(0.0, 1.0, 0.0, 1.0),(0.0, 0.0, 0.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        self.gui.addButton(self.palette_id, self.textures_diffuse[2], self.setAtrMapColor, [(0.0, 0.0, 1.0, 1.0),(0.0, 0.0, 0.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        self.gui.addButton(self.palette_id, self.textures_diffuse[3], self.setAtrMapColor, [(0.0, 0.0, 0.0, 1.0),(1.0, 0.0, 0.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        self.gui.addButton(self.palette_id, self.textures_diffuse[4], self.setAtrMapColor, [(0.0, 0.0, 0.0, 1.0),(0.0, 1.0, 0.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        self.gui.addButton(self.palette_id, self.textures_diffuse[5], self.setAtrMapColor, [(0.0, 0.0, 0.0, 1.0),(0.0, 0.0, 1.0, 1.0) ] ,tooltip=self.tooltip, tooltip_text='Set Brush Texture')
        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 48], self.changeTex,[0] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 128], self.changeTex,[1] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 208], self.changeTex,[2] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 288], self.changeTex,[3] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 368], self.changeTex,[4] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        self.gui.addFloatingButton(self.palette_id, [32,32], 'icon/change.png',[48, 448], self.changeTex,[5] ,tooltip=self.tooltip, tooltip_text='Change texture')        
        
        
        #save/load
        self.gui.addSaveLoadDialog(self.save, self.load, self.hideSaveMenu)
        #config
        self.gui.addConfigDialog(self.configBrush)
        #sky/sea dialog
        self.gui.addSkySeaDialog(self.configSkySea)
        
        #extra tools and info at the bottom
        self.statusbar=self.gui.addToolbar(self.gui.BottomLeft, (704, 128), icon_size=64, y_offset=-64, hover_command=self.onToolbarHover, color=(1,1,1, 0.0))
        self.size_info=self.gui.addInfoIcon(self.statusbar, 'icon/resize.png', '1.0', tooltip=self.tooltip, tooltip_text='Brush Size or Object Scale:   [A]-Decrease    [D]-Increase')
        self.color_info=self.gui.addInfoIcon(self.statusbar, 'icon/color.png', '0.05',tooltip=self.tooltip, tooltip_text='Brush Strength or Object Z offset:   [W]-Increase   [S]-Decrease')
        self.heading_info=self.gui.addInfoIcon(self.statusbar, 'icon/rotate.png', '0',tooltip=self.tooltip, tooltip_text='Brush Rotation ([1][2][3] to change axis in Object Mode):   [Q]-Left   [E]-Right')        
        self.gui.addButton(self.statusbar, 'icon/config.png', self.configBrush, [True], self.tooltip, 'Configure brush and grid (numeric values)')
        self.gui.addButton(self.statusbar, 'icon/hm_icon.png', self.setMode, [MODE_HEIGHT], self.tooltip, 'Paint Heightmap Mode [F1]')
        self.gui.addButton(self.statusbar, 'icon/tex_icon.png', self.setMode, [MODE_TEXTURE], self.tooltip, 'Paint Texture Mode [F2]')
        self.gui.addButton(self.statusbar, 'icon/grass.png', self.setMode, [MODE_GRASS], self.tooltip, 'Paint Grass Mode [F3]')
        self.gui.addButton(self.statusbar, 'icon/place_icon.png', self.setMode, [MODE_OBJECT], self.tooltip, 'Paint Objects Mode [F4]')
        self.gui.addButton(self.statusbar, 'icon/walkmap_icon.png', self.setMode, [MODE_WALK], self.tooltip, 'Paint Walkmap Mode [F5]')
        self.gui.addButton(self.statusbar, 'icon/sky_sea_icon.png', self.configSkySea,[True], tooltip=self.tooltip, tooltip_text='Configure sky and sea (and all that they encompass) [F6]')
        self.gui.addButton(self.statusbar, 'icon/save.png', self.showSaveMenu, tooltip=self.tooltip, tooltip_text='Save/Load [F7]')
        #gray out buttons
        self.gui.grayOutButtons(self.statusbar, (4,10), None)
        
        #object toolbars (scrollable)
        #each object paint mode has its own
        self.object_toolbar_id=self.gui.addScrolledToolbar(self.gui.TopRight, 192,(192, 6000), x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5))
        self.multi_toolbar_id=self.gui.addScrolledToolbar(self.gui.TopRight, 192,(192, 6000), x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5))
        self.wall_toolbar_id=self.gui.addScrolledToolbar(self.gui.TopRight, 192,(192, 6000), x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5))
        self.actor_toolbar_id=self.gui.addScrolledToolbar(self.gui.TopRight, 192,(192, 6000), x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5))
        self.collision_toolbar_id=self.gui.addScrolledToolbar(self.gui.TopRight, 192,(192, 6000), x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5))
        
        #get models
        dirList=os.listdir(Filename(path+"models/").toOsSpecific())
        for fname in dirList:            
            if  Filename(fname).getExtension() in ('egg', 'bam'):
                self.gui.addListButton(self.object_toolbar_id, fname[:-4], command=self.setObject, arg=["models/"+fname])
            elif os.path.isdir(path+"models/"+fname):                
                self.gui.addListButton(self.multi_toolbar_id, fname, command=self.setRandomObject, arg=["models/"+fname+"/"])
        #get walls
        dirList=os.listdir(Filename(path+"models_walls/").toOsSpecific())
        for fname in dirList:                        
            if os.path.isdir(path+"models_walls/"+fname):                
                self.gui.addListButton(self.wall_toolbar_id, fname, command=self.setRandomObject, arg=["models_walls/"+fname+"/"])        
        #get actors
        dirList=os.listdir(Filename(path+"models_actor/").toOsSpecific())
        for fname in dirList:                        
            if Filename(fname).getExtension() in ('egg', 'bam') and fname.startswith('_m_'):                    
                self.gui.addListButton(self.actor_toolbar_id, fname[3:-4], command=self.setActor, arg=["models_actor/"+fname])        
        #get collision-models
        #these hava a part named 'editor', when loading these 'editor' parts should be hidden
        #appart from that collision-models are just like normal models
        dirList=os.listdir(Filename(path+"models_collision/").toOsSpecific())
        for fname in dirList:            
            if  Filename(fname).getExtension() in ('egg', 'bam'):
                self.gui.addListButton(self.collision_toolbar_id, fname[:-4], command=self.setObject, arg=["models_collision/"+fname])        
        #object-mode toolbar
        self.mode_toolbar_id=self.gui.addToolbar(self.gui.TopRight, (192, 64), icon_size=64, x_offset=-192, y_offset=0, hover_command=self.onToolbarHover)
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_object.png', self.setObjectMode,[OBJECT_MODE_ONE],tooltip=self.tooltip, tooltip_text='Place single objects')
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_multi.png', self.setObjectMode,[OBJECT_MODE_MULTI],tooltip=self.tooltip, tooltip_text='Place multiple, similar objects')
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_wall.png', self.setObjectMode,[OBJECT_MODE_WALL],tooltip=self.tooltip, tooltip_text='Place walls')
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_pointer.png', self.setObjectMode,[OBJECT_MODE_SELECT],tooltip=self.tooltip, tooltip_text='Pickup placed objects')
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_actor.png', self.setObjectMode,[OBJECT_MODE_ACTOR],tooltip=self.tooltip, tooltip_text='Place actors (models with animations)')
        self.gui.addButton(self.mode_toolbar_id, 'icon/icon_collision.png', self.setObjectMode,[OBJECT_MODE_COLLISION],tooltip=self.tooltip, tooltip_text='Place Collision solids')
        self.gui.grayOutButtons(self.mode_toolbar_id, (0,6), 0)
        #object-mode select toolbar
        self.select_toolbar_id=self.gui.addToolbar(self.gui.TopRight, (192, 384), icon_size=32, x_offset=-192, y_offset=128, hover_command=self.onToolbarHover, color=(0,0,0, 0.5)) 
        #hack to add text
        self.gui.elements[self.select_toolbar_id]['frame']['text']="X:\nY:\nZ:\nH:\nP:\nR:\n      Scale:"
        self.gui.elements[self.select_toolbar_id]['frame']['text_scale']=32
        self.gui.elements[self.select_toolbar_id]['frame']['text_fg']=(1,1,1,1)
        self.gui.elements[self.select_toolbar_id]['frame']['text_font']=self.gui.fontBig
        self.gui.elements[self.select_toolbar_id]['frame']['text_pos']=(16,-24)
        for i in range(6):
            self.gui.addEntry(self.select_toolbar_id, size_x=180, offset_x=30)
        self.gui.addEntry(self.select_toolbar_id, size_x=125, offset_x=85)
        self.gui.addFloatingButton(self.select_toolbar_id, [128,32], 'icon/apply.png',[32, 232], self.applyTransform,[0] ,tooltip=self.tooltip, tooltip_text='Apply changes in position, rotation and scale')        
        self.gui.addFloatingButton(self.select_toolbar_id, [128,32], 'icon/pickup.png',[32, 272], self.pickUp,[0] ,tooltip=self.tooltip, tooltip_text='Pick up the selected object and move it manualy')        
        self.gui.addFloatingButton(self.select_toolbar_id, [128,32], 'icon/delete.png',[32, 312], self.deleteObject,[0] ,tooltip=self.tooltip, tooltip_text='Delete the selected object')        
        
        
        #extra buttons for height paint mode (up/down/level)
        self.heightmode_toolbar_id=self.gui.addToolbar(self.gui.BottomRight, (192, 32), icon_size=32, y_offset=-32,x_offset=-96, hover_command=self.onToolbarHover, color=(1,1,1, 0.3))        
        self.gui.addButton(self.heightmode_toolbar_id, 'icon/up.png', self.changeHeightMode,[HEIGHT_MODE_UP],tooltip=self.tooltip, tooltip_text='Raise terrain mode (click to set mode)')
        self.gui.addButton(self.heightmode_toolbar_id, 'icon/down.png', self.changeHeightMode,[HEIGHT_MODE_DOWN],tooltip=self.tooltip, tooltip_text='Lower terrain mode (click to set mode)')
        self.gui.addButton(self.heightmode_toolbar_id, 'icon/level.png', self.changeHeightMode,[HEIGHT_MODE_LEVEL],tooltip=self.tooltip, tooltip_text='Level terrain mode (click to set mode)')
        self.gui.grayOutButtons(self.heightmode_toolbar_id, (0,3), 0)
        
        #extra buttons for walkmap paint (walkable/unwealkable)
        self.walkmap_toolbar_id=self.gui.addToolbar(self.gui.BottomRight, (128, 64), icon_size=64, y_offset=-64,x_offset=-128, hover_command=self.onToolbarHover, color=(1,1,1, 0.3))        
        self.gui.addButton(self.walkmap_toolbar_id, 'icon/icon_nowalk.png', self.changeWalkMode,[WALK_MODE_NOWALK],tooltip=self.tooltip, tooltip_text='Paint un-walkable area(marked RED)')
        self.gui.addButton(self.walkmap_toolbar_id, 'icon/icon_walk.png', self.changeWalkMode,[WALK_MODE_WALK],tooltip=self.tooltip, tooltip_text='Paint walkable area')        
        self.gui.grayOutButtons(self.walkmap_toolbar_id, (0,2), 0)
        
        #extra buttons for grass paint (add/remove)
        self.grass_toolbar_id=self.gui.addToolbar(self.gui.BottomRight, (128, 64), icon_size=64, y_offset=-64,x_offset=-128, hover_command=self.onToolbarHover, color=(1,1,1, 0.3))                
        self.gui.addButton(self.grass_toolbar_id, 'icon/no_grass.png', self.changeGrassMode,[GRASS_MODE_REMOVE],tooltip=self.tooltip, tooltip_text='Remove grass')        
        self.gui.addButton(self.grass_toolbar_id, 'icon/grass.png', self.changeGrassMode,[GRASS_MODE_PAINT],tooltip=self.tooltip, tooltip_text='Paint grass')
        self.gui.grayOutButtons(self.grass_toolbar_id, (0,2), 1)
        self.painter.brushes[BUFFER_GRASS].setColor(1,0,0,1)
        
        #properties panel
        self.prop_panel_id=self.gui.addPropPanel()
        self.props=self.gui.elements[self.prop_panel_id]['entry_props']
        self.snap=self.gui.elements[self.prop_panel_id]['entry_snap']        
                
        #object painter
        self.objectPainter=ObjectPainter()
        
        #terrain mesh
        #the 80k mesh loads to slow from egg, using bam
        #self.mesh=loader.loadModel('data/mesh80k.egg') #there's also a 3k, 10k and 35k mesh (can be broken at this point!)
        self.mesh=loader.loadModel('data/mesh80k.bam')
        #load default textures:           
        #TODO(maybe): remove default tex from model ... and fix filtering then somehow
        for tex in self.textures_diffuse[:6]:
            id=self.textures_diffuse.index(tex)
            self.mesh.setTexture(self.mesh.findTextureStage('tex{0}'.format(id+1)), loader.loadTexture(tex), 1)
        for tex in self.textures_normal[:6]:
            id=self.textures_normal.index(tex)
            self.mesh.setTexture(self.mesh.findTextureStage('tex{0}n'.format(id+1)), loader.loadTexture(tex), 1)  
        self.mesh.reparentTo(render)
        self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_f.glsl"))        
        self.mesh.setShaderInput("height", self.painter.textures[BUFFER_HEIGHT]) 
        self.mesh.setShaderInput("atr1", self.painter.textures[BUFFER_ATR]) 
        self.mesh.setShaderInput("atr2", self.painter.textures[BUFFER_ATR2])        
        self.mesh.setShaderInput("walkmap", self.painter.textures[BUFFER_WALK])                
        self.mesh.setTransparency(TransparencyAttrib.MNone)
        self.mesh.node().setBounds(OmniBoundingVolume())
        self.mesh.node().setFinal(1)
        self.mesh.setBin("background", 11)
        self.mesh.setShaderInput("water_level",26.0)
        
        #grass
        self.grass=render.attachNewNode('grass')
        self.CreateGrassTile(uv_offset=Vec2(0,0), pos=(0,0,0), parent=self.grass, fogcenter=Vec3(256,256,0))
        self.CreateGrassTile(uv_offset=Vec2(0,0.5), pos=(0, 256, 0), parent=self.grass, fogcenter=Vec3(256,0,0))
        self.CreateGrassTile(uv_offset=Vec2(0.5,0), pos=(256, 0, 0), parent=self.grass, fogcenter=Vec3(0,256,0))
        self.CreateGrassTile(uv_offset=Vec2(0.5,0.5), pos=(256, 256, 0), parent=self.grass, fogcenter=Vec3(0,0,0))  
        self.grass.setBin("background", 11)       
        self.grass.hide(MASK_WATER)
        self.grass.hide(MASK_SHADOW)
        
        #skydome
        self.skydome = loader.loadModel("data/skydome") 
        self.skydome.setScale(10)                 
        self.skydome.reparentTo(render)            
        self.skydome.setShaderInput("sky", Vec4(0.4,0.6,1.0, 1.0))   
        #self.skydome.setShaderInput("fog", Vec4(1.0,1.0,1.0, 1.0)) 
        self.skydome.setShaderInput("cloudColor", Vec4(0.9,0.9,1.0, 0.8))
        self.skydome.setShaderInput("cloudTile",4.0) 
        self.skydome.setShaderInput("cloudSpeed",0.008)
        self.skydome.setShaderInput("horizont",140.0)
        self.skydome.setBin('background', 1)
        self.skydome.setTwoSided(True)
        self.skydome.node().setBounds(OmniBoundingVolume())
        self.skydome.node().setFinal(1)
        self.skydome.setShader(Shader.load(Shader.SLGLSL, "shaders/cloud_v.glsl", "shaders/cloud_f.glsl"))
        self.skydome.hide(MASK_SHADOW)
        self.skydome.setTransparency(TransparencyAttrib.MNone)
        
        #waterplane
        self.waterNP = loader.loadModel("data/waterplane") 
        self.waterNP.setPos(256, 256, 0)
        self.waterNP.setTransparency(TransparencyAttrib.MAlpha)
        self.waterNP.flattenLight()
        self.waterNP.setPos(0, 0, 26)
        self.waterNP.reparentTo(render)  
        #Add a buffer and camera that will render the reflection texture
        self.wBuffer = base.win.makeTextureBuffer("water", 512, 512)
        self.wBuffer.setClearColorActive(True)
        self.wBuffer.setClearColor(base.win.getClearColor())
        self.wBuffer.setSort(-1)
        self.waterCamera = base.makeCamera(self.wBuffer)
        self.waterCamera.reparentTo(render)
        self.waterCamera.node().setLens(base.camLens)
        self.waterCamera.node().setCameraMask(MASK_WATER)               
        #Create this texture and apply settings
        wTexture = self.wBuffer.getTexture()
        wTexture.setWrapU(Texture.WMClamp)
        wTexture.setWrapV(Texture.WMClamp)
        wTexture.setMinfilter(Texture.FTLinearMipmapLinear)       
        #Create plane for clipping and for reflection matrix
        self.wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, 26))        
        wPlaneNP = render.attachNewNode(PlaneNode("water", self.wPlane))
        tmpNP = NodePath("StateInitializer")
        tmpNP.setClipPlane(wPlaneNP)
        tmpNP.setAttrib(CullFaceAttrib.makeReverse())
        #tmpNP.setAttrib(ColorScaleAttrib.make(Vec4(24.0/200.0, 1.0, 1.0, 1.0)))
        self.waterCamera.node().setInitialState(tmpNP.getState())
        #self.waterCamera.node().showFrustum()
        #self.waterNP.projectTexture(TextureStage("reflection"), wTexture, self.waterCamera)
        #reflect UV generated on the shader - faster(?)
        self.waterNP.setShaderInput('camera',self.waterCamera)
        self.waterNP.setShaderInput("reflection",wTexture)
        
        self.waterNP.setShader(Shader.load(Shader.SLGLSL, "shaders/water_v.glsl", "shaders/water_f.glsl"))
        self.waterNP.setShaderInput("water_norm", loader.loadTexture('data/water.png'))  
        self.waterNP.setShaderInput("height", self.painter.textures[BUFFER_HEIGHT]) 
        self.waterNP.setShaderInput("tile",10.0)
        self.waterNP.setShaderInput("water_level",26.0)
        self.waterNP.setShaderInput("speed",0.02)
        self.waterNP.setShaderInput("wave",Vec3(32.0, 34.0, 0.2))        
        self.waterNP.hide(MASK_WATER)
        self.waterNP.hide(MASK_SHADOW)
        
        #self.controler.waterNP=self.waterNP
        #self.controler.waterCamera=self.waterCamera
        #self.controler.wPlane=self.wPlane
                
        #render.setAttrib(ColorScaleAttrib.make(Vec4(0.0, 0.0, 0.0, 1.0)))
        #light
        #sun
        self.dlight = DirectionalLight('dlight') 
        self.dlight.setColor(VBase4(0.95, 0.95, 0.9, 1))     
        self.mainLight = render.attachNewNode(self.dlight)
        self.mainLight.setP(-60)       
        self.mainLight.setH(90)
        render.setLight(self.mainLight)
        
        #ambient light 
        self.alight = DirectionalLight('dlight') 
        self.alight.setColor(Vec4(.05, .05, .1, 1))     
        self.ambientLight = render.attachNewNode(self.alight)
        #self.ambientLight.setP(-90)       
        #self.ambientLight.setH(90)
        render.setLight(self.ambientLight)
        self.ambientLight.setPos(base.camera.getPos())
        self.ambientLight.setHpr(base.camera.getHpr())
        self.ambientLight.wrtReparentTo(base.camera)
        
        render.setShaderInput("dlight0", self.mainLight)
        render.setShaderInput("dlight1", self.ambientLight)
        render.setShaderInput("ambient", Vec4(.1, .1, .1, 1)) 
        
        #render shadow map
        depth_map = Texture()
        depth_map.setFormat( Texture.FDepthComponent)
        depth_map.setWrapU(Texture.WMBorderColor)
        depth_map.setWrapV(Texture.WMBorderColor) 
        depth_map.setBorderColor(Vec4(1.0, 1.0, 1.0, 1.0)) 
        #depth_map.setMinfilter(Texture.FTShadow )
        #depth_map.setMagfilter(Texture.FTShadow )        
        depth_map.setMinfilter(Texture.FTNearest   )
        depth_map.setMagfilter(Texture.FTNearest   )
        props = FrameBufferProperties()
        props.setRgbColor(0)
        props.setDepthBits(1)
        props.setAlphaBits(0)
        props.set_srgb_color(False)
        depthBuffer = base.win.makeTextureBuffer("Shadow Buffer", 
                                              1024, 
                                              1024, 
                                              to_ram = False, 
                                              tex = depth_map, 
                                              fbp = props)
        depthBuffer.setClearColor(Vec4(1.0,1.0,1.0,1.0)) 
        depthBuffer.setSort(-101)
        shadowCamera = base.makeCamera(depthBuffer) 
        lens = OrthographicLens()
        lens.setFilmSize(500, 500)
        shadowCamera.node().setLens(lens)
        shadowCamera.node().getLens().setNearFar(1,400) 
        shadowCamera.node().setCameraMask(MASK_SHADOW)
        shadowCamera.reparentTo(render)
        #shadowCamera.node().showFrustum()
        shadowCamera.setPos(400, 256, 256)          
        shadowCamera.setHpr(self.mainLight.getHpr())
        #self.shadowNode=render.attachNewNode('shadowNode')
        #self.shadowNode.setPos(self.controler.cameraNode.getPos())
        #shadowCamera.wrtReparentTo(self.shadowNode)            
        render.setShaderInput('shadow', depth_map)
        render.setShaderInput("bias", 1.0)
        render.setShaderInput('shadowCamera',shadowCamera)
        
        #fog
        #rgb color + coefficiency in alpha
        render.setShaderInput("fog",  Vec4(0.4, 0.4, 0.4, 0.002))
        
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
        self.accept('tab', self.nextModel)
        self.accept('f1', self.setMode,[MODE_HEIGHT,'hotkey']) 
        self.accept('f2', self.setMode,[MODE_TEXTURE,'hotkey'])
        self.accept('f3', self.setMode,[MODE_GRASS,'hotkey'])        
        self.accept('f4', self.setMode,[MODE_OBJECT,'hotkey'])        
        self.accept('f5', self.setMode,[MODE_WALK,'hotkey']) 
        #self.accept('f6',self.showSaveMenu)
        self.accept('f7',self.showSaveMenu)
        self.accept('1', self.setAxis,['H: '])
        self.accept('2', self.setAxis,['P: '])
        self.accept('3', self.setAxis,['R: '])
        self.accept('escape', self.objectPainter.stop)        
        self.accept('enter', self.focusOnProperties)  
        self.accept( 'window-event', self.windowEventHandler) 
        
        #make sure things have some/any starting value
        self.setMode(MODE_HEIGHT)
        self.setBrush(0)
        self.painter.brushes[BUFFER_ATR].setColor(0,0,0,1.0)
        self.painter.brushes[BUFFER_ATR2].setColor(0,0,1,1.0)
        
        #tasks
        taskMgr.add(self.perFrameUpdate, 'perFrameUpdate_task', sort=46)  
        
    def setupFilters(self, manager, path=""):    
        colorTex = Texture()#the scene
        auxTex = Texture() # r=blur, g=shadow, b=?, a=?
        blurTex = Texture() #1/2 size of the shadows to be blured            
        blurTex2 = Texture()
        glareTex = Texture()
        flareTex = Texture()
        composeTex=Texture()#the scene(colorTex) blured where auxTex.r>0 and with shadows (blurTex2.r) added
        
        final_quad = manager.renderSceneInto(colortex=colorTex, auxtex=auxTex)        
        #blurr shadows #1
        interquad0 = manager.renderQuadInto(colortex=blurTex, div=2)
        interquad0.setShader(Shader.load(Shader.SLGLSL, path+"shaders/blur_v.glsl", path+"shaders/blur_f.glsl"))
        interquad0.setShaderInput("input_map", auxTex)
        #blurrscene
        interquad1 = manager.renderQuadInto(colortex=blurTex2, div=4)
        interquad1.setShader(Shader.load(Shader.SLGLSL, path+"shaders/blur_v.glsl", path+"shaders/blur_f.glsl"))
        interquad1.setShaderInput("input_map", colorTex)
        #glare
        interquad2 = manager.renderQuadInto(colortex=glareTex, div=4)
        interquad2.setShader(Shader.load(Shader.SLGLSL, path+"shaders/glare_v.glsl", path+"shaders/glare_f.glsl"))
        interquad2.setShaderInput("auxTex", auxTex)  
        interquad2.setShaderInput("colorTex", colorTex)
        interquad2.setShaderInput("blurTex", blurTex)
        #lense flare
        interquad3 = manager.renderQuadInto(colortex=flareTex, div=2)
        interquad3.setShader(Shader.load(path+"shaders/lens_flare.sha"))
        interquad3.setShaderInput("tex0", glareTex)
        #compose the scene
        interquad4 = manager.renderQuadInto(colortex=composeTex)
        interquad4.setShader(Shader.load(Shader.SLGLSL, path+"shaders/compose_v.glsl", path+"shaders/compose_f.glsl"))
        interquad4.setShaderInput("flareTex", flareTex)
        interquad4.setShaderInput("glareTex", glareTex)
        interquad4.setShaderInput("colorTex", colorTex)
        interquad4.setShaderInput("blurTex", blurTex)
        interquad4.setShaderInput("blurTex2", blurTex2)
        interquad4.setShaderInput("auxTex", auxTex)   
        interquad4.setShaderInput("noiseTex", loader.loadTexture(path+"data/noise2.png"))    
        interquad4.setShaderInput('time', 0.0)   
        #fxaa
        final_quad.setShader(Shader.load(Shader.SLGLSL, path+"shaders/fxaa_v.glsl", path+"shaders/fxaa_f.glsl"))
        final_quad.setShaderInput("tex0", composeTex)
        final_quad.setShaderInput("rt_w",float(base.win.getXSize()))
        final_quad.setShaderInput("rt_h",float(base.win.getYSize()))
        final_quad.setShaderInput("FXAA_SPAN_MAX" , float(8.0))
        final_quad.setShaderInput("FXAA_REDUCE_MUL", float(1.0/8.0))
        final_quad.setShaderInput("FXAA_SUBPIX_SHIFT", float(1.0/4.0))
        return [interquad0, interquad1, interquad2, interquad3, interquad4, final_quad]        

    
    def deleteObject(self, not_used=None, guiEvent=None):
        node=self.objectPainter.selectedObject
        if node:
            if node in self.objectPainter.actors:
                self.objectPainter.actors.pop(self.objectPainter.actors.index(node)).cleanup() 
            node.removeNode()
            self.objectPainter.selectedObject=None
            self.setObjectMode(OBJECT_MODE_ONE)
            self.props.set('') 
            
    def applyTransform(self, not_used=None, guiEvent=None):
        x=self.gui.elements[self.select_toolbar_id]['buttons'][0].get()        
        y=self.gui.elements[self.select_toolbar_id]['buttons'][1].get()
        z=self.gui.elements[self.select_toolbar_id]['buttons'][2].get()
        h=self.gui.elements[self.select_toolbar_id]['buttons'][3].get()
        p=self.gui.elements[self.select_toolbar_id]['buttons'][4].get()
        r=self.gui.elements[self.select_toolbar_id]['buttons'][5].get()
        scale=self.gui.elements[self.select_toolbar_id]['buttons'][6].get()
        x=self.objectPainter._stringToFloat(x)
        y=self.objectPainter._stringToFloat(y)
        z=self.objectPainter._stringToFloat(z)
        h=self.objectPainter._stringToFloat(h)
        p=self.objectPainter._stringToFloat(p)
        r=self.objectPainter._stringToFloat(r)
        scale=self.objectPainter._stringToFloat(scale)
        self.objectPainter.selectedObject.setPosHpr((x,y,z), (h,p,r))
        self.objectPainter.selectedObject.setScale(scale)
        self.gui.elements[self.select_toolbar_id]['buttons'][0]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][1]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][2]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][3]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][4]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][5]['focus']=0
        self.gui.elements[self.select_toolbar_id]['buttons'][6]['focus']=0
        
        props=self.props.get()
        self.objectPainter.selectedObject.setPythonTag('props', props) 
        self.props.set('')
        self.props['focus']=0        
        self.gui.hideElement(self.select_toolbar_id)
        self.setObjectMode(OBJECT_MODE_SELECT)
        
    def pickUp(self, not_used=None, guiEvent=None):   
        self.objectPainter.pickup()
        self.setObjectMode(OBJECT_MODE_ONE)
        self.heading_info['text']=self.objectPainter.adjustHpr(0,self.hpr_axis)
        self.size_info['text']='%.2f'%self.objectPainter.currentScale
        self.color_info['text']='%.2f'%self.objectPainter.currentZ   
        self.props.set(self.objectPainter.currentObject.getPythonTag('props'))
    
    def configSkySea(self, options=False, guiEvent=None):    
        if options==True:
            self.ignoreHover=True
            self.painter.hideBrushes()
            self.gui.SkySeaFrame.show()
            self.ignore('mouse1-up')
            self.ignore('mouse1')
        elif options==False:    
            self.ignoreHover=False
            self.gui.SkySeaFrame.hide()
            self.setMode(self.mode)
        else: 
            self.ignoreHover=False
            self.gui.SkySeaFrame.hide()
            self.setMode(self.mode)
            sky=Vec4(self.gui.SkySeaOptions[0][0],self.gui.SkySeaOptions[0][1],self.gui.SkySeaOptions[0][2],self.gui.SkySeaOptions[0][3])
            fog=Vec4(self.gui.SkySeaOptions[1][0],self.gui.SkySeaOptions[1][1],self.gui.SkySeaOptions[1][2],self.gui.SkySeaOptions[1][3])
            cloudColor=Vec4(self.gui.SkySeaOptions[2][0],self.gui.SkySeaOptions[2][1],self.gui.SkySeaOptions[2][2],self.gui.SkySeaOptions[2][3])
            cloudTile=self.gui.SkySeaOptions[3]
            cloudSpeed=self.gui.SkySeaOptions[4]
            horizont=self.gui.SkySeaOptions[5]
            tile=self.gui.SkySeaOptions[6]
            speed=self.gui.SkySeaOptions[7]
            wave=Vec3(self.gui.SkySeaOptions[8][0],self.gui.SkySeaOptions[8][1],self.gui.SkySeaOptions[8][2])
            water_z=self.gui.SkySeaOptions[9]            
            self.skydome.setShaderInput("sky", sky)   
            render.setShaderInput("fog", fog) 
            self.skydome.setShaderInput("cloudColor", cloudColor)
            self.skydome.setShaderInput("cloudTile",cloudTile) 
            self.skydome.setShaderInput("cloudSpeed",cloudSpeed)
            self.skydome.setShaderInput("horizont",horizont)
            self.mesh.setShaderInput("water_level",water_z)
            if water_z>0.0:
                self.wBuffer.setActive(True)
                self.waterNP.show()
                self.waterNP.setShaderInput("tile",tile)
                self.waterNP.setShaderInput("speed",speed)                
                self.waterNP.setShaderInput("water_level",water_z)
                self.waterNP.setShaderInput("wave",wave)
                self.waterNP.setPos(0, 0, water_z)
                self.wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, water_z))
                wPlaneNP = render.attachNewNode(PlaneNode("water", self.wPlane))
                self.mesh.setShaderInput("water_level",water_z)
                tmpNP = NodePath("StateInitializer")
                tmpNP.setClipPlane(wPlaneNP)
                tmpNP.setAttrib(CullFaceAttrib.makeReverse())
                tmpNP.setAttrib(ColorScaleAttrib.make(Vec4((water_z-2.0)/200.0, 0.0, 0.0, 0.0)))
                self.waterCamera.node().setInitialState(tmpNP.getState())
            else:
                self.waterNP.hide()
                self.wBuffer.setActive(False)	
                
    def configBrush(self, options=False, guiEvent=None):    
        if options==True:
            self.ignoreHover=True
            self.painter.hideBrushes()
            self.gui.ConfigFrame.show()
            self.ignore('mouse1-up')
            self.ignore('mouse1')
            self.gui.ConfigEntry[0].enterText(self.size_info['text'])
            self.gui.ConfigEntry[1].enterText(self.color_info['text'])
            if self.mode==MODE_OBJECT:
                self.gui.ConfigEntry[2].enterText(str(self.objectPainter.currentHPR[0]))
                self.gui.ConfigEntry[3].enterText(str(self.objectPainter.currentHPR[1]))
                self.gui.ConfigEntry[4].enterText(str(self.objectPainter.currentHPR[2]))
            else:
                self.gui.ConfigEntry[2].enterText(str(self.painter.brushes[0].getH()))
                self.gui.ConfigEntry[3].enterText('0.0')
                self.gui.ConfigEntry[4].enterText('0.0')
            self.gui.ConfigEntry[5].enterText(str(self.grid_scale))
            self.gui.ConfigEntry[6].enterText(str(self.grid_z))            
        elif options==False:    
            self.ignoreHover=False
            self.gui.ConfigFrame.hide()
            self.setMode(self.mode)
        else: 
            self.ignoreHover=False
            self.gui.ConfigFrame.hide()
            self.setMode(self.mode) 
            self.grid.setTexScale(TextureStage.getDefault(), self.gui.ConfigOptions['grid'], self.gui.ConfigOptions['grid'], 1)
            self.grid.setZ(self.gui.ConfigOptions['grid_z'])   
            self.grid_scale=self.gui.ConfigOptions['grid']
            self.grid_z=self.gui.ConfigOptions['grid_z']
            self.painter.pointer.setZ(self.gui.ConfigOptions['grid_z'])
            self.painter.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, self.gui.ConfigOptions['grid_z'])) 
            self.controler.cameraNode.setZ(self.gui.ConfigOptions['grid_z'])
            if self.mode==MODE_OBJECT:
                #hpr
                self.setAxis='H: '
                self.heading_info['text']=self.setAxis+str(self.gui.ConfigOptions['hpr'][0])
                self.objectPainter.currentHPR=self.gui.ConfigOptions['hpr']                
                #scale
                self.objectPainter.currentScale=self.gui.ConfigOptions['scale']
                self.size_info['text']='%.2f'%self.objectPainter.currentScale
                #alpha (Z)
                self.objectPainter.currentZ=self.gui.ConfigOptions['alpha']
                self.color_info['text']='%.2f'%self.objectPainter.currentZ    
            else:
                #hpr                                
                for brush in self.painter.brushes:            
                    brush.setH(self.gui.ConfigOptions['hpr'][0])
                self.heading_info['text']=self.hpr_axis+'%.0f'%self.painter.brushes[0].getH()                
                #scale                               
                self.painter.brushSize=self.gui.ConfigOptions['scale']                
                self.painter.adjustBrushSize(0)
                self.size_info['text']='%.2f'%self.painter.brushSize
                #alpha (color)
                if self.mode==MODE_HEIGHT and self.height_mode==HEIGHT_MODE_LEVEL:
                    self.tempColor=self.gui.ConfigOptions['alpha']
                    self.painter.brushes[BUFFER_HEIGHT].setColor(self.tempColor,self.tempColor,self.tempColor,1)
                    self.color_info['text']='%.2f'%self.tempColor                
                else:
                    self.painter.brushAlpha=self.gui.ConfigOptions['alpha']
                    self.painter.adjustBrushAlpha(0)                    
                    self.color_info['text']='%.2f'%self.painter.brushAlpha    
                    
    def changeGrassMode(self, mode=None, guiEvent=None):
        self.gui.grayOutButtons(self.grass_toolbar_id, (0,2), mode)          
        self.painter.brushes[BUFFER_GRASS].setColor(mode,0,0,1)        
            
    def changeWalkMode(self, mode=None, guiEvent=None):
        self.gui.grayOutButtons(self.walkmap_toolbar_id, (0,2), mode)
        if mode==WALK_MODE_NOWALK:
            self.painter.brushes[BUFFER_WALK].setColor(1,0,0, 1.0)  
        else:    
            self.painter.brushes[BUFFER_WALK].setColor(0,0,0, 1.0)  
        
    def changeHeightMode(self, mode=None, guiEvent=None):
        if mode==None:
            mode=self.height_mode+1
        if mode>HEIGHT_MODE_LEVEL:
            mode=HEIGHT_MODE_UP
        if mode==HEIGHT_MODE_UP:
            self.tempColor=1            
            self.painter.brushAlpha=self.tempAlpha
            self.painter.brushes[BUFFER_HEIGHT].setColor(1,1,1,self.painter.brushAlpha)
            self.color_info['text']='%.2f'%self.tempAlpha
        if mode==HEIGHT_MODE_DOWN:
            self.tempColor=0
            self.painter.brushAlpha=self.tempAlpha
            self.painter.brushes[BUFFER_HEIGHT].setColor(0,0,0,self.painter.brushAlpha)
            self.color_info['text']='%.2f'%self.tempAlpha
        if mode==HEIGHT_MODE_LEVEL:
            self.tempColor=self.painter.brushAlpha
            self.tempAlpha=self.painter.brushAlpha
            self.painter.brushAlpha=1
            self.painter.brushes[BUFFER_HEIGHT].setColor(self.tempColor,self.tempColor,self.tempColor,1)
            self.color_info['text']='%.2f'%self.tempColor
        self.gui.grayOutButtons(self.heightmode_toolbar_id, (0,3), mode)
        self.height_mode=mode        
        
    def focusOnProperties(self):
        self.props['focus']=1
        
    def setRandomWall(self, model_path=None, id=None, guiEvent=None):        
        if id!=None:
            self.gui.blink(self.multi_toolbar_id, id)
        if model_path==None:
            model_path=self.last_model_path
        models=[]
        dirList=os.listdir(Filename(model_path).toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('egg', 'bam'):
                models.append(model_path+fname)
        self.objectPainter.loadWall(random.choice(models))                      
        self.last_model_path=model_path
        
    def nextWall(self, model_path=None):        
        if model_path==None:
            model_path=self.last_model_path
        models=[]
        dirList=os.listdir(Filename(model_path).toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('egg', 'bam'):
                models.append(model_path+fname)
        if self.objectPainter.currentWall:
            self.objectPainter.loadWall(random.choice(models), True)
        else:
            self.objectPainter.loadModel(random.choice(models))
        self.last_model_path=model_path
    
    def setRandomObject(self, model_path=None, id=None, guiEvent=None):
        if id!=None:
            self.gui.blink(self.multi_toolbar_id, id)
        if model_path==None:
            model_path=self.last_model_path
        models=[]
        dirList=os.listdir(Filename(model_path).toOsSpecific())
        for fname in dirList:
            if  Filename(fname).getExtension() in ('egg', 'bam'):
                models.append(model_path+fname)
        self.objectPainter.loadModel(random.choice(models))              
        #self.objectPainter.adjustHpr(random.randint(0,72)*5,axis='H: ')
        #self.objectPainter.adjustScale(random.randint(-1,1)*0.05)
        #self.heading_info['text']=self.objectPainter.adjustHpr(0,self.hpr_axis)
        #self.size_info['text']='%.2f'%self.objectPainter.currentScale
        self.last_model_path=model_path
        
    def setActor(self, model, id=None, guiEvent=None): 
        if id!=None:
            self.gui.blink(self.object_toolbar_id, id)
            self.objectPainter.loadActor(model)
            
    def setObject(self, model, id=None, guiEvent=None): 
        if id!=None:
            self.gui.blink(self.object_toolbar_id, id)
            self.objectPainter.loadModel(model)
            
    def setAxis(self, axis):        
        if self.mode==MODE_OBJECT:
            self.hpr_axis=axis  
            self.heading_info['text']=self.objectPainter.adjustHpr(0,axis)
        else:
            return
        
    def setObjectMode(self, mode, guiEvent=None): 
        self.gui.grayOutButtons(self.mode_toolbar_id, (0,6), mode)
        self.object_mode=mode        
        if guiEvent!=None:
            self.objectPainter.stop()
        if mode==OBJECT_MODE_ONE:
            self.gui.showElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(1))
        if mode==OBJECT_MODE_MULTI:
            self.gui.showElement(self.multi_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(1))
        if mode==OBJECT_MODE_WALL:        
            self.gui.showElement(self.wall_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(1))            
        if mode==OBJECT_MODE_SELECT:
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)            
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(2))            
        if mode==OBJECT_MODE_ACTOR:
            self.gui.showElement(self.actor_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(1))
        if mode==OBJECT_MODE_COLLISION:
            self.gui.showElement(self.collision_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id) 
            self.gui.hideElement(self.select_toolbar_id) 
            self.objectPainter.pickerNode.setFromCollideMask(BitMask32.bit(1))
            
    def hideDialog(self, guiEvent=None): 
        self.gui.dialog.hide()
   
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
        
    def CreateGrassTile(self, uv_offset, pos, parent, fogcenter=Vec3(0,0,0), count=256):
        grass=loader.loadModel("data/grass_model")
        grass.reparentTo(parent)
        grass.setInstanceCount(count) 
        grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
        grass.node().setFinal(1)
        grass.setShader(Shader.load(Shader.SLGLSL, "shaders/grass_v.glsl", "shaders/grass_f.glsl"))
        grass.setShaderInput('height', self.painter.textures[BUFFER_HEIGHT]) 
        grass.setShaderInput('grass', self.painter.textures[BUFFER_GRASS])
        grass.setShaderInput('uv_offset', uv_offset)   
        grass.setShaderInput('fogcenter', fogcenter)
        grass.setPos(pos)
        return grass
        
    def load(self, guiEvent=None):
        save_dir=path+self.gui.entry1.get()
        feedback=""
        if self.gui.flags[0]:#height map
            print "loading height map...",
            file=path+save_dir+"/"+self.gui.entry2.get()+'.png'            
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_HEIGHT].setTexture(loader.loadTexture(file))
                print "done"                
            else:
                print "FILE NOT FOUND!"
                feedback+=file +' '   
        if self.gui.flags[1]:#atr map, both
            print "loading detail map...",
            file=path+save_dir+"/"+self.gui.entry3.get()+'0.png'
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_ATR].setTexture(loader.loadTexture(file))
                print "ok...",                
            else:
                print "FILE NOT FOUND!"            
                feedback+=file+' '
            file=path+save_dir+"/"+self.gui.entry3.get()+'1.png'
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_ATR2].setTexture(loader.loadTexture(file))
                print "done"    
            else:
                print "FILE NOT FOUND!"            
                feedback+=file+' '  
        if self.gui.flags[2]:#grass map
            print "loading grass map...",
            file=path+save_dir+"/"+self.gui.entry5.get()+'.png' 
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_GRASS].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"  
                feedback+=file+' '
        if self.gui.flags[4]:#objects and textures used for terrain
            print "loading objects",
            file=path+save_dir+"/"+self.gui.entry6.get()+'.json' 
            if os.path.exists(file):
                data=LoadScene(file, self.objectPainter.quadtree, self.objectPainter.actors, self.mesh, self.textures_diffuse, self.curent_textures)
                i=0
                for id in self.curent_textures:
                    self.gui.elements[self.palette_id]['buttons'][i]['frameTexture']=self.textures_diffuse[id]
                    i+=1
                #load sky and water data
                self.gui.setSkySeaValues(data)
                sky=Vec4(data[0]['sky'][0], data[0]['sky'][1], data[0]['sky'][2], data[0]['sky'][3])
                fog=Vec4(data[0]['fog'][0], data[0]['fog'][1], data[0]['fog'][2], data[0]['fog'][3])
                cloudColor=Vec4(data[0]['cloudColor'][0], data[0]['cloudColor'][1], data[0]['cloudColor'][2], data[0]['cloudColor'][3])
                cloudTile=data[0]['cloudTile']
                cloudSpeed=data[0]['cloudSpeed']
                horizont=data[0]['horizont']
                tile=data[0]['tile']
                speed=data[0]['speed']
                wave=Vec3(data[0]['wave'][0], data[0]['wave'][1], data[0]['wave'][2])
                water_z=data[0]['water_z']            
                self.skydome.setShaderInput("sky", sky)   
                render.setShaderInput("fog", fog) 
                self.skydome.setShaderInput("cloudColor", cloudColor)
                self.skydome.setShaderInput("cloudTile",cloudTile) 
                self.skydome.setShaderInput("cloudSpeed",cloudSpeed)
                self.skydome.setShaderInput("horizont",horizont)
                self.mesh.setShaderInput("water_level",water_z)
                if water_z>0.0:
                    self.wBuffer.setActive(True)
                    self.waterNP.show()
                    self.waterNP.setShaderInput("tile",tile)
                    self.waterNP.setShaderInput("speed",speed)                
                    self.waterNP.setShaderInput("water_level",water_z)
                    self.waterNP.setShaderInput("wave",wave)
                    self.waterNP.setPos(0, 0, water_z)
                    self.wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, water_z))
                    wPlaneNP = render.attachNewNode(PlaneNode("water", self.wPlane))
                    self.mesh.setShaderInput("water_level",water_z)
                    tmpNP = NodePath("StateInitializer")
                    tmpNP.setClipPlane(wPlaneNP)
                    tmpNP.setAttrib(CullFaceAttrib.makeReverse())
                    tmpNP.setAttrib(ColorScaleAttrib.make(Vec4((water_z-2.0)/200.0, 0.0, 0.0, 0.0)))
                    self.waterCamera.node().setInitialState(tmpNP.getState())
                else:
                    self.waterNP.hide()
                    self.wBuffer.setActive(False)    
                print "done"
            else:
                print "FILE NOT FOUND!"  
                feedback+=file+' '    
        if self.gui.flags[5]:#collision
            print "loading collision mesh...",
            file=path+save_dir+"/"+self.gui.entry7.get()+'.egg' 
            if os.path.exists(file):
                if self.collision_mesh:
                    self.collision_mesh.removeNode()
                self.collision_mesh=loader.loadModel(file)
                self.collision_mesh.reparentTo(render)
                self.collision_mesh.setCollideMask(BitMask32.bit(1))
                print "done"
            else:
                print "FILE NOT FOUND!"  
                feedback+=file+' '
        if self.gui.flags[6]:#nav map
            print "loading navigation map...",
            file=path+save_dir+"/"+self.gui.entry8.get()+".png"
            if os.path.exists(file):
                self.painter.paintPlanes[BUFFER_WALK].setTexture(loader.loadTexture(file))
                print "done"
            else:
                print "FILE NOT FOUND!"  
                feedback+=file+' '               
        print "Loading DONE!"         
        if feedback!="":            
            self.gui.okDialog(text="Some files are missing:\n"+feedback, command=self.hideDialog)       
        self.hideSaveMenu()
        
        
    def save(self, override, guiEvent=None):          
        save_dir=path+self.gui.entry1.get()        
        if os.path.exists(path+save_dir):
            if override=="ASK":                
                self.gui.yesNoDialog(text=save_dir+" already exists! \nOverride files?", command=self.save,arg=[])
                self.gui.SaveLoadFrame.hide()                
                return    
            if override==False:
                self.gui.dialog.hide()
                self.hideSaveMenu()
                return
        else:
            os.makedirs(Filename(path+save_dir).toOsSpecific())            
        if self.gui.flags[0]:#height map
            print "saving height map...",
            self.painter.write(BUFFER_HEIGHT, path+save_dir+"/"+self.gui.entry2.get()+'.png')
            print "done"
        if self.gui.flags[1]:#atr maps
            print "saving detail map...",
            self.painter.write(BUFFER_ATR, path+save_dir+"/"+self.gui.entry3.get()+'0.png')
            print "ok... "
            self.painter.write(BUFFER_ATR2, path+save_dir+"/"+self.gui.entry3.get()+'1.png')
            print "done"        
        if self.gui.flags[2]:#grass map
            print "saving grass map...",
            self.painter.write(BUFFER_GRASS, path+save_dir+"/"+self.gui.entry5.get()+'.png')         
            print "done"   
        if self.gui.flags[4]:#objects and textures used
            print "saving objects...",
            #sky and water data
            sky=(self.gui.SkySeaOptions[0][0],self.gui.SkySeaOptions[0][1],self.gui.SkySeaOptions[0][2],self.gui.SkySeaOptions[0][3])
            fog=(self.gui.SkySeaOptions[1][0],self.gui.SkySeaOptions[1][1],self.gui.SkySeaOptions[1][2],self.gui.SkySeaOptions[1][3])
            cloudColor=(self.gui.SkySeaOptions[2][0],self.gui.SkySeaOptions[2][1],self.gui.SkySeaOptions[2][2],self.gui.SkySeaOptions[2][3])
            cloudTile=self.gui.SkySeaOptions[3]
            cloudSpeed=self.gui.SkySeaOptions[4]
            horizont=self.gui.SkySeaOptions[5]
            tile=self.gui.SkySeaOptions[6]
            speed=self.gui.SkySeaOptions[7]
            wave=(self.gui.SkySeaOptions[8][0],self.gui.SkySeaOptions[8][1],self.gui.SkySeaOptions[8][2])
            water_z=self.gui.SkySeaOptions[9]
            sky_water={'sky':sky,'fog':fog,
                        'cloudColor':cloudColor,
                        'cloudTile':cloudTile,
                        'cloudSpeed':cloudSpeed,
                        'horizont':horizont,
                        'tile':tile,
                        'speed':speed, 
                        'wave':wave,
                        'water_z':water_z}
            SaveScene(path+save_dir+"/"+self.gui.entry6.get()+'.json', self.objectPainter.quadtree, self.textures_diffuse, self.curent_textures, sky_water)
            print "done"        
        if self.gui.flags[5]:#collison
            print "saving collision mesh...",
            self.genCollision(True, path+save_dir+"/"+self.gui.entry7.get()+'.egg')    
            print "done"
        if self.gui.flags[6]:#navmesh
            print "saving Navigation Mesh(CSV) and map...",            
            map=self.painter.write(BUFFER_WALK, path+save_dir+"/"+self.gui.entry8.get()+'.png', True)
            GenerateNavmeshCSV(map, path+save_dir+"/"+self.gui.entry8.get()+'.csv')            
            print "done"    
        print "SAVING DONE!" 
        self.gui.okDialog(text="Files saved to:\n"+save_dir, command=self.hideDialog)    
        self.hideSaveMenu()              
    
    def setTex(self, layer, id, guiEvent=None): 
        self.curent_textures[layer]=id
        self.mesh.setTexture(self.mesh.findTextureStage('tex'+str(layer+1)), loader.loadTexture(self.textures_diffuse[id]), 1)
        self.mesh.setTexture(self.mesh.findTextureStage('tex'+str(layer+1)+'n'), loader.loadTexture(self.textures_normal[id]), 1)        
        self.gui.elements[self.palette_id]['buttons'][layer]['frameTexture']=self.textures_diffuse[id]
        
    def changeTex(self, layer, guiEvent=None): 
        id=self.curent_textures[layer]+1
        while id in self.curent_textures:            
            if id>len(self.textures_diffuse)-1:
                id=0
            else:
                id+=1
        if id>len(self.textures_diffuse)-1:
            id=0        
        self.curent_textures[layer]=id
        self.mesh.setTexture(self.mesh.findTextureStage('tex'+str(layer+1)), loader.loadTexture(self.textures_diffuse[id]), 1)
        self.mesh.setTexture(self.mesh.findTextureStage('tex'+str(layer+1)+'n'), loader.loadTexture(self.textures_normal[id]), 1)        
        self.gui.elements[self.palette_id]['buttons'][layer]['frameTexture']=self.textures_diffuse[id]
                    
    def setBrush(self, id, guiEvent=None):
        self.painter.setBrushTex(id)
        for button in self.gui.elements[0]['buttons']:
            button.setColor(0,0,0, 1)
        self.gui.elements[0]['buttons'][id].setColor(0,0,1, 1)
     
    def paint(self):
        if self.mode==MODE_OBJECT:
            self.props['focus']=0
            self.snap['focus']=0
            props=self.props.get()            
            if self.object_mode in(OBJECT_MODE_ONE,OBJECT_MODE_COLLISION, OBJECT_MODE_ACTOR):
                self.objectPainter.drop(props)
                self.props.set('')                
            elif self.object_mode==OBJECT_MODE_PICKUP:
                if self.objectPainter.pickup():
                    self.setObjectMode(OBJECT_MODE_ONE)
                    self.heading_info['text']=self.objectPainter.adjustHpr(0,self.hpr_axis)
                    self.size_info['text']='%.2f'%self.objectPainter.currentScale
                    self.color_info['text']='%.2f'%self.objectPainter.currentZ   
                    self.props.set(self.objectPainter.currentObject.getPythonTag('props'))
            elif self.object_mode==OBJECT_MODE_MULTI: 
                self.objectPainter.drop(props)
                self.setRandomObject()
            elif self.object_mode==OBJECT_MODE_WALL:
                self.objectPainter.drop(props)
                self.objectPainter.currentObject=render.attachNewNode('temp')
                self.setRandomWall()
            elif self.object_mode==OBJECT_MODE_SELECT:    
                if self.objectPainter.select():
                    self.gui.showElement(self.select_toolbar_id)
                    pos=self.objectPainter.selectedObject.getPos()
                    hpr=self.objectPainter.selectedObject.getHpr()                    
                    scale=self.objectPainter.selectedObject.getScale()
                    props=self.objectPainter.selectedObject.getPythonTag('props')                    
                    self.gui.elements[self.select_toolbar_id]['buttons'][0].enterText('%.2f'%pos[0])
                    self.gui.elements[self.select_toolbar_id]['buttons'][1].enterText('%.2f'%pos[1])
                    self.gui.elements[self.select_toolbar_id]['buttons'][2].enterText('%.2f'%pos[2])
                    self.gui.elements[self.select_toolbar_id]['buttons'][3].enterText('%.2f'%hpr[0])
                    self.gui.elements[self.select_toolbar_id]['buttons'][4].enterText('%.2f'%hpr[1])
                    self.gui.elements[self.select_toolbar_id]['buttons'][5].enterText('%.2f'%hpr[2])
                    self.gui.elements[self.select_toolbar_id]['buttons'][6].enterText('%.2f'%scale[0])
                    self.props.enterText(props)
                    
    def setMode(self, mode, guiEvent=None):        
        if mode==MODE_HEIGHT:
            if guiEvent!=None:
                self.painter.brushAlpha=0.05
                self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.gui.grayOutButtons(self.statusbar, (4,9), 4)
            self.painter.brushes[BUFFER_HEIGHT].show()
            self.painter.brushes[BUFFER_HEIGHT].setColor(self.tempColor, self.tempColor, self.tempColor, self.painter.brushAlpha)
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_ATR2].hide()
            self.painter.brushes[BUFFER_GRASS].hide() 
            self.painter.brushes[BUFFER_WALK].hide() 
            self.painter.pointer.show()
            self.hpr_axis=''
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])            
            self.gui.hideElement(self.palette_id)            
            self.gui.showElement(self.toolbar_id)
            self.gui.showElement(self.heightmode_toolbar_id)
            self.gui.hideElement(self.mode_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.prop_panel_id)
            self.gui.hideElement(self.walkmap_toolbar_id)
            self.gui.hideElement(self.grass_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.stop()
            self.mesh.setShaderInput("walkmap", loader.loadTexture('data/walkmap.png'))
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_f.glsl"))  
        elif mode==MODE_TEXTURE:
            if guiEvent!=None:    
                self.painter.brushAlpha=1.0
                self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.gui.grayOutButtons(self.statusbar, (4,9), 5)
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].show()
            self.painter.brushes[BUFFER_ATR2].show()
            self.painter.brushes[BUFFER_GRASS].hide()
            self.painter.brushes[BUFFER_WALK].hide() 
            self.painter.pointer.show()     
            self.hpr_axis=''        
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.showElement(self.palette_id)            
            self.gui.showElement(self.toolbar_id)
            self.gui.hideElement(self.mode_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.prop_panel_id)
            self.gui.hideElement(self.heightmode_toolbar_id)
            self.gui.hideElement(self.walkmap_toolbar_id)
            self.gui.hideElement(self.grass_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.stop()
            self.mesh.setShaderInput("walkmap", loader.loadTexture('data/walkmap.png'))
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_f.glsl"))  
        elif mode==MODE_GRASS:
            if guiEvent!=None:
                self.painter.brushAlpha=1.0
                self.color_info['text']='%.2f'%self.painter.brushAlpha
            self.gui.grayOutButtons(self.statusbar, (4,9), 6)
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_ATR2].hide()   
            self.painter.brushes[BUFFER_WALK].hide()            
            self.painter.brushes[BUFFER_GRASS].show()
            #self.painter.brushes[BUFFER_GRASS].setColor(1,0,0, self.painter.brushAlpha)  
            self.painter.pointer.show() 
            self.hpr_axis=''      
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.hideElement(self.palette_id)
            self.gui.showElement(self.toolbar_id)
            self.gui.hideElement(self.mode_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.prop_panel_id)
            self.gui.hideElement(self.heightmode_toolbar_id)
            self.gui.hideElement(self.walkmap_toolbar_id)
            self.gui.showElement(self.grass_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.stop()
            self.mesh.setShaderInput("walkmap", loader.loadTexture('data/walkmap.png'))
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_f.glsl"))              
        elif mode==MODE_OBJECT:
            if guiEvent!=None:                
                self.hpr_axis='H: '
                if self.collision_mesh==None: 
                    self.gui.yesNoDialog("To place objects a collision mesh is needed.\nGenerate Collision Mesh?", self.genCollision,['temp/collision.egg'])
            self.painter.hideBrushes() 
            self.painter.pointer.hide()            
            self.gui.grayOutButtons(self.statusbar, (4,9), 7) 
            self.gui.hideElement(self.palette_id)
            self.gui.hideElement(self.toolbar_id)
            self.gui.hideElement(self.heightmode_toolbar_id)
            self.gui.showElement(self.mode_toolbar_id)
            self.gui.showElement(self.prop_panel_id)
            self.gui.hideElement(self.walkmap_toolbar_id)
            self.gui.hideElement(self.grass_toolbar_id)
            self.setObjectMode(self.object_mode)            
            self.accept('mouse1', self.paint)                
            self.ignore('mouse1-up')
            self.mesh.setShaderInput("walkmap", self.painter.textures[BUFFER_WALK])
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_w_f.glsl"))  
        elif mode==MODE_WALK:
            if guiEvent!=None:
                self.painter.brushAlpha=1.0
                self.color_info['text']='%.2f'%self.painter.brushAlpha
                self.changeWalkMode(WALK_MODE_NOWALK)
            self.gui.grayOutButtons(self.statusbar, (4,9), 8)
            self.painter.brushes[BUFFER_HEIGHT].hide()
            self.painter.brushes[BUFFER_ATR].hide()
            self.painter.brushes[BUFFER_ATR2].hide()             
            self.painter.brushes[BUFFER_GRASS].hide()    
            self.painter.brushes[BUFFER_WALK].show()             
            self.painter.pointer.show() 
            self.hpr_axis=''      
            self.accept('mouse1', self.keyMap.__setitem__, ['paint', True])                
            self.accept('mouse1-up', self.keyMap.__setitem__, ['paint', False])
            self.gui.hideElement(self.palette_id)
            self.gui.showElement(self.toolbar_id)
            self.gui.hideElement(self.mode_toolbar_id)
            self.gui.hideElement(self.object_toolbar_id)
            self.gui.hideElement(self.multi_toolbar_id)
            self.gui.hideElement(self.wall_toolbar_id)
            self.gui.hideElement(self.actor_toolbar_id)
            self.gui.hideElement(self.collision_toolbar_id)
            self.gui.hideElement(self.prop_panel_id)
            self.gui.hideElement(self.heightmode_toolbar_id)
            self.gui.showElement(self.walkmap_toolbar_id)
            self.gui.hideElement(self.grass_toolbar_id)
            self.gui.hideElement(self.select_toolbar_id)
            self.objectPainter.stop() 
            self.mesh.setShaderInput("walkmap", self.painter.textures[BUFFER_WALK])
            self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/terrain_v.glsl", "shaders/terrain_w_f.glsl"))              
        self.mode=mode
        self.heading_info['text']=self.hpr_axis+'%.0f'%self.painter.brushes[0].getH()
        
    def genCollision(self, yes, file, guiEvent=None):
        if yes:
            heightmap=PNMImage(self.painter.buffSize[BUFFER_HEIGHT], self.painter.buffSize[BUFFER_HEIGHT],4)              
            base.graphicsEngine.extractTextureData(self.painter.textures[BUFFER_HEIGHT],base.win.getGsg())
            self.painter.textures[BUFFER_HEIGHT].store(heightmap)
            GenerateCollisionEgg(heightmap, file, input='data/collision80k.egg')
            if self.collision_mesh:
                self.collision_mesh.removeNode()
            self.collision_mesh=loader.loadModel(file, noCache=True)
            self.collision_mesh.reparentTo(render)  
            self.collision_mesh.setCollideMask(BitMask32.bit(1))
        if guiEvent!=None:     
            self.gui.dialog.hide()   
            if yes:
                self.gui.okDialog(text="Collision mesh saved to:\n"+file, command=self.hideDialog)
            
    def nextModel(self):                
        if self.mode==MODE_OBJECT:
            if self.object_mode==OBJECT_MODE_MULTI:
                self.setRandomObject()
            if self.object_mode==OBJECT_MODE_WALL:
                self.nextWall()
        
    def update(self):        
        if self.mode==MODE_HEIGHT:
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_HEIGHT)
        elif self.mode==MODE_GRASS:
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_GRASS) 
        elif self.mode==MODE_TEXTURE:
            if self.keyMap['paint']:      
                self.painter.paint(BUFFER_ATR)         
                self.painter.paint(BUFFER_ATR2)
        elif self.mode==MODE_WALK:
            if self.keyMap['paint']:
                self.painter.paint(BUFFER_WALK)          
        elif self.mode==MODE_OBJECT:   
            if self.keyMap['rotate_l']:                
                self.heading_info['text']=self.objectPainter.adjustHpr(2.5,self.hpr_axis)
            if self.keyMap['rotate_r']:                    
                self.heading_info['text']=self.objectPainter.adjustHpr(-2.5,self.hpr_axis)
            if self.keyMap['scale_up']:
                self.objectPainter.adjustScale(0.01)
                self.size_info['text']='%.2f'%self.objectPainter.currentScale
            if self.keyMap['scale_down']:
                self.objectPainter.adjustScale(-0.01) 
                self.size_info['text']='%.2f'%self.objectPainter.currentScale
            if self.keyMap['alpha_up']:
                self.objectPainter.adjustZ(0.05)  
                self.color_info['text']='%.2f'%self.objectPainter.currentZ    
            if self.keyMap['alpha_down']:
                self.objectPainter.adjustZ(-0.05) 
                self.color_info['text']='%.2f'%self.objectPainter.currentZ 
            return 
            
        #if self.mode in (MODE_HEIGHT,MODE_TEXTURE,MODE_GRASS):    
        if self.keyMap['rotate_l']:
            self.painter.adjustBrushHeading(5)
            self.heading_info['text']=self.hpr_axis+'%.0f'%self.painter.brushes[0].getH()
        if self.keyMap['rotate_r']:
            self.painter.adjustBrushHeading(-5)    
            self.heading_info['text']=self.hpr_axis+'%.0f'%self.painter.brushes[0].getH()
        if self.keyMap['scale_up']:
            self.painter.adjustBrushSize(0.01)
            self.size_info['text']='%.2f'%self.painter.brushSize
        if self.keyMap['scale_down']:
            self.painter.adjustBrushSize(-0.01) 
            self.size_info['text']='%.2f'%self.painter.brushSize
        if self.keyMap['alpha_up']:
            if self.mode==MODE_HEIGHT and self.height_mode==HEIGHT_MODE_LEVEL:
                self.tempColor=min(1.0, max(0.0, self.tempColor+0.01)) 
                self.painter.brushes[BUFFER_HEIGHT].setColor(self.tempColor,self.tempColor,self.tempColor,1)
                self.color_info['text']='%.2f'%self.tempColor 
            else:    
                self.painter.adjustBrushAlpha(0.01)  
                self.color_info['text']='%.2f'%self.painter.brushAlpha                 
        if self.keyMap['alpha_down']:
            if self.mode==MODE_HEIGHT and  self.height_mode==HEIGHT_MODE_LEVEL:
                self.tempColor=min(1.0, max(0.0, self.tempColor-0.01)) 
                self.painter.brushes[BUFFER_HEIGHT].setColor(self.tempColor,self.tempColor,self.tempColor,1)
                self.color_info['text']='%.2f'%self.tempColor                
            else:                    
                self.painter.adjustBrushAlpha(-0.01) 
                self.color_info['text']='%.2f'%self.painter.brushAlpha             
        return 
        
    def perFrameUpdate(self, task):         
        time=globalClock.getFrameTime()            
        render.setShaderInput('time', time) 
        self.filters[4].setShaderInput('time', time)
        #self.interquad3.setShaderInput('time', time)
        #skydome
        pos=self.controler.cameraNode.getPos()
        self.skydome.setPos(pos[0], pos[1], 0)  
        #self.shadowNode.setPos(pos)        
        #water
        if self.waterNP.getZ()>0.0:   
            self.waterCamera.setMat(base.cam.getMat(render)*self.wPlane.getReflectionMat()) 
        if self.lastUpdateTime+0.03<time:
            self.update()        
            self.lastUpdateTime=time            
        if self.mode==MODE_OBJECT:
            self.objectPainter.update(self.snap.get())
        return task.cont    
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            wp=window.getProperties()       
            newsize=[wp.getXSize(),wp.getYSize()]
            if self.winsize!=newsize:            
                self.gui.updateBaseNodes()  
                self.filters[-1].setShaderInput("rt_w",float(base.win.getXSize()))
                self.filters[-1].setShaderInput("rt_h",float(base.win.getYSize()))                
                
    def setAtrMapColor(self, color1, color2, event=None):        
        self.painter.brushes[BUFFER_ATR].setColor(color1[0],color1[1],color1[2],self.painter.brushAlpha)
        self.painter.brushes[BUFFER_ATR2].setColor(color2[0],color2[1],color2[2],self.painter.brushAlpha)
 
app=Editor()
run()    
