from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *

class CameraControler (DirectObject):
    def __init__(self, pos=(256,256,0), offset=(0, -120, 120), speed=50.0, angle=-45):
    
        self.cameraNode  = render.attachNewNode("cameraNode")
        self.cameraNode.setPos(pos)
        self.cameraGimbal  = self.cameraNode.attachNewNode("cameraGimbal")
        base.camera.setPos(pos)
        base.camera.setX(base.camera, offset[0])
        base.camera.setY(base.camera, offset[1])
        base.camera.setZ(offset[2])
        base.camera.setP(angle)
        base.camera.wrtReparentTo(self.cameraGimbal)
        
        self.keyMap = {'up': False,
                       'down': False,
                       'left': False,
                       'right': False,
                       'rotate': False,
                       'pan': False}
                       
        self.accept('w', self.keyMap.__setitem__, ['up', True])                
        self.accept('w-up', self.keyMap.__setitem__, ['up', False])
        self.accept('s', self.keyMap.__setitem__, ['down', True])                
        self.accept('s-up', self.keyMap.__setitem__, ['down', False])
        self.accept('a', self.keyMap.__setitem__, ['right', True])                
        self.accept('a-up', self.keyMap.__setitem__, ['right', False])
        self.accept('d', self.keyMap.__setitem__, ['left', True])                
        self.accept('d-up', self.keyMap.__setitem__, ['left', False])
        self.accept('mouse2', self.keyMap.__setitem__, ['rotate', True])                
        self.accept('mouse2-up', self.keyMap.__setitem__, ['rotate', False])
        self.accept('mouse3', self.keyMap.__setitem__, ['pan', True])                
        self.accept('mouse3-up', self.keyMap.__setitem__, ['pan', False])
        self.accept('alt', self.keyMap.__setitem__, ['pan', True])                
        self.accept('alt-up', self.keyMap.__setitem__, ['pan', False])
        self.accept('control', self.keyMap.__setitem__, ['rotate', True])                
        self.accept('control-up', self.keyMap.__setitem__, ['rotate', False])
        
        self.mouseSpeed=speed #default 50.0
        self.accept('wheel_up', self.zoom_control,[0.1])
        self.accept('wheel_down',self.zoom_control,[-0.1])
        self.accept('=', self.zoom_control,[0.1])
        self.accept('-',self.zoom_control,[-0.1])
        
        self.skip=False
        
        taskMgr.add(self.update, "camcon_update", sort=-1)
        
    def zoom(self, t):
        base.camera.setY(base.camera, t)
    
    def zoom_control(self, amount):
        LerpFunc(self.zoom,fromData=0,toData=amount, duration=.2, blendType='easeOut').start()
        
    def update(self, task):        
        if base.mouseWatcherNode.hasMouse():
            deltaX = base.mouseWatcherNode.getMouseX()  # mouse distance from the center
            deltaY = base.mouseWatcherNode.getMouseY()
            if self.keyMap['pan']:
                base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
                if not self.skip:
                    self.cameraNode.setX(self.cameraNode, 2.0*deltaX*self.mouseSpeed)
                    self.cameraNode.setY(self.cameraNode, 2.0*deltaY*self.mouseSpeed)
                self.skip=False
            elif self.keyMap['rotate']:        
                base.win.movePointer(0, base.win.getXSize()/2, base.win.getYSize()/2)
                if not self.skip:
                    self.cameraNode.setH(self.cameraNode.getH()- deltaX*self.mouseSpeed)
                    self.cameraGimbal.setP(self.cameraGimbal.getP()+ deltaY*self.mouseSpeed)
                self.skip=False
            else:
                self.skip=True            
        return task.cont 