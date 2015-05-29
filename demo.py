from panda3d.core import loadPrcFileData
loadPrcFileData('','textures-power-2 None')#needed for fxaa
#loadPrcFileData('','win-size 1280 720')
#loadPrcFileData('','notify-level spam')
loadPrcFileData('','win-size 1024 768')
#loadPrcFileData('','win-size 854 480')
loadPrcFileData('','show-frame-rate-meter  1')
loadPrcFileData('','framebuffer-srgb true')
loadPrcFileData('','texture-minfilter  mipmap')
loadPrcFileData('','texture-magfilter  linear')
loadPrcFileData('','default-texture-color-space sRGB')
loadPrcFileData('','pstats-gpu-timing true')
#loadPrcFileData('','show-buffers 1')
#loadPrcFileData('','threading-model Cull/Draw')
#loadPrcFileData('','undecorated 1')
#loadPrcFileData('','compressed-textures  1')
loadPrcFileData('','sync-video 0')
#loadPrcFileData('','frame-rate-meter-milliseconds 1')
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
wp.setTitle("Koparka - Game Like Demo")  
WindowProperties.setDefault(wp)

from panda3d.core import *
from direct.showbase import ShowBase
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from direct.interval.IntervalGlobal import *
from direct.actor.Actor import Actor
import json
import sys

from demo_util import loadLevel
from demo_util import setupLights
from demo_util import setupShadows
from demo_util import setupFilters
from demo_util import processProps
from demo_util import CameraControler
from demo_util import PointAndClick
from demo_util import Navigator


from lightmanager import LightManager


class Demo (DirectObject):
    def __init__(self, directory):
        #init ShowBase
        base = ShowBase.ShowBase()    
        base.setBackgroundColor(1,1,1) 
        #PStatClient.connect()
        self.lManager=LightManager()
        self.skyimg=PNMImage("data/sky_grad.png")
        
        #manager for post process filters (fxaa, soft shadows, dof)
        manager=FilterManager(base.win, base.cam)
        self.filters=setupFilters(manager, path, fxaa_only=False)
        
        #load a level
        self.level=loadLevel(path=path, from_dir=directory) 
        
        self.startpos=None
        
        #process properties
        functions={'coll_mask':self.setCollideMaskOn,
                   'hide':self.hideNode,
                   'startpos':self.setStratPos,
                   'alpha':self.setAlpha
                   }                   
        processProps(self.level, functions)        
        
        #lights and shadows    
        self.sun=setupLights(self.lManager)                
        self.shadows=setupShadows(buffer_size=1024)
        
        #camera controll
        base.disableMouse()  
        self.controler=CameraControler(shadows=self.shadows)                
        #point and click interface
        self.pointer=PointAndClick()
        self.accept('mouse1', self.onMouseClick)
        
        #player model
        #could be another class.... well next time
        self.pcNode=render.attachNewNode('pcNode')        
        self.actor=Actor("demo_models/male", {"attack1":"demo_models/male_attack1",
                                            "attack2":"demo_models/male_attack2",
                                            "walk":"demo_models/male_run",
                                            "block":"demo_models/male_block",
                                            "die":"demo_models/male_die",
                                            "strafe":"demo_models/male_strafe2",
                                            "hit":"demo_models/male_hit",
                                            "idle":"demo_models/male_ready2"}) 
        self.actor.setBlend(frameBlend = True) 
        self.actor.reparentTo(self.pcNode)
        self.actor.setScale(.1)
        self.actor.setShader(Shader.load(Shader.SLGLSL, path+"shaders/player_v.glsl",path+"shaders/player_f.glsl"))
        self.actor.loop("idle")         
        self.pcNode.setPos(self.startpos)
        #collisions
        self.coll_ray=self.pcNode.attachNewNode(CollisionNode('collRay'))        
        self.coll_ray.node().addSolid(CollisionRay(0, 0, 20, 0,0,-180))
        self.coll_ray.node().setIntoCollideMask(BitMask32.allOff()) 
        self.coll_ray.node().setFromCollideMask(BitMask32.bit(1)) 
        #self.coll_ray.show()
        self.traverser = CollisionTraverser() 
        self.queue = CollisionHandlerQueue()
        self.traverser.addCollider(self.coll_ray, self.queue)
        
        #pathfinding
        self.navi=Navigator(path+directory+'/navmesh.csv', self.pcNode, self.actor)
        self.target=render.attachNewNode('target')
        self.setTime(7.5)
        #tasks
        taskMgr.add(self.update, 'update_task', sort=45)
        self.clock=7.5        
        taskMgr.doMethodLater(1.0, self.clockTick,'clock_task', sort=10)
        self.accept( 'window-event', self.windowEventHandler) 
        
    def clockTick(self, task):
        self.clock+=0.05
        if self.clock>23.9:
            self.clock=0.0
        self.setTime(self.clock)                
        return task.again
        
    def blendPixels(self, p1, p2, blend):
        c1=[p1[0]/255.0,p1[1]/255.0,p1[2]/255.0, p1[3]/255.0] 
        c2=[p2[0]/255.0,p2[1]/255.0,p2[2]/255.0, p2[3]/255.0]         
        return Vec4( c1[0]*blend+c2[0]*(1.0-blend), c1[1]*blend+c2[1]*(1.0-blend), c1[2]*blend+c2[2]*(1.0-blend), c1[3]*blend+c2[3]*(1.0-blend))
        
    def setTime(self, time):
        sunpos=min(0.5, max(-0.5,(time-12.0)/14.0)) 
        render.setShaderInput('sunpos', sunpos)
        x1=int(time)
        x2=x1-1
        if x2<0:
            x2=0
        blend=time%1.0        
        
        p1=self.skyimg.getPixel(x1, 0)
        p2=self.skyimg.getPixel(x2, 0)
        sunColor=self.blendPixels(p1, p2, blend)
        sunColor[0]=sunColor[0]*1.5
        sunColor[1]=sunColor[1]*1.5
        sunColor[2]=sunColor[2]*1.5
        p1=self.skyimg.getPixel(x1, 1)
        p2=self.skyimg.getPixel(x2, 1)
        skyColor=self.blendPixels(p1, p2, blend)
        
        p1=self.skyimg.getPixel(x1, 2)
        p2=self.skyimg.getPixel(x2, 2)
        cloudColor=self.blendPixels(p1, p2, blend)
        
        p1=self.skyimg.getPixel(x1, 3)
        p2=self.skyimg.getPixel(x2, 3)
        fogColor=self.blendPixels(p1, p2, blend)        
        fogColor[3]=abs(sunpos)*0.01+0.001
        
        if time<6.0 or time>18.0:
            p=0.0            
        else:
            p=sunpos*-180.0
        LerpHprInterval(self.shadows['sunNode'], 1.0, (0,p,0)).start()
        #self.shadows['sunNode'].setP(p) 
        self.lManager.setLight(id=self.sun, pos=self.shadows['shadowCamera'].getPos(render), color=sunColor, radius=10000.0)
        self.level['skydome'].setShaderInput("sunColor",sunColor)        
        self.level['skydome'].setShaderInput("skyColor",skyColor)  
        self.level['skydome'].setShaderInput("cloudColor",cloudColor)
        render.setShaderInput("fog", fogColor)
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            self.filters[-1].setShaderInput("rt_w",float(base.win.getXSize()))
            self.filters[-1].setShaderInput("rt_h",float(base.win.getYSize()))
                
    def onMouseClick(self):
        pos=self.pointer.getPos()
        if pos:
            self.target.setPos(pos)
            self.navi.moveTo(self.target)
            
    def setAlpha(self, node, mode):
        pass
        #node.setTransparency(TransparencyAttrib.MAlpha)
        
    def setCollideMaskOn(self, node, mask):
        print "setting mask", mask, "on", node
        node.setCollideMask(BitMask32.bit(mask))
    
    def hideNode(self, node, doHide):
        if doHide==1:
            print "hidding node", node
            node.hide()    
    
    def setStratPos(self, node, not_used=None):
        self.startpos=node.getPos(render)
    
    def update(self, task):
        time=globalClock.getFrameTime()            
        render.setShaderInput('time', time)   
        self.controler.cameraNode.setPos(self.pcNode.getPos())
        #self.shadows['shadowNode'].setPos(self.pcNode.getPos())
        if len(self.filters)>1:
            self.filters[4].setShaderInput('time', time)  
        #water
        if self.level['water']['waterNP'].getZ()>0.0:   
            self.level['water']['waterCamera'].setMat(base.cam.getMat(render)*self.level['water']['wPlane'].getReflectionMat())
        #collision
        self.traverser.traverse(render)
        if self.queue.getNumEntries() > 0:        
            self.queue.sortEntries()                
            pos=self.queue.getEntry(0).getSurfacePoint(render)
            self.pcNode.setZ(pos[2]+0.2)
        return task.cont
        
app=Demo('save/default1')
base.run()      
