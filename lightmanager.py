from panda3d.core import *

class LightManager():
    def __init__(self, max_lights=8, ambient=(0.1, 0.1, 0.1)): 
        self.lights=[]
        #shader has a hardcoded limit of 100
        #but use more then 20 with care
        if max_lights>100:
            max_lights=100
        self.max_lights=max_lights
        self.ambientLight(ambient)
        self.update()
        taskMgr.add(self._perFrameUpdate, '_perFrameUpdate')
         
    def _perFrameUpdate(self, task):
        render.setShaderInput("camera_pos", base.cam.getPos(render))
        return task.cont
        
    def ambientLight(self, *args):
        color=[]
        for arg in args:
            color.append(arg)         
        if len(color)==1:                
            render.setShaderInput('ambient', color[0])
        elif len(color)>2:    
            render.setShaderInput('ambient', Vec3(color[0], color[1], color[2]))
        else:
            render.setShaderInput('ambient', Vec3(0.0, 0.0, 0.0))
            
    def update(self):
        light_pos= PTA_LVecBase4f()
        light_color= PTA_LVecBase4f()
        num_lights=0
        for light in self.lights: 
            if light:
                light_pos.pushBack(UnalignedLVecBase4f(light[0], light[1], light[2], light[3]))
                light_color.pushBack(UnalignedLVecBase4f(light[4], light[5], light[6], light[7]))
                num_lights+=1
        for i in range(self.max_lights-num_lights):
            light_pos.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
            light_color.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
        render.setShaderInput('light_pos', light_pos)
        render.setShaderInput('light_color', light_color)
        render.setShaderInput('num_lights', int(num_lights))#this should be an int, damn you outdated ATI driver!              
        
    def addLight(self, pos, color, radius, specular=-1.0):
        if specular==-1.0:
            specular=(color[0]+color[1]+color[2])/3.0        
        new_light=[float(pos[0]),float(pos[1]),float(pos[2]),float(radius*radius),float(color[0]), float(color[1]), float(color[2]), float(specular)]
        if len(self.lights)<self.max_lights:
            self.lights.append(new_light)
            self.update()
            return self.lights.index(new_light)
        else:
            index=None
            for light in self.lights:
                if light==None:
                    index=self.lights.index(light)
                    break
            if index:
                self.lights[index]=new_light
                self.update()
                return index
                
    def removeLight(self, id):
        if id <= len(self.lights):
            self.lights[id]=None
            self.update()
        
    def moveLight(self, id, pos):
        if id <= len(self.lights):
            self.lights[id][0]=pos[0]
            self.lights[id][1]=pos[1]
            self.lights[id][2]=pos[2]
            self.update()
                
    def setColor(self, id, color):
        if id <= len(self.lights):
            self.lights[id][4]=color[0]
            self.lights[id][5]=color[1]
            self.lights[id][6]=color[2]
            self.update()
            
    def setRadius(self, id, radius):
        if id <= len(self.lights):
            self.lights[id][3]=radius*radius
            self.update()  
            
    def setLight(self, id, pos, color, radius, specular=-1.0):
        if specular==-1.0:
            specular=(color[0]+color[1]+color[2])/3.0 
        if id <= len(self.lights):
            self.lights[id][0]=pos[0]
            self.lights[id][1]=pos[1]
            self.lights[id][2]=pos[2]
            self.lights[id][3]=radius*radius
            self.lights[id][4]=color[0]
            self.lights[id][5]=color[1]
            self.lights[id][6]=color[2]
            self.lights[id][7]=specular
            self.update() 
