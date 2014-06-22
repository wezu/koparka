from panda3d.core import *

class ObjectPainter():
    def __init__(self): 
        #collision detection setup
        self.traverser = CollisionTraverser()   
        #self.traverser.showCollisions(render)
        self.queue     = CollisionHandlerQueue()         
        self.pickerNode = CollisionNode('mouseRay')    
        self.pickerNP = camera.attachNewNode(self.pickerNode) 
        #print "mask:", self.pickerNP.getCollideMask()    
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()               
        self.pickerNode.addSolid(self.pickerRay)      
        self.traverser.addCollider(self.pickerNP, self.queue)
                
        self.currentObject=None
        self.hitNode=None
        self.currentHPR=[0,0,0]
        self.currentZ=0.0
        self.currentScale=1.0
        
        #quadtree structure
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
                       
    def adjustHpr(self, amount, axis):
        if axis=='H: ':
            i=0
        elif axis=='P: ':
            i=1
        elif axis=='R: ':
            i=2         
        new=self.currentHPR[i]+amount
        if new >360.0:
            new-=360.0
        if new <-0.0:
            new+=360.0    
        self.currentHPR[i]=new 
        if self.currentObject!=None:
            self.currentObject.setHpr(self.currentHPR[0],self.currentHPR[1],self.currentHPR[2])
        return axis+'%.0f'%self.currentHPR[i]
        
    def adjustScale(self, amount):
        new=min(10.0, max(0.1, self.currentScale+amount)) 
        self.currentScale=new
        if self.currentObject!=None:
            self.currentObject.setScale(self.currentScale)
            
    def adjustZ(self, amount):
        new=min(10.0, max(-10.0, self.currentZ+amount)) 
        self.currentZ=new
        if self.currentObject!=None:
            self.currentObject.setZ(self.currentZ)
            
    def stop(self):
        if self.currentObject!=None:
            self.currentObject.removeNode()
            self.currentObject=None
            
    def loadModel(self, model):
        if self.currentObject!=None:
            self.currentObject.removeNode()
        self.currentObject=loader.loadModel(model)
        self.currentObject.reparentTo(render)
        self.currentObject.setCollideMask(BitMask32.allOff())
        self.currentObject.setShaderAuto()
        self.currentObject.find('**/collision').setCollideMask(BitMask32.bit(2))        
        self.currentObject.find('**/collision').setPythonTag('object', self.currentObject)
        self.currentObject.setPythonTag('model_file', model)
        self.currentObject.setPythonTag('props', '')
        self.currentObject.setHpr(self.currentHPR[0],self.currentHPR[1],self.currentHPR[2])
        self.currentObject.setZ(self.currentZ)
        self.currentObject.setScale(self.currentScale)
        
    def drop(self):
        if self.currentObject:
            best_node=None
            best_distance=725.0
            for node in self.quadtree:
                distance=node.getDistance(self.currentObject)
                if distance < best_distance:
                    best_distance=distance
                    best_node=node
            self.currentObject.wrtReparentTo(best_node)  
            self.currentObject=None
            
    def pickup(self): 
        if self.currentObject:
            return False
        if self.hitNode:
            if self.hitNode.hasPythonTag('object'):                
                self.currentObject=self.hitNode.getPythonTag('object')
                self.currentObject.wrtReparentTo(render) 
                self.currentHPR=[self.currentObject.getH(render), self.currentObject.getP(render), self.currentObject.getR(render)]
                self.currentZ=self.currentObject.getZ(render)
                self.currentScales=self.currentObject.getScale()[0]
                return True  
                
    def update(self):
        if base.mouseWatcherNode.hasMouse():      
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())            
            self.traverser.traverse(render)
            if self.queue.getNumEntries() > 0:        
                self.queue.sortEntries()                
                hit_pos=self.queue.getEntry(0).getSurfacePoint(render)
                self.hitNode=self.queue.getEntry(0).getIntoNodePath()
                if self.currentObject:                
                    self.currentObject.setPos(hit_pos)
                    self.currentObject.setZ(hit_pos[2]+self.currentZ)