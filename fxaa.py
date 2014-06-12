from panda3d.core import *
from direct.filter.FilterManager import FilterManager

def makeFXAA(manager=None, span_max=8.0, reduce_mul=8.0, subpixel_shift=4.0):
    wp=base.win.getProperties()
    winX = wp.getXSize()
    winY = wp.getYSize()
    tex = Texture()
    if manager==None:
        manager = FilterManager(base.win, base.cam)
    quad = manager.renderSceneInto(colortex=tex)
    quad.setShader(Shader.load(Shader.SLGLSL, "shaders/fxaa_v.glsl", "shaders/fxaa_f.glsl"))
    quad.setShaderInput("tex0", tex)
    quad.setShaderInput("rt_w",winX)
    quad.setShaderInput("rt_h",winY)
    quad.setShaderInput("FXAA_SPAN_MAX" , span_max)
    quad.setShaderInput("FXAA_REDUCE_MUL", 1.0/reduce_mul)
    quad.setShaderInput("FXAA_SUBPIX_SHIFT", 1.0/subpixel_shift)  
    return manager