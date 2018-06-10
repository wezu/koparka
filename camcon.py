from panda3d.core import *
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *

class CameraControler (DirectObject):
    def __init__(self, cfg, pos=(256,256,0), offset=(0, -120, 120), speed=50.0, angle=-45):

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

        #self.accept('w', self.keyMap.__setitem__, ['up', True])
        #self.accept('w-up', self.keyMap.__setitem__, ['up', False])
        #self.accept('s', self.keyMap.__setitem__, ['down', True])
        #self.accept('s-up', self.keyMap.__setitem__, ['down', False])
        #self.accept('a', self.keyMap.__setitem__, ['right', True])
        #self.accept('a-up', self.keyMap.__setitem__, ['right', False])
        #self.accept('d', self.keyMap.__setitem__, ['left', True])
        #self.accept('d-up', self.keyMap.__setitem__, ['left', False])
        self.accept(cfg['key_cam_rotate'], self.keyMap.__setitem__, ['rotate', True])
        self.accept(cfg['key_cam_rotate']+'-up', self.keyMap.__setitem__, ['rotate', False])
        self.accept(cfg['key_cam_pan'], self.keyMap.__setitem__, ['pan', True])
        self.accept(cfg['key_cam_pan']+'-up', self.keyMap.__setitem__, ['pan', False])
        self.accept(cfg['key_cam_pan2'], self.keyMap.__setitem__, ['pan', True])
        self.accept(cfg['key_cam_pan2']+'-up', self.keyMap.__setitem__, ['pan', False])
        self.accept(cfg['key_cam_rotate2'], self.keyMap.__setitem__, ['rotate', True])
        self.accept(cfg['key_cam_rotate2']+'-up', self.keyMap.__setitem__, ['rotate', False])

        self.mouseSpeed=speed #default 50.0
        self.accept(cfg['key_cam_zoomin'], self.zoom_control,[0.2])
        self.accept(cfg['key_cam_zoomout'],self.zoom_control,[-0.2])
        self.accept(cfg['key_cam_zoomin2'], self.zoom_control,[0.2])
        self.accept(cfg['key_cam_zoomout2'],self.zoom_control,[-0.2])

        self.accept(cfg['key_cam_fast']+'-'+cfg['key_cam_zoomin'], self.zoom_control,[0.8])
        self.accept(cfg['key_cam_fast']+'-'+cfg['key_cam_zoomout'],self.zoom_control,[-0.8])
        self.accept(cfg['key_cam_fast']+'-'+cfg['key_cam_zoomin2'], self.zoom_control,[0.8])
        self.accept(cfg['key_cam_fast']+'-'+cfg['key_cam_zoomout2'],self.zoom_control,[-0.8])

        self.accept(cfg['key_cam_slow']+'-'+cfg['key_cam_zoomin'], self.zoom_control,[0.1])
        self.accept(cfg['key_cam_slow']+'-'+cfg['key_cam_zoomout'],self.zoom_control,[-0.1])
        self.accept(cfg['key_cam_slow']+'-'+cfg['key_cam_zoomin2'], self.zoom_control,[0.1])
        self.accept(cfg['key_cam_slow']+'-'+cfg['key_cam_zoomout2'],self.zoom_control,[-0.1])


        self.skip=False
        #self.waterNP=None
        #self.waterCamera=None
        #self.wPlane=None

        taskMgr.add(self.update, "camcon_update")

    def zoom(self, t):
        base.camera.setY(base.camera, t)

    def zoom_control(self, amount):
        LerpFunc(self.zoom,fromData=0,toData=amount, duration=.2, blendType='easeOut').start()

    def _moveCamX(self, t):
        self.cameraNode.setX(self.cameraNode, 0.2*t*self.mouseSpeed)
    def _moveCamY(self, t):
        self.cameraNode.setY(self.cameraNode, 0.2*t*self.mouseSpeed)

    def _rotateCamH(self, t):
        self.cameraNode.setH(self.cameraNode.getH()- 0.2*t*self.mouseSpeed)
    def _rotateCamP(self, t):
        self.cameraGimbal.setP(self.cameraGimbal.getP()+ 0.2*t*self.mouseSpeed)

    def move_control(self, x, y):
        LerpFunc(self._moveCamX,fromData=0,toData=x, duration=.2).start()
        LerpFunc(self._moveCamY,fromData=0,toData=y, duration=.2).start()
        #Sequence(Wait(0.1), Func(base.win.movePointer, 0, base.win.getXSize()/2, base.win.getYSize()/2)).start()

    def rotate_control(self, h, p):
        LerpFunc(self._rotateCamH,fromData=0,toData=h, duration=.1).start()
        LerpFunc(self._rotateCamP,fromData=0,toData=p, duration=.1).start()
        #Sequence(Wait(0.1), Func(base.win.movePointer, 0, base.win.getXSize()/2, base.win.getYSize()/2)).start()

    def update(self, task):
        #if self.waterNP:
        #    if self.waterNP.getZ()>0.0:
        #        self.waterCamera.setMat(base.cam.getMat(render)*self.wPlane.getReflectionMat())
        if base.mouseWatcherNode.hasMouse():
            deltaX = base.mouseWatcherNode.getMouseX()  # mouse distance from the center
            deltaY = base.mouseWatcherNode.getMouseY()
            if self.keyMap['pan']:
                base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)
                if not self.skip:
                    if abs(deltaX)+abs(deltaY)>0.001:
                        self.move_control(deltaX, deltaY)
                        #base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)
                        #self.cameraNode.setX(self.cameraNode, 2.0*deltaX*self.mouseSpeed)
                        #self.cameraNode.setY(self.cameraNode, 2.0*deltaY*self.mouseSpeed)
                self.skip=False
            elif self.keyMap['rotate']:
                base.win.movePointer(0, base.win.getXSize()//2, base.win.getYSize()//2)
                if not self.skip:
                    if abs(deltaX)+abs(deltaY)>0.01:
                        self.rotate_control(deltaX, deltaY)
                    #self.cameraNode.setH(self.cameraNode.getH()- deltaX*self.mouseSpeed)
                    #self.cameraGimbal.setP(self.cameraGimbal.getP()+ deltaY*self.mouseSpeed)
                self.skip=False
            else:
                self.skip=True
        return task.cont
