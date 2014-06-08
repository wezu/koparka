from panda3d.core import *
from direct.gui.DirectGui import *
from direct.interval.IntervalGlobal import *

def _pos2d(x,y):
    return Point3(x,0,-y)
    
def _rec2d(width, height):
    return (-width, 0, 0, height)
    
def _resetPivot(frame):
    size=frame['frameSize']    
    frame.setPos(-size[0], 0, -size[3])        
    frame.flattenLight()


class GuiHelper():
    def __init__(self):
        self.elements=[]
        
        self.font = DGG.getDefaultFont()
        self.font.setPixelsPerUnit(16)
        
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
    
    def addToolbar(self, parent, size, icon_size=32, x_offset=0, y_offset=0):         
        frame=DirectFrame( frameSize=_rec2d(size,128),
                        frameColor=(1,0,0, 0),
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setX(frame, x_offset)
        frame.setZ(frame, -y_offset)
        data={'size':size, 'icon_size':icon_size, 'frame':frame, 'buttons':[]}
        id=len(self.elements)
        self.elements.append(data)
        return id
        
    def addButton(self, toolbar, icon, command, arg=[]):
        size=self.elements[toolbar]['icon_size']
        parent=self.elements[toolbar]['frame']
        max_x=self.elements[toolbar]['size']
        x=len(self.elements[toolbar]['buttons'])*size
        y=0
        while x>=max_x:
            y+=size
            x-=max_x
        
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
        
    def addInfoIcon(self, toolbar, icon, text):        
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
        return frame
        
    def addComposer(self, parent, update_command, x_offset=-160, y_offset=-224):
        frame=DirectFrame( frameSize=_rec2d(160,224),
                        frameColor=(1,0,0, 0),
                        parent=parent)
        _resetPivot(frame)
        frame.setTransparency(TransparencyAttrib.MDual)
        frame.setX(frame, x_offset)
        frame.setZ(frame, -y_offset)
        
        preview=DirectFrame( frameSize=_rec2d(128,128),
                        frameColor=(1,1,1, 1),                                               
                        frameTexture='data/detail.png',
                        parent=frame)
        _resetPivot(preview)        
        preview.setPos(_pos2d(16, 96))
        
        r_slider=DirectSlider(range=(0,1),
                              value=1,
                              pageSize=10,      
                              thumb_relief=DGG.FLAT,
                              scale=64,
                              command=update_command,
                              thumb_frameSize=(0.1, -0.1, -0.2, 0.2),
                              parent=frame)
        r_slider.setPos(_pos2d(80, 16))
        r_slider.setColor(1,0,0,1)
        
        g_slider=DirectSlider(range=(0,1),
                              value=0,
                              pageSize=10,      
                              thumb_relief=DGG.FLAT,
                              scale=64,
                              command=update_command,
                              thumb_frameSize=(0.1, -0.1, -0.2, 0.2),
                              parent=frame)
        g_slider.setPos(_pos2d(80, 48))
        g_slider.setColor(0,1,0,1)
        
        b_slider=DirectSlider(range=(0,1),
                              value=0,
                              pageSize=10,      
                              thumb_relief=DGG.FLAT,
                              scale=64,
                              thumb_frameSize=(0.1, -0.1, -0.2, 0.2),
                              command=update_command,
                              parent=frame)
        b_slider.setPos(_pos2d(80, 80))
        b_slider.setColor(0,0,1,1)
        
        preview_geom=preview.stateNodePath[0] 
        preview_geom.setShader(loader.loadShader('shaders/composer_view.cg'))
        preview_geom.setShaderInput('mix', Vec4(r_slider['value'],g_slider['value'],b_slider['value'],1.0 ))
        
        data={'frame':frame, 'geom':preview_geom, 'r_slider':r_slider, 'g_slider':g_slider, 'b_slider':b_slider}
        id=len(self.elements)
        self.elements.append(data)
        return id
        