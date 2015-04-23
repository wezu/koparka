from panda3d.core import *
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles import Particles
from direct.particles import ForceGroup
from panda3d.physics import*

def createEffect(values):
    p = ParticleEffect()
    loadValues(values, p)
    color_gradient=loader.loadTexture(values["color_gradient"])
    size_gradient=loader.loadTexture(values["size_gradient"])
    shape_gradient=loader.loadTexture(values["shape_gradient"])
    blend_gradient=loader.loadTexture("data/blend.png", minfilter=Texture.FTNearest, magfilter=Texture.FTNearest)
    color_gradient.setWrapU(Texture.WMClamp)
    color_gradient.setWrapV(Texture.WMClamp)
    color_gradient.setFormat(Texture.F_srgb_alpha)
    size_gradient.setWrapU(Texture.WMClamp)
    size_gradient.setWrapV(Texture.WMClamp)
    shape_gradient.setWrapU(Texture.WMClamp)
    shape_gradient.setWrapV(Texture.WMClamp)
    blend_gradient.setWrapU(Texture.WMClamp)
    blend_gradient.setWrapV(Texture.WMClamp)
    for geom in p.findAllMatches('**/+GeomNode'):       
        geom.setDepthWrite(False)
        #geom.setBin("transparent", 31)
        #need to hide it from the water and shadow camera now... I don't know hot to get the geom later :(
        geom.hide(BitMask32.bit(1))
        geom.hide(BitMask32.bit(2))
        geom.setShader(Shader.load(Shader.SLGLSL, "shaders/vfx_v.glsl","shaders/vfx_f.glsl"), 1)
        geom.setShaderInput('distortion',values['distortion'])
        #geom.setShaderInput("fog",  Vec4(0.4, 0.4, 0.4, 0.002))
        geom.setShaderInput("color_gradient", color_gradient)
        geom.setShaderInput("size_gradient",  size_gradient)
        geom.setShaderInput("shape_gradient", shape_gradient)
        geom.setShaderInput("blend_gradient", blend_gradient)
    #p.start(parent=self.root, renderParent = render) 
    return p  

def loadValues(v, p):
    p0 = Particles.Particles('particles-1') #const.
    # Particles parameters
    p0.setFactory("PointParticleFactory") #const.
    p0.setRenderer("SpriteParticleRenderer")#const.
    p0.setEmitter(v["emiter"])
    p0.setPoolSize(v["pool"])
    p0.setBirthRate(v["birthRate"])
    p0.setLitterSize(v["litter"])
    p0.setLitterSpread(v["litterSpread"])        
    p0.setLocalVelocityFlag(1)#const.
    p0.setSystemGrowsOlderFlag(0)#const.
    # Factory parameters
    p0.factory.setLifespanBase(v["life"])
    p0.factory.setLifespanSpread(v["lifeSpread"])
    p0.factory.setMassBase(v["mass"])
    p0.factory.setMassSpread(v["massSpread"])
    p0.factory.setTerminalVelocityBase(100.0000) #has no effect?
    p0.factory.setTerminalVelocitySpread(0.0000) #has no effect?           
    # Renderer parameters
    #p0.renderer.setAlphaMode(BaseParticleRenderer.PRALPHAIN)
    #p0.renderer.setUserAlpha(1.00)
    # Sprite parameters
    p0.renderer.addTextureFromFile('particle/smoke1.png') #some default must be added or it bugs out
    p0.renderer.setColor(Vec4(1.00, 1.00, 1.00, 1.00))
    p0.renderer.setXScaleFlag(0)
    p0.renderer.setYScaleFlag(0)
    p0.renderer.setAnimAngleFlag(0)
    p0.renderer.setNonanimatedTheta(180.0000) #?
    p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PRALPHANONE)    
    if v['colorBlend']=="blend":    
        p0.renderer.setAlphaDisable(0)
        p0.renderer.setColorBlendMode(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOneMinusIncomingAlpha)#TODO!
    elif v['colorBlend']=="add":    
        p0.renderer.setAlphaDisable(1)
        p0.renderer.setColorBlendMode(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne)        
    p0.renderer.getColorInterpolationManager().addLinear(0.0,1.0,Vec4(0.0,0.0,0.0,1.0),Vec4(1.0,1.0,1.0,1.0),True)
    # Emitter parameters
    p0.emitter.setEmissionType(v["mode"])
    p0.emitter.setAmplitude(v["amplitude"])
    p0.emitter.setAmplitudeSpread(v["amplitudeSpread"])
    p0.emitter.setOffsetForce(Vec3(v["offsetForce"][0], v["offsetForce"][1], v["offsetForce"][2]))
    p0.emitter.setExplicitLaunchVector(Vec3(0.0000, 0.0000, 0.0000))
    p0.emitter.setRadiateOrigin(Point3(0.0000, 0.0000, 0.0000))
    if v['emiter']=='BoxEmitter':
        p0.emitter.setMaxBound(Point3(v['max'][0],v['max'][1],v['max'][2])) 
        p0.emitter.setMinBound(Point3(v['min'][0],v['min'][1],v['min'][2])) 
    elif v['emiter']=='DiscEmitter':
        p0.emitter.setRadius(v["radius"])
        p0.emitter.setInnerAngle(v["innerAngle"])
        p0.emitter.setInnerMagnitude(v["innerMagnitude"])
        p0.emitter.setOuterAngle(v["outerAngle"])
        p0.emitter.setOuterMagnitude(v["outerMagnitude"]) 	
    elif v['emiter']=='LineEmitter':
        p0.emitter.setEndpoint1(Point3(v['max'][0],v['max'][1],v['max'][2])) 
        p0.emitter.setEndpoint2(Point3(v['min'][0],v['min'][1],v['min'][2]))         	
    elif v['emiter']=='PointEmitter':
        pass #no options here
    elif v['emiter']=='RectangleEmitter':
        p0.emitter.setMaxBound(Point3(v['max'][0],v['max'][1],v['max'][2])) 
        p0.emitter.setMinBound(Point3(v['min'][0],v['min'][1],v['min'][2])) 
    elif v['emiter']=='RingEmitter':  
        p0.emitter.setAngle(v["angle"])
        p0.emitter.setRadius(v["radius"])
        p0.emitter.setRadiusSpread(v["radiusSpread"])
    elif v['emiter']=='SphereSurfaceEmitter':            
        p0.emitter.setRadius(v["radius"])
    elif v['emiter']=='SphereVolumeEmitter':            
        p0.emitter.setRadius(v["radius"])
    elif v['emiter']=='TangentRingEmitter':         
        p0.emitter.setRadius(v["radius"])
        p0.emitter.setRadiusSpread(v["radiusSpread"])
    p.addParticles(p0)
    f0 = ForceGroup.ForceGroup('default')
    # Force parameters
    if v["forceVector"][3]>0.0:
        force0 = LinearVectorForce(Vec3(v["forceVector"][0],v["forceVector"][1],v["forceVector"][2]), v["forceVector"][3], v["forceVector"][4])
        force0.setVectorMasks(1, 1, 1)
        force0.setActive(1)
        f0.addForce(force0)
    if v["forceJitter"][1]>0:    
        force1 = LinearJitterForce(v["forceJitter"][0], v["forceJitter"][1])
        force1.setVectorMasks(1, 1, 1)
        force1.setActive(1)
        f0.addForce(force1)
    if v["forceSink"][5]>0:        
        force2 = LinearSinkForce(Point3(v["forceSink"][0], v["forceSink"][1], v["forceSink"][2]), v["forceSink"][3], v["forceSink"][4], v["forceSink"][5], v["forceSink"][6])
        force2.setVectorMasks(1, 1, 1)
        force2.setActive(1)
        f0.addForce(force2)
    if v["forceSource"][5]>0:    
        force3 = LinearSourceForce(Point3(v["forceSource"][0], v["forceSource"][1], v["forceSource"][2]), v["forceSource"][3], v["forceSource"][4], v["forceSource"][5], v["forceSource"][6])
        force3.setVectorMasks(1, 1, 1)
        force3.setActive(1)
        f0.addForce(force3)
    if v["forceVertex"][3]>0:    
        force4 = LinearCylinderVortexForce(v["forceSource"][0], v["forceSource"][1], v["forceSource"][2], v["forceSource"][3], v["forceSource"][4])
        force4.setVectorMasks(1, 1, 1)
        force4.setActive(1)
        f0.addForce(force4)    
    p.addForceGroup(f0)