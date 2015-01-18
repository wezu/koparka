from panda3d.core import loadPrcFileData
loadPrcFileData('','textures-power-2 None')#needed for fxaa
loadPrcFileData('','win-size 1024 768')
loadPrcFileData('','show-frame-rate-meter  1')
loadPrcFileData('','threading-model Cull/Draw')
loadPrcFileData('','compressed-textures  1')
#loadPrcFileData('','sync-video 1')
#loadPrcFileData('','win-size 1280 720')
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
import direct.directbase.DirectStart
from direct.showbase.DirectObject import DirectObject
from direct.filter.FilterManager import FilterManager
from direct.actor.Actor import Actor
import json
import sys

class Demo (DirectObject):
    def __init__(self, directory):
        base.setBackgroundColor(0.77, 0.77, 0.77)  
        #files needed to be read
        objects=directory+'/objects.json'
        collision=directory+'/collision'
        detail_map1=directory+'/detail0.png'
        detail_map2=directory+'/detail1.png'
        grass_map=directory+'/grass.png'
        height_map=directory+'/heightmap.png'
        
        #fxaa, just the manager, the effect is created when the window is opened/resized
        self.fxaaManager=FilterManager(base.win, base.cam)
                       
        #some needed variables...
        self.actors=[]                       
        self.winsize=[0,0]        
        #quadtree structure - TODO:could this be loaded from a bam file?
        nodeA=render.attachNewNode('quadA')
        nodeA.setPos(render,128,128,0)
        nodeB=render.attachNewNode('quadB')
        nodeB.setPos(render,384,128,0)
        nodeC=render.attachNewNode('quadC')
        nodeC.setPos(render,128,384,0)
        nodeD=render.attachNewNode('quadD')
        nodeD.setPos(render,384,384,0)        
        nodeA1=nodeA.attachNewNode('quadA1')
        nodeA1.setPos(render,64, 64, 0)
        nodeA2=nodeA.attachNewNode('quadA2')
        nodeA2.setPos(render,192, 64, 0)
        nodeA3=nodeA.attachNewNode('quadA3')
        nodeA3.setPos(render,64, 192, 0)
        nodeA4=nodeA.attachNewNode('quadA4')
        nodeA4.setPos(render,192, 192, 0)        
        nodeB1=nodeB.attachNewNode('quadB1')
        nodeB1.setPos(render,320, 64, 0)
        nodeB2=nodeB.attachNewNode('quadB2')
        nodeB2.setPos(render,448, 64, 0)
        nodeB3=nodeB.attachNewNode('quadB3')
        nodeB3.setPos(render,320, 192, 0)
        nodeB4=nodeB.attachNewNode('quadB4')
        nodeB4.setPos(render,448, 192, 0)        
        nodeC1=nodeC.attachNewNode('quadC1')
        nodeC1.setPos(render,64, 320, 0)
        nodeC2=nodeC.attachNewNode('quadC2')
        nodeC2.setPos(render,192, 320, 0)
        nodeC3=nodeC.attachNewNode('quadC3')
        nodeC3.setPos(render,64, 448, 0)
        nodeC4=nodeC.attachNewNode('quadC4')
        nodeC4.setPos(render,192, 448, 0)        
        nodeD1=nodeD.attachNewNode('quadD1')
        nodeD1.setPos(render,320, 320, 0)
        nodeD2=nodeD.attachNewNode('quadD2')
        nodeD2.setPos(render,448, 320, 0)
        nodeD3=nodeD.attachNewNode('quadD3')
        nodeD3.setPos(render,320, 448, 0)
        nodeD4=nodeD.attachNewNode('quadD4')
        nodeD4.setPos(render,448, 448, 0)
        self.quadtree=[nodeA1,nodeA2,nodeA3,nodeA4,
                       nodeB1,nodeB2,nodeB3,nodeB4,
                       nodeC1,nodeC2,nodeC3,nodeC4,
                       nodeD1,nodeD2,nodeD3,nodeD4]
        
        #setup terrain part1
        self.mesh=loader.loadModel('data/mesh80k.bam')             
        self.mesh.reparentTo(render)
        #collision mesh
        self.collision=loader.loadModel(collision)             
        self.collision.reparentTo(render)
        
        #load the objects and textures from a file
        self.LoadScene(objects, self.quadtree, self.actors, self.mesh, flatten=True)
        
        #setup terrain part2
        self.mesh.setShader(Shader.load(Shader.SLGLSL, "shaders/demo_terrain_v.glsl", "shaders/demo_terrain_f.glsl"))        
        self.mesh.setShaderInput("height", loader.loadTexture(height_map)) 
        self.mesh.setShaderInput("atr1",  loader.loadTexture(detail_map1))
        self.mesh.setShaderInput("atr2",  loader.loadTexture(detail_map2))
        self.mesh.setTransparency(TransparencyAttrib.MNone)
        self.mesh.node().setBounds(OmniBoundingVolume())
        self.mesh.node().setFinal(1)
        self.mesh.setBin("background", 11)
        #grass
        self.grass=render.attachNewNode('grass')
        self.CreateGrassTile(Vec2(0,0), (0,0,0), self.grass, Vec3(256,256,0), grass_map, height_map)
        self.CreateGrassTile(Vec2(0,0.5), (0, 256, 0), self.grass, Vec3(256,0,0), grass_map, height_map)
        self.CreateGrassTile(Vec2(0.5,0), (256, 0, 0), self.grass, Vec3(0,256,0), grass_map, height_map)
        self.CreateGrassTile(Vec2(0.5,0.5), (256, 256, 0), self.grass, Vec3(0,0,0), grass_map, height_map)  
        self.grass.setBin("background", 11)       
        #light
        self.dlight = DirectionalLight('dlight') 
        self.dlight.setColor(VBase4(1, 1, 0.9, 1))     
        self.mainLight = render.attachNewNode(self.dlight)
        self.mainLight.setP(-60)       
        self.mainLight.setH(90)        
        render.setLight(self.mainLight)        
        #ambient
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .35, 1))
        self.Ambient=render.attachNewNode(ambientLight)
        render.setLight(self.Ambient)        
        self.mesh.setLightOff(self.Ambient)
        render.setShaderInput("dlight0", self.mainLight) #needed for the default.cg shader        
        render.setShaderInput("ambient", Vec4(.2, .2, .3, 1))
        
        
        #fog
        render.setShaderInput("fog",  Vec4(0.8, 0.8, 0.8, 0.007))
        
        #resize event (resets fxaa)
        self.accept( 'window-event', self.windowEventHandler)
        
        #the task updates a 'time' shader input for the grass shader
        #in a future p3d version some sort of time imput should be provided by the c/c++ side(?)
        taskMgr.add(self.perFrameUpdate, 'perFrameUpdate_task')  
        
        #####################
        #Roaming-Ralph stuff
        #####################
        self.keyMap = {"left":0, "right":0, "forward":0, "cam-left":0, "cam-right":0}
        # Create the main character, Ralph
        ralphStartPos = (256,256,0)
        self.ralph = Actor("demo_models/ralph",
                                 {"run":"demo_models/ralph-run",
                                  "walk":"demo_models/ralph-walk"})
        self.ralph.reparentTo(render)
        self.ralph.setPos(ralphStartPos)
        self.ralph.setScale(0.5)
        
        # Create a floater object.         
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation
        self.accept("escape", sys.exit)
        self.accept("arrow_left", self.setKey, ["left",1])
        self.accept("arrow_right", self.setKey, ["right",1])
        self.accept("arrow_up", self.setKey, ["forward",1])
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_left-up", self.setKey, ["left",0])
        self.accept("arrow_right-up", self.setKey, ["right",0])
        self.accept("arrow_up-up", self.setKey, ["forward",0])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera        
        base.disableMouse()
        base.camera.setPos(self.ralph.getX(),self.ralph.getY()+30, 50)
        
        # collisions...
        mask=BitMask32.bit(0)
        mask.setBit(2)
        self.cTrav = CollisionTraverser()
        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(mask)
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.ralphGroundColNp = self.ralph.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.ralphGroundColNp, self.ralphGroundHandler)

        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
        
    def perFrameUpdate(self, task):         
        time=globalClock.getFrameTime()    
        render.setShaderInput('time', time)         
        return task.cont 
        
    def windowEventHandler( self, window=None ):    
        if window is not None: # window is none if panda3d is not started
            wp=window.getProperties()       
            newsize=[wp.getXSize(),wp.getYSize()]
            if self.winsize!=newsize:    
                #resizing the window breaks the filter manager, so I just make a new one
                self.fxaaManager.cleanup()
                self.fxaaManager=self.makeFXAADOF(self.fxaaManager)
                self.winsize=newsize
                
    def CreateGrassTile(self, uv_offset, pos, parent, fogcenter, grass_map, height_map, count=256):
        grass=loader.loadModel("data/grass_model")
        grass.reparentTo(parent)
        grass.setInstanceCount(count) 
        grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
        grass.node().setFinal(1)
        grass.setShader(Shader.load(Shader.SLGLSL, "shaders/grass_v.glsl", "shaders/grass_f.glsl"))
        grass.setShaderInput('height', loader.loadTexture(height_map)) 
        grass.setShaderInput('grass', loader.loadTexture(grass_map))
        grass.setShaderInput('uv_offset', uv_offset)   
        grass.setShaderInput('fogcenter', fogcenter)
        grass.setPos(pos)
        #grass.setScale(1,1,0.2)
        #grass.setBin("fixed", 40)
        #grass.setDepthTest(False)
        #grass.setDepthWrite(False)
        return grass
        
    def LoadScene(self, file, quad_tree, actors, terrain, flatten=False):
        json_data=None
        with open(file) as f:  
            json_data=json.load(f)
        print 'Loading'    
        for object in json_data:
            print ".",
            if 'textures' in object:
                i=0
                for tex in object['textures']:
                    diff=loader.loadTexture(tex)
                    diff.setAnisotropicDegree(2)
                    #normal texture should have the same name but should be in '/normal/' directory
                    normal_tex=tex.replace('/diffuse/','/normal/')
                    norm=loader.loadTexture(normal_tex)
                    norm.setAnisotropicDegree(2)
                    terrain.setTexture(terrain.findTextureStage('tex{0}'.format(i+1)), diff, 1)                    
                    terrain.setTexture(terrain.findTextureStage('tex{0}n'.format(i+1)), norm, 1) 
                    i+=1
                continue    
            elif 'model' in object:
                model=loader.loadModel(object['model'])
                model.setPythonTag('model_file', object['model'])
            elif 'actor' in object:
                model=Actor(object['actor'], object['actor_anims'])
                collision=loader.loadModel(object['actor_collision'])            
                collision.reparentTo(model)
                actors.append(model)
                model.setPythonTag('actor_files', [object['actor'],object['actor_anims'],object['actor_collision']])            
                #default anim
                if 'default' in object['actor_anims']:
                    model.loop('default')
                elif 'idle' in object['actor_anims']:
                    model.loop('idle')
                else: #some random anim
                    model.loop(object['actor_anims'].items()[0])
            model.reparentTo(quad_tree[object['parent_index']])
            model.setCollideMask(BitMask32.allOff())        
            model.setShader(loader.loadShader("shaders/default.cg")) 
            model.find('**/collision').setCollideMask(BitMask32.bit(2))        
            model.find('**/collision').setPythonTag('object', model)
            
            model.setPythonTag('props', object['props'])
            model.setHpr(render,object['rotation_h'],object['rotation_p'],object['rotation_r'])
            model.setPos(render,object['position_x'],object['position_y'],object['position_z'])
            model.setScale(object['scale'])
            
    def makeFXAADOF(self, manager=None, span_max=4.0, reduce_mul=2.0, subpixel_shift=4.0):
        wp=base.win.getProperties()
        winX = wp.getXSize()
        winY = wp.getYSize()
        tex = Texture()
        fog= Texture()
        if manager==None:
            manager = FilterManager(base.win, base.cam)
        quad = manager.renderSceneInto(colortex=tex, auxtex=fog)
        quad.setShader(Shader.load(Shader.SLGLSL, "shaders/fxaa_v.glsl", "shaders/fxaadof_f.glsl"))
        quad.setShaderInput("tex0", tex)
        quad.setShaderInput("rt_w",winX)
        quad.setShaderInput("rt_h",winY)
        quad.setShaderInput("FXAA_SPAN_MAX" , float(span_max))
        quad.setShaderInput("FXAA_REDUCE_MUL", float(1.0/reduce_mul))
        quad.setShaderInput("FXAA_SUBPIX_SHIFT", float(1.0/subpixel_shift)) 
        quad.setShaderInput("fog", fog)
        return manager  
        
    #RR 
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value    

    # Accepts arrow keys to move either the player or the menu cursor,
    # Also deals with grid checking and collision detection
    def move(self, task):

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        base.camera.lookAt(self.ralph)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save ralph's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = self.ralph.getPos()

        # If a move-key is pressed, move ralph in the specified direction.

        if (self.keyMap["left"]!=0):
            self.ralph.setH(self.ralph.getH() + 300 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.ralph.setH(self.ralph.getH() - 300 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.ralph.setY(self.ralph, -25 * globalClock.getDt())

        # If ralph is moving, loop the run animation.
        # If he is standing still, stop the animation.

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0):
            if self.isMoving is False:
                self.ralph.loop("run")
                self.isMoving = True
        else:
            if self.isMoving:
                self.ralph.stop()
                self.ralph.pose("walk",5)
                self.isMoving = False

        # If the camera is too far from ralph, move it closer.
        # If the camera is too close to ralph, move it farther.

        camvec = self.ralph.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 40.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-40))
            camdist = 40.0
        if (camdist < 10.0):
            base.camera.setPos(base.camera.getPos() - camvec*(10-camdist))
            camdist = 10.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        # Adjust ralph's Z coordinate.  If ralph's ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))                                    
        if (len(entries)>0) and (entries[0].getIntoNode().getName() != "collision"):
            self.ralph.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.ralph.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above ralph, whichever is greater.
        
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() != "collision"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+10.0)
        if (base.camera.getZ() < self.ralph.getZ() + 11.0):
            base.camera.setZ(self.ralph.getZ() + 11.0)
            
        # The camera should look in ralph's direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above ralph's head.
        
        self.floater.setPos(self.ralph.getPos())
        self.floater.setZ(self.ralph.getZ() + 2.0)
        base.camera.lookAt(self.floater)

        return task.cont
        
app=Demo('save/default1')
run()      