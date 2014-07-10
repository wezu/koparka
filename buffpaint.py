from panda3d.core import *

class BufferPainter ():
    def __init__(self, brushList, showBuff=False):        
        self.brushList=brushList        
        #make a pointer
        self.pointer = loader.loadModel("data/pointer")
        self.pointer.reparentTo(render)
        self.pointer.setLightOff()
        #the plane will bu used to see where the mouse pointer is
        self.plane = Plane(Vec3(0, 0, 0.1), Point3(0, 0, 0.1))
        
        self.buffers=[]
        self.brushes=[]
        self.textures=[]
        self.roots=[]
        self.cameras=[]
        self.paintPlanes=[]
        self.buffSize=[]
        self.brushSize=1.0
        self.brushAlpha=0.05
        self.hiddenBrushes=[]
        
        #view the buffers
        if showBuff:
            base.bufferViewer.toggleEnable()
            base.bufferViewer.setPosition("lrcorner")
            base.bufferViewer.setCardSize(0.2, 0.0) 
        
        
        taskMgr.add(self.__getMousePos, "_Editor__getMousePos")
   
    def write(self, id, file):
        p=PNMImage(self.buffSize[id], self.buffSize[id],4)              
        base.graphicsEngine.extractTextureData(self.textures[id],base.win.getGsg())
        self.textures[id].store(p) 
        p.removeAlpha()
        p.write(file)
   
    def addCanvas(self, size=512, default_tex='data/black.png', brush_shader=None, shader_inputs=None):
        id=str(len(self.buffers))
        self.buffSize.append(size)        
        self.roots.append(NodePath("bufferRender"+id))
        self.textures.append(Texture())
        self.buffers.append(base.win.makeTextureBuffer("canvas"+id, size, size,self.textures[-1]))
        self.buffers[-1].setSort(-100)
        #the camera for the buffer
        self.cameras.append(base.makeCamera(win=self.buffers[-1]))
        self.cameras[-1].reparentTo(self.roots[-1])          
        self.cameras[-1].setPos(256,256,100)                
        self.cameras[-1].setP(-90)                   
        lens = OrthographicLens()
        lens.setFilmSize(512, 512)  
        self.cameras[-1].node().setLens(lens)          
        #plane with the texture, a blank texture for now
        cm = CardMaker("plane")
        cm.setFrame(0, 512, 0, 512)        
        self.paintPlanes.append(self.roots[-1].attachNewNode(cm.generate()))
        self.paintPlanes[-1].lookAt(0, 0, -1)
        self.paintPlanes[-1].setTexture(loader.loadTexture(default_tex))
        self.paintPlanes[-1].setLightOff()
        self.paintPlanes[-1].setZ(-1)   
        #the brush 
        cm.setFrame(-16, 16, -16, 16)                
        self.brushes.append(self.roots[-1].attachNewNode(cm.generate()))
        self.brushes[-1].lookAt(0, 0, -1)
        self.brushes[-1].setTexture(loader.loadTexture(self.brushList[0]))
        self.brushes[-1].setTransparency(TransparencyAttrib.MAlpha)        
        self.brushes[-1].setLightOff()
        self.brushes[-1].setColor(1, 1, 1, 0.05) 
        if brush_shader:           
            self.brushes[-1].setShader(brush_shader)
            for input in shader_inputs:
                self.brushes[-1].setShaderInput(input, shader_inputs[input])
            
    def paint(self, id):
        #print "paint"
        p=PNMImage(self.buffSize[id], self.buffSize[id],4)              
        base.graphicsEngine.extractTextureData(self.textures[id],base.win.getGsg())
        self.textures[id].store(p) 
        myTexture=Texture()
        myTexture.load(p)        
        self.paintPlanes[id].setTexture(myTexture, 1)
    
    def adjustBrushAlpha(self, alpha):
        for brush in self.brushes:
            color=brush.getColor()
            new_alpha=min(1.0, max(0.0, self.brushAlpha+alpha))           
            self.brushAlpha=new_alpha                
            brush.setColor(color[0],color[1],color[2], new_alpha)
    
    def hideBrushes(self):          
        for brush in self.brushes:            
            brush.hide()
            
    def setBrushColor(self, color):
        for brush in self.brushes:
            alpha=brush.getColor()
            brush.setColor(color[0],color[1],color[2], alpha[3])
            
    def setBrushTex(self, id):
        for brush in self.brushes:            
            brush.setTexture(loader.loadTexture(self.brushList[id]))
            
    def adjustBrushHeading(self, heading):
        for brush in self.brushes:            
            brush.setH(brush.getH()+heading)
            
    def adjustBrushSize(self, size):
        for brush in self.brushes:  
            new_size=min(5.00, max(0.11, self.brushSize+size))
            #make 'sticky' around 1.0
            #if new_size> 0.99 and new_size< 1.01:
            #    new_size=1            
            self.brushSize=new_size            
            brush.setScale(new_size)
            brush.setShaderInput('brushSize', new_size)
    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint),render.getRelativePoint(camera, farPoint)):                
                self.pointer.setX(min(512.0, max(0.0, pos3d[0]))) 
                self.pointer.setY(min(512.0, max(0.0, pos3d[1]))) 
                for brush in self.brushes:
                    brush.setPos(self.pointer.getPos())
        return task.again          