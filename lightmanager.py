from panda3d.core import *

class LightManager():
    def __init__(self): 
        self.lights=[]
        self.max_lights=10
        self.update()
        
    def update(self):
        light_pos= PTA_LVecBase4f()
        light_color= PTA_LVecBase4f()
        num_lights=0
        for light in self.lights: 
            if light:
                light_pos.pushBack(UnalignedLVecBase4f(light[0], light[1], light[2], light[3]))
                light_color.pushBack(UnalignedLVecBase4f(light[4], light[5], light[6], 1.0))
                num_lights+=1
        for i in range(self.max_lights-num_lights):
            light_pos.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
            light_color.pushBack(UnalignedLVecBase4f(0.0,0.0,0.0,0.0))            
        render.setShaderInput('light_pos', light_pos)
        render.setShaderInput('light_color', light_color)
        render.setShaderInput('num_lights', num_lights)              
        
    def addLight(self, pos, color, radius):
        new_light=[float(pos[0]),float(pos[1]),float(pos[2]),float(radius*radius),float(color[0]), float(color[1]), float(color[2])]
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
            
    def setLight(self, id, pos, color, radius):
        if id <= len(self.lights):
            self.lights[id][0]=pos[0]
            self.lights[id][1]=pos[1]
            self.lights[id][2]=pos[2]
            self.lights[id][3]=radius*radius
            self.lights[id][4]=color[0]
            self.lights[id][5]=color[1]
            self.lights[id][6]=color[2]
            self.update() 