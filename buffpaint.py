from panda3d.core import *

class BufferPainter ():
    def __init__(self, brushList, showBuff=False):    
        self.use_gl_select=False   
        self.pixel=VBase4() #used by gl picking
        self.brushList=brushList        
        #make a pointer
        self.pointer = loader.loadModel("data/pointer")
        self.pointer.reparentTo(render)
        self.pointer.setLightOff()
        self.pointer.hide(BitMask32.bit(1))
        self.pointer.hide(BitMask32.bit(2))
        self.pointer.setShader(Shader.load(Shader.SLGLSL, "shaders/editor_v.glsl", "shaders/editor_f.glsl"))
        #the plane will bu used to see where the mouse pointer is
        self.z=25.5
        self.pointer.setZ(self.z)
        self.plane = Plane(Vec3(0, 0, 1), Point3(0, 0, self.z))        
        
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
   
    def setupGlSelect(self, height, scale=100.0):
        self.use_gl_select=True
        self.pointer.setZ(0.0)
        self.pickingTex = Texture("picking_texture")
        props = FrameBufferProperties()
        props.setRgbaBits(16, 16, 0, 0)
        props.setSrgbColor(False)
        self.pickingBuffer = base.win.makeTextureBuffer("picking_buffer",
                                                  1, 1,
                                                  self.pickingTex,
                                                  to_ram=True,
                                                  fbp=props)

        self.pickingBuffer.setClearColor(VBase4())
        self.pickingBuffer.setSort(10)
        self.pickingPeeker = self.pickingTex.peek()
        self.pickingCam = base.makeCamera(self.pickingBuffer) 
        node = self.pickingCam.node()  
        lens = node.getLens()            
        lens.setNear(32.0)
        lens.setFar(2**16)
        lens.setFov(2.0)
        cull_bounds = lens.makeBounds()
        lens.setFov(0.4)
        node.setCullBounds(cull_bounds)
        #MASK_TERRAIN_ONLY=BitMask32.bit(3)
        node.setCameraMask(BitMask32.bit(3))
        #node.showFrustum()
        
        state_np = NodePath("picking_state")
        #shaderAtt = ShaderAttrib.make()
        #shaderAtt= shaderAtt.setShader(Shader.load(Shader.SLGLSL, "shaders/pick_v.glsl","shaders/pick_f.glsl"),1)
        state_np.setShader(Shader.load(Shader.SLGLSL, "shaders/pick_v.glsl","shaders/pick_f.glsl"),1)
        state_np.setShaderInput("height", height)
        state_np.setShaderInput("z_scale", scale)
        #state_np.setAttrib(shaderAtt, 1)        
        node.setInitialState(state_np.getState())
        
    def write(self, id, file, returnPNMImage=False):
        p=PNMImage(self.buffSize[id], self.buffSize[id],4)              
        base.graphicsEngine.extractTextureData(self.textures[id],base.win.getGsg())
        self.textures[id].store(p) 
        p.removeAlpha()
        p.write(file)
        if returnPNMImage:
            return p
        
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
        self.brushes[-1].setColorOff()
        self.brushes[-1].setColor(1, 1, 1, 0.05) 
        self.brushes[-1].setShaderInput("brush_color",self.brushes[-1].getColor())
        if brush_shader:           
            self.brushes[-1].setShader(brush_shader)
            self.brushes[-1].setShaderInput('map', self.textures[-1])
            if shader_inputs:
                for input in shader_inputs:
                    self.brushes[-1].setShaderInput(input, shader_inputs[input])
            
    def paint(self, id):
        p=PNMImage(self.buffSize[id], self.buffSize[id],4)              
        base.graphicsEngine.extractTextureData(self.textures[id],base.win.getGsg())
        self.textures[id].store(p) 
        myTexture=Texture()
        myTexture.load(p)        
        self.paintPlanes[id].setTexture(myTexture, 1)
        self.brushes[id].setShaderInput('map', myTexture)
        
    def setBrushIDColor(self, id, color, keep_alpha=True):
        brush=self.brushes[id]
        if keep_alpha:
            alpha=brush.getColor()[3]
        else:
            alpha=color[3]    
        brush.setColor(color[0],color[1],color[2], alpha)
        brush.setShaderInput("brush_color",brush.getColor())
    
    def setBrushIDAlpha(self, id, new_alpha):
        brush=self.brushes[id]
        color=brush.getColor()              
        brush.setColor(color[0],color[1],color[2], new_alpha)
        brush.setShaderInput("brush_color",brush.getColor())
            
    def setBrushAlpha(self,  slider=None, alpha=None):
        if slider:
            alpha=slider['value']
        new_alpha=min(1.0, max(0.0, alpha))           
        self.brushAlpha=new_alpha                
        for brush in self.brushes:
            color=brush.getColor()              
            brush.setColor(color[0],color[1],color[2], new_alpha)
            
    def adjustBrushAlpha(self, alpha):                
        new_alpha=min(1.0, max(0.0, self.brushAlpha+alpha))           
        self.brushAlpha=new_alpha                
        for brush in self.brushes:
            color=brush.getColor()              
            brush.setColor(color[0],color[1],color[2], new_alpha)
            brush.setShaderInput("brush_color",brush.getColor())
    
    def hideBrushes(self):          
        for brush in self.brushes:            
            brush.hide()
            
    def setBrushColor(self, color):
        for brush in self.brushes:
            alpha=brush.getColor()
            brush.setColor(color[0],color[1],color[2], alpha[3])
            brush.setShaderInput("brush_color",brush.getColor())
            
    def setBrushTex(self, id):
        for brush in self.brushes:            
            brush.setTexture(loader.loadTexture(self.brushList[id]))
            
    def setBrushHeading(self, slider=None, heading=None):
        if slider:
            heading=int(slider['value'])
        for brush in self.brushes:        
            new_heading =heading%360.0     
            brush.setH(new_heading)            
            
    def adjustBrushHeading(self, heading):               
        for brush in self.brushes:        
            new_heading =(brush.getH()+heading)%360.0     
            brush.setH(new_heading)
            
    def setBrushSize(self, slider=None, size=None):
        if slider:
            size=slider['value']
        new_size=min(10.00, max(0.01, size))                        
        self.brushSize=new_size 
        for brush in self.brushes:                         
            brush.setScale(new_size)
                    
    def adjustBrushSize(self, size):
        new_size=min(10.00, max(0.01, self.brushSize+size))                        
        self.brushSize=new_size 
        for brush in self.brushes:                         
            brush.setScale(new_size)
            
    def __getMousePos(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            nearPoint = Point3()
            farPoint = Point3()
            base.camLens.extrude(mpos, nearPoint, farPoint)
            if self.use_gl_select:
                self.pickingCam.lookAt(farPoint)

                if not self.pickingPeeker:
                    self.pickingPeeker = self.pickingTex.peek()
                else:    
                    self.pickingPeeker.lookup(self.pixel, .5, .5)                
                    self.pointer.setX(min(512.0, max(0.0, self.pixel[0]*512.0))) 
                    self.pointer.setY(min(512.0, max(0.0, self.pixel[1]*512.0)))                
                    for brush in self.brushes:
                        brush.setPos(self.pointer.getPos())
                
            else:    
                if self.plane.intersectsLine(pos3d, render.getRelativePoint(camera, nearPoint),render.getRelativePoint(camera, farPoint)):                
                    self.pointer.setX(min(512.0, max(0.0, pos3d[0]))) 
                    self.pointer.setY(min(512.0, max(0.0, pos3d[1])))                
                    for brush in self.brushes:
                        brush.setPos(self.pointer.getPos())
        return task.again          
