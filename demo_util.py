from panda3d.core import *
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from direct.interval.IntervalGlobal import *
from panda3d.ai import *
import json
#import os
from ast import literal_eval as astEval

MASK_WATER=BitMask32.bit(1)
MASK_SHADOW=BitMask32.bit(2)

def processProps(level, functions):
    quadtree=level['quadtree']
    for node in quadtree:
        for child in node.getChildren():
            if child.hasPythonTag('formatProps'):
                props=child.getPythonTag('formatProps')
                for prop in props:
                    if prop in functions:
                        functions[prop](child, props[prop])


def setupFilters(manager, path, fxaa_only=False):
    colorTex = Texture()#the scene
    auxTex = Texture() # r=blur, g=shadow, b=?, a=?
    composeTex=Texture()#the scene(colorTex) blured where auxTex.r>0 and with shadows (blurTex2.r) added
    filters=[]
    final_quad = manager.renderSceneInto(colortex=colorTex, auxtex=auxTex)
    if final_quad is None or not fxaa_only:
        blurTex = Texture() #1/2 size of the shadows to be blured
        blurTex2 = Texture()
        glareTex = Texture()
        flareTex = Texture()
        #blurr shadows #1
        interquad0 = manager.renderQuadInto(colortex=blurTex, div=2)
        interquad0.setShader(Shader.load(Shader.SLGLSL, path+"shaders/blur_v.glsl", path+"shaders/blur_f.glsl"))
        interquad0.setShaderInput("input_map", auxTex)
        filters.append(interquad0)
        #blurrscene
        interquad1 = manager.renderQuadInto(colortex=blurTex2, div=4)
        interquad1.setShader(Shader.load(Shader.SLGLSL, path+"shaders/blur_v.glsl", path+"shaders/blur_f.glsl"))
        interquad1.setShaderInput("input_map", colorTex)
        filters.append(interquad1)
        #glare
        interquad2 = manager.renderQuadInto(colortex=glareTex, div=4)
        interquad2.setShader(Shader.load(Shader.SLGLSL, path+"shaders/glare_v.glsl", path+"shaders/glare_f.glsl"))
        interquad2.setShaderInput("auxTex", auxTex)
        interquad2.setShaderInput("colorTex", colorTex)
        interquad2.setShaderInput("blurTex", blurTex)
        filters.append(interquad2)
        #lense flare
        interquad3 = manager.renderQuadInto(colortex=flareTex, div=2)
        interquad3.setShader(Shader.load(path+"shaders/lens_flare.sha"))
        interquad3.setShaderInput("tex0", glareTex)
        filters.append(interquad3)
        #compose the scene
        interquad4 = manager.renderQuadInto(colortex=composeTex)
        interquad4.setShader(Shader.load(Shader.SLGLSL, path+"shaders/compose_v.glsl", path+"shaders/compose_f.glsl"))
        interquad4.setShaderInput("flareTex", flareTex)
        interquad4.setShaderInput("glareTex", glareTex)
        interquad4.setShaderInput("colorTex", colorTex)
        interquad4.setShaderInput("blurTex", blurTex)
        interquad4.setShaderInput("blurTex2", blurTex2)
        interquad4.setShaderInput("auxTex", auxTex)
        interquad4.setShaderInput("noiseTex", loader.loadTexture(path+"data/noise2.png"))
        interquad4.setShaderInput('time', 0.0)
        interquad4.setShaderInput('screen_size', Vec2(float(base.win.getXSize()),float(base.win.getYSize())))
        filters.append(interquad4)
    else:
        final_quad = manager.renderSceneInto(colortex=composeTex)
    #fxaa
    final_quad.setShader(Shader.load(Shader.SLGLSL, path+"shaders/fxaa_v.glsl", path+"shaders/fxaa_f.glsl"))
    final_quad.setShaderInput("tex0", composeTex)
    final_quad.setShaderInput("rt_w",float(base.win.getXSize()))
    final_quad.setShaderInput("rt_h",float(base.win.getYSize()))
    final_quad.setShaderInput("FXAA_SPAN_MAX" , float(8.0))
    final_quad.setShaderInput("FXAA_REDUCE_MUL", float(1.0/8.0))
    final_quad.setShaderInput("FXAA_SUBPIX_SHIFT", float(1.0/4.0))
    filters.append(final_quad)
    return filters

def loadModel(file, collision=None, animation=None):
    model=None
    if animation:
        model=Actor(file, animation)
        #default anim
        if 'default' in animation:
            model.loop('default')
        elif 'idle' in animation:
            model.loop('idle')
        else: #some random anim
             model.loop(animation.items()[0])
    else:
        model=loader.loadModel(file)
    model.setPythonTag('model_file', file)
    #load shaders
    for geom in model.findAllMatches('**/+GeomNode'):
        if geom.hasTag('cg_shader'):
            geom.setShader(loader.loadShader("shaders/"+geom.getTag('cg_shader')))
        elif geom.hasTag('glsl_shader'):
            glsl_shader=geom.getTag('glsl_shader')
            geom.setShader(Shader.load(Shader.SLGLSL, "shaders/{0}_v.glsl".format(glsl_shader),"shaders/{0}_f.glsl".format(glsl_shader)))
        else:
            #geom.setShader(loader.loadShader("shaders/default.cg"))
            geom.setShader(Shader.load(Shader.SLGLSL, "shaders/default_v.glsl","shaders/default_f.glsl"))
    #collisions
    model.setCollideMask(BitMask32.allOff())
    if collision:
        coll=loader.loadModel(collision)
        coll.reparentTo(model)
        coll.find('**/collision').setCollideMask(BitMask32.bit(2))
        coll.find('**/collision').setPythonTag('object', model)
        if animation:
            model.setPythonTag('actor_files', [file,animation,coll])
    else:
        try:
            model.find('**/collision').setCollideMask(BitMask32.bit(2))
            model.find('**/collision').setPythonTag('object', model)
        except:
            print "WARNING: Model {0} has no collision geometry!\nGenerating collision sphere...".format(file)
            bounds=model.getBounds()
            radi=bounds.getRadius()
            cent=bounds.getCenter()
            coll_sphere=model.attachNewNode(CollisionNode('collision'))
            coll_sphere.node().addSolid(CollisionSphere(cent[0],cent[1],cent[2], radi))
            coll_sphere.setCollideMask(BitMask32.bit(2))
            coll_sphere.setPythonTag('object', model)
            #coll_sphere.show()
            if animation:
                model.setPythonTag('actor_files', [file,animation,None])
    return model

def LoadScene(path, file, quad_tree, actors, terrain, grass, flatten=False):
    json_data=None
    with open(path+file) as f:
        json_data=json.load(f)
    return_data=[]
    for object in json_data:
        model=None
        if 'textures' in object:
            i=0
            for tex in object['textures']:
                terrain.setTexture(terrain.findTextureStage('tex{0}'.format(i+1)), loader.loadTexture(path+tex, anisotropicDegree=2), 1)
                #normal texture should have the same name but should be in '/normal/' directory
                normal_tex=tex.replace('/diffuse/','/normal/')
                terrain.setTexture(terrain.findTextureStage('tex{0}n'.format(i+1)), loader.loadTexture(path+normal_tex,anisotropicDegree=2), 1)
                i+=1
            continue
        elif 'grass' in object:
            i=0
            for tex in object['grass']:
                grs_tex= loader.loadTexture(path+tex)
                grs_tex.setWrapU(Texture.WMClamp)
                grs_tex.setWrapV(Texture.WMClamp)
                grass.setTexture(grass.findTextureStage('tex{0}'.format(i+1)), grs_tex, 1)
                i+=1
            continue
        elif 'model' in object:
            model=loadModel(path+object['model'])
        elif 'actor' in object:
            model=loadModel(path+object['actor'],path+object['actor_collision'],object['actor_anims'])
            actors.append(model)
        else:
            return_data.append(object)
        if model:
            model.reparentTo(quad_tree[object['parent_index']])
            formatProps=None
            try:
                formatProps=astEval(str(object['props']))
            except:
                pass
            if formatProps:
                model.setPythonTag('formatProps', formatProps)
            model.setPythonTag('props', object['props'])
            model.setHpr(render,object['rotation_h'],object['rotation_p'],object['rotation_r'])
            model.setPos(render,object['position_x'],object['position_y'],object['position_z'])
            model.setScale(object['scale'])

    if flatten:
        for node in quad_tree:
            flat=render.attachNewNode('flatten')
            for child in node.getChildren():
                if child.getPythonTag('props')=='': #objects with SOME properties should be keept alone
                    child.clearPythonTag('model_file')
                    child.clearPythonTag('props')
                    child.clearModelNodes()
                    child.wrtReparentTo(flat)
            flat.flattenStrong()
            flat.wrtReparentTo(node)
    return return_data

def makeQuadTree(root):
    nodeA=root.attachNewNode('quadA')
    nodeA.setPos(root,128,128,0)
    nodeB=root.attachNewNode('quadB')
    nodeB.setPos(root,384,128,0)
    nodeC=root.attachNewNode('quadC')
    nodeC.setPos(root,128,384,0)
    nodeD=root.attachNewNode('quadD')
    nodeD.setPos(root,384,384,0)
    nodeA1=nodeA.attachNewNode('quadA1')
    nodeA1.setPos(root,64, 64, 0)
    nodeA2=nodeA.attachNewNode('quadA2')
    nodeA2.setPos(root,192, 64, 0)
    nodeA3=nodeA.attachNewNode('quadA3')
    nodeA3.setPos(root,64, 192, 0)
    nodeA4=nodeA.attachNewNode('quadA4')
    nodeA4.setPos(root,192, 192, 0)
    nodeB1=nodeB.attachNewNode('quadB1')
    nodeB1.setPos(root,320, 64, 0)
    nodeB2=nodeB.attachNewNode('quadB2')
    nodeB2.setPos(root,448, 64, 0)
    nodeB3=nodeB.attachNewNode('quadB3')
    nodeB3.setPos(root,320, 192, 0)
    nodeB4=nodeB.attachNewNode('quadB4')
    nodeB4.setPos(root,448, 192, 0)
    nodeC1=nodeC.attachNewNode('quadC1')
    nodeC1.setPos(root,64, 320, 0)
    nodeC2=nodeC.attachNewNode('quadC2')
    nodeC2.setPos(root,192, 320, 0)
    nodeC3=nodeC.attachNewNode('quadC3')
    nodeC3.setPos(root,64, 448, 0)
    nodeC4=nodeC.attachNewNode('quadC4')
    nodeC4.setPos(root,192, 448, 0)
    nodeD1=nodeD.attachNewNode('quadD1')
    nodeD1.setPos(root,320, 320, 0)
    nodeD2=nodeD.attachNewNode('quadD2')
    nodeD2.setPos(root,448, 320, 0)
    nodeD3=nodeD.attachNewNode('quadD3')
    nodeD3.setPos(root,320, 448, 0)
    nodeD4=nodeD.attachNewNode('quadD4')
    nodeD4.setPos(root,448, 448, 0)
    quadtree=[nodeA1,nodeA2,nodeA3,nodeA4,
              nodeB1,nodeB2,nodeB3,nodeB4,
              nodeC1,nodeC2,nodeC3,nodeC4,
              nodeD1,nodeD2,nodeD3,nodeD4]
    return quadtree

def setupTerrain(path, detail_map1, detail_map2, height_map):
    mesh=loader.loadModel(path+'data/mesh80k.bam')
    mesh.reparentTo(render)
    mesh.setShader(Shader.load(Shader.SLGLSL, path+"shaders/terrain_v.glsl", path+"shaders/terrain_f.glsl"))
    h_map=loader.loadTexture(height_map)
    h_map.setWrapU(Texture.WMClamp)
    h_map.setWrapV(Texture.WMClamp)
    mesh.setShaderInput("height", h_map)
    mesh.setShaderInput("atr1", loader.loadTexture(detail_map1))
    mesh.setShaderInput("atr2", loader.loadTexture(detail_map2))
    render.setShaderInput("z_scale", 100.0)
    mesh.setShaderInput("tex_scale", 16.0)
    mesh.setTransparency(TransparencyAttrib.MNone)
    mesh.node().setBounds(OmniBoundingVolume())
    mesh.node().setFinal(1)
    mesh.setBin("background", 11)
    #mesh.setShaderInput("water_level",26.0)
    return mesh

def loadSkyDome(path):
    skydome = loader.loadModel(path+"data/skydome2")
    skydome.reparentTo(render)
    skydome.setPos(256, 256, -200)
    skydome.setScale(10)
    #skydome.setShaderInput("sky", Vec4(0.4,0.6,1.0, 1.0))
    #skydome.setShaderInput("fog", Vec4(1.0,1.0,1.0, 1.0))
    #skydome.setShaderInput("cloudColor", Vec4(0.9,0.9,1.0, 0.8))
    #skydome.setShaderInput("cloudTile",8.0)
    #skydome.setShaderInput("cloudSpeed",0.008)
    #skydome.setShaderInput("horizont",20.0)
    #skydome.setShaderInput("sunColor",Vec4(1.0,1.0,1.0, 1.0))
    #skydome.setShaderInput("skyColor",Vec4(1.0,1.0,1.0, 1.0))
    skydome.setBin('background', 1)
    skydome.setTwoSided(True)
    skydome.node().setBounds(OmniBoundingVolume())
    skydome.node().setFinal(1)
    skydome.setShader(Shader.load(Shader.SLGLSL, path+"shaders/cloud_v.glsl", path+"shaders/cloud_f.glsl"))
    skydome.hide(MASK_SHADOW)
    skydome.setTransparency(TransparencyAttrib.MNone, 1)
    return skydome

def setupWater(path, height_map):
    waterNP = loader.loadModel(path+"data/waterplane")
    waterNP.setPos(256, 256, 0)
    waterNP.setTransparency(TransparencyAttrib.MAlpha)
    waterNP.flattenLight()
    waterNP.setPos(0, 0, 30)    
    waterNP.reparentTo(render)
    #Add a buffer and camera that will render the reflection texture
    wBuffer = base.win.makeTextureBuffer("water", 512, 512)
    wBuffer.setClearColorActive(True)
    wBuffer.setClearColor(base.win.getClearColor())
    wBuffer.setSort(-1)
    waterCamera = base.makeCamera(wBuffer)
    waterCamera.reparentTo(render)
    waterCamera.node().setLens(base.camLens)
    waterCamera.node().setCameraMask(MASK_WATER)
    #Create this texture and apply settings
    wTexture = wBuffer.getTexture()
    wTexture.setWrapU(Texture.WMClamp)
    wTexture.setWrapV(Texture.WMClamp)
    wTexture.setMinfilter(Texture.FTLinearMipmapLinear)
    #Create plane for clipping and for reflection matrix
    wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, 19))
    wPlaneNP = render.attachNewNode(PlaneNode("water", wPlane))
    tmpNP = NodePath("StateInitializer")
    tmpNP.setClipPlane(wPlaneNP)
    tmpNP.setAttrib(CullFaceAttrib.makeReverse())
    waterCamera.node().setInitialState(tmpNP.getState())
    waterNP.setShaderInput('camera',waterCamera)
    waterNP.setShaderInput("reflection",wTexture)

    waterNP.setShader(Shader.load(Shader.SLGLSL, "shaders/water2_v.glsl", "shaders/water2_f.glsl"))
    waterNP.setShaderInput("water_norm", loader.loadTexture(path+'data/water.png'))
    waterNP.setShaderInput("water_height", loader.loadTexture(path+'data/ocen3.png'))
    waterNP.setShaderInput("height", loader.loadTexture(height_map))
    #waterNP.setShaderInput("tile",20.0)
    #waterNP.setShaderInput("water_level",30.0)
    #waterNP.setShaderInput("speed",0.01)
    #waterNP.setShaderInput("wave",Vec4(0.005, 0.002, 6.0, 1.0))
    #waterNP.setDepthWrite(False)
    waterNP.hide(MASK_WATER)
    waterNP.hide(MASK_SHADOW)
    waterNP.setBin("transparent", 31)
    return {'waterNP':waterNP, 'waterCamera':waterCamera, 'wBuffer':wBuffer, 'wPlane':wPlane}

def setupLights(lmanager):
    #sun
    sun=lmanager.addLight(pos=(256.0, 256.0, 200.0), color=(0.9, 0.9, 0.9), radius=10000.0)

    #ambient light
    alight = DirectionalLight('dlight')
    alight.setColor(Vec4(.1, .1, .15, 1.0))
    ambientLight = render.attachNewNode(alight)
    render.setLight(ambientLight)
    ambientLight.setPos(base.camera.getPos())
    ambientLight.setHpr(base.camera.getHpr())
    ambientLight.wrtReparentTo(base.camera)
    render.setShaderInput("ambient", Vec4(.001, .001, .001, 1))
    return sun

def setupShadows(buffer_size=1024):
    #render shadow map
    depth_map = Texture()
    depth_map.setFormat(Texture.FDepthComponent)
    depth_map.setWrapU(Texture.WMBorderColor)
    depth_map.setWrapV(Texture.WMBorderColor)
    depth_map.setBorderColor(Vec4(1.0, 1.0, 1.0, 1.0))
    #depth_map.setMinfilter(Texture.FTShadow )
    #depth_map.setMagfilter(Texture.FTShadow )
    depth_map.setMinfilter(Texture.FTLinearMipmapLinear)
    depth_map.setMagfilter(Texture.FTLinearMipmapLinear)
    props = FrameBufferProperties()
    props.setRgbColor(0)
    props.setDepthBits(1)
    props.setAlphaBits(0)
    props.set_srgb_color(False)
    depthBuffer = base.win.makeTextureBuffer("Shadow Buffer", buffer_size, buffer_size, to_ram=False, tex=depth_map, fbp = props)
    depthBuffer.setClearColor(Vec4(1.0,1.0,1.0,1.0))
    depthBuffer.setSort(-101)
    shadowCamera = base.makeCamera(depthBuffer)
    lens = OrthographicLens()
    lens.setFilmSize(300, 300)
    shadowCamera.node().setLens(lens)
    shadowCamera.node().getLens().setNearFar(1,400)
    shadowCamera.node().setCameraMask(MASK_SHADOW)

    shadowCamera.reparentTo(render)
    shadowCamera.setPos(256, 256, 200)
    shadowCamera.setHpr(90, -90, 0)

    sunNode=render.attachNewNode('sunNode')
    sunNode.setPos(256, 256, 0)
    shadowCamera.wrtReparentTo(sunNode)
    render.setShaderInput('shadow', depth_map)
    render.setShaderInput("bias", 1.0)
    render.setShaderInput('shadowCamera',shadowCamera)
    return {'sunNode':sunNode, 'shadowCamera':shadowCamera}

def loadLevel(path, from_dir):
    #files needed to be read
    objects=path+from_dir+'/objects.json'
    collision=path+from_dir+'/collision'
    detail_map1=path+from_dir+'/detail0.png'
    detail_map2=path+from_dir+'/detail1.png'
    grass_map=path+from_dir+'/grass.png'
    height_map=path+from_dir+'/heightmap.png'

    #setup all the needed structures...
    actors=[]
    #quadtree structure
    quadtree=makeQuadTree(render)
    #setup terrain
    mesh=setupTerrain(path, detail_map1, detail_map2, height_map)
    #collision mesh
    collision_mesh=loader.loadModel(collision)
    collision_mesh.reparentTo(render)
    #skydome
    skydome=loadSkyDome(path)
    #water
    water=setupWater(path, height_map)
    wBuffer=water['wBuffer']
    waterNP=water['waterNP']
    waterCamera=water['waterCamera']

    grass=render.attachNewNode('grass')
    createGrassTile(path, grass_map, height_map, uv_offset=Vec2(0,0), pos=(0,0,0), parent=grass, fogcenter=Vec3(256,256,0))
    createGrassTile(path, grass_map, height_map,uv_offset=Vec2(0,0.5), pos=(0, 256, 0), parent=grass, fogcenter=Vec3(256,0,0))
    createGrassTile(path, grass_map, height_map,uv_offset=Vec2(0.5,0), pos=(256, 0, 0), parent=grass, fogcenter=Vec3(0,256,0))
    createGrassTile(path, grass_map, height_map,uv_offset=Vec2(0.5,0.5), pos=(256, 256, 0), parent=grass, fogcenter=Vec3(0,0,0))
    grass.setBin("background", 11)
    grass.hide(MASK_WATER)
    grass.hide(MASK_SHADOW)

    #load the json scene
    data=LoadScene(path, objects, quadtree, actors, mesh, grass, flatten=False)

    #load sky and water data
    TerrainTile=data[0]['TerrainTile']
    TerrainScale=data[0]['TerrainScale']
    SkyTile=data[0]['SkyTile']
    CloudSpeed=data[0]['CloudSpeed']
    WaveTile=data[0]['WaveTile']
    WaveHeight=data[0]['WaveHeight']
    WaveXYMove=[data[0]['WaveXYMove'][0],data[0]['WaveXYMove'][1]]
    WaterTile=data[0]['WaterTile']
    WaterSpeed=data[0]['WaterSpeed']
    WaterLevel=data[0]['WaterLevel']
    skydome.setShaderInput("cloudTile",SkyTile)
    skydome.setShaderInput("cloudSpeed",CloudSpeed)
    mesh.setShaderInput("water_level",WaterLevel)
    render.setShaderInput("z_scale", TerrainScale)
    mesh.setShaderInput("tex_scale", TerrainTile)
    if WaterLevel>0.0:
        wBuffer.setActive(True)
        waterNP.show()
        waterNP.setShaderInput("tile",WaterTile)
        waterNP.setShaderInput("speed",WaterSpeed)
        waterNP.setShaderInput("water_level",WaterLevel)
        waterNP.setShaderInput("wave",Vec4(WaveXYMove[0],WaveXYMove[1],WaveTile,WaveHeight))
        waterNP.setPos(0, 0, WaterLevel)
        wPlane = Plane(Vec3(0, 0, 1), Point3(0, 0, WaterLevel))
        wPlaneNP = render.attachNewNode(PlaneNode("water", wPlane))
        water['wPlane']=wPlane
        mesh.setShaderInput("water_level",WaterLevel)
        tmpNP = NodePath("StateInitializer")
        tmpNP.setClipPlane(wPlaneNP)
        tmpNP.setAttrib(CullFaceAttrib.makeReverse())
        waterCamera.node().setInitialState(tmpNP.getState())
    else:
        waterNP.hide()
        wBuffer.setActive(False)
        mesh.setShaderInput("water_level",-10.0)

    level={'actors':actors,
           'quadtree':quadtree,
           'mesh':mesh,
           'collision_mesh':collision_mesh,
           'skydome':skydome,
           'water':water,
           'grass':grass}
    return level

def createGrassTile(path, grass_map, height_map, uv_offset, pos, parent, fogcenter=Vec3(0,0,0), count=256):
    grass=loader.loadModel("data/grass_model_lo")
    #grass.setTwoSided(True)
    grass.setTransparency(TransparencyAttrib.MBinary, 1)
    grass.reparentTo(parent)
    grass.setInstanceCount(count)
    grass.node().setBounds(BoundingBox((0,0,0), (256,256,128)))
    grass.node().setFinal(1)
    grass.setShader(Shader.load(Shader.SLGLSL, "shaders/grass_lights_v.glsl", "shaders/grass_lights_f.glsl"))
    #grass.setShader(Shader.load(Shader.SLGLSL, "shaders/grass_v.glsl", "shaders/grass_f.glsl"))
    grass.setShaderInput('height', loader.loadTexture(height_map))
    grass.setShaderInput('grass', loader.loadTexture(grass_map))
    grass.setShaderInput('uv_offset', uv_offset)
    grass.setShaderInput('fogcenter', fogcenter)
    grass.setPos(pos)
    return grass

class CameraControler (DirectObject):
    def __init__(self, offset=(0, -30, 30),focus_point=(0,0,6), speed=15.0, shadows=None):

        self.cameraNode  = render.attachNewNode("cameraNode")
        self.cameraGimbal  = self.cameraNode.attachNewNode("cameraGimbal")
        base.camera.setPos(offset)
        base.camera.lookAt(focus_point)
        base.camera.wrtReparentTo(self.cameraGimbal)
        self.shadows=shadows

        self.keyMap = {'rotate': False}

        self.accept('mouse3', self.keyMap.__setitem__, ['rotate', True])
        self.accept('mouse3-up', self.keyMap.__setitem__, ['rotate', False])

        self.mouseSpeed=speed #default 50.0
        self.accept('wheel_up', self.zoom_control,[0.2])
        self.accept('wheel_down',self.zoom_control,[-0.2])
        self.accept('=', self.zoom_control,[2.0])
        self.accept('-',self.zoom_control,[-2.0])

        self.accept('control-wheel_up', self.zoom_control,[0.8])
        self.accept('control-wheel_down',self.zoom_control,[-0.8])
        self.accept('control-=', self.zoom_control,[5.0])
        self.accept('control--',self.zoom_control,[-5.0])

        self.accept('alt-wheel_up', self.zoom_control,[0.1])
        self.accept('alt-wheel_down',self.zoom_control,[-0.1])
        self.accept('alt-=', self.zoom_control,[0.5])
        self.accept('alt--',self.zoom_control,[-0.5])

        self.x=0.0
        self.y=0.0
        taskMgr.add(self.update, "camcon_update", sort=45)

    def zoom(self, t):
        distance=base.camera.getDistance(self.cameraNode)
        if t > 0.0 and distance <15.0:
            return
        if t < 0.0 and distance >100.0:
            return
        base.camera.setY(base.camera, t)
        #lens = self.shadows['shadowCamera'].node().getLens()
        #film_size=lens.getFilmSize()-Vec2(t*5.0, t*5.0)
        #print film_size
        #lens.setFilmSize(film_size)

    def zoom_control(self, amount):
        LerpFunc(self.zoom,fromData=0,toData=amount, duration=.3, blendType='easeOut').start()



    def _rotateCamH(self, t):
        self.cameraNode.setH(self.cameraNode.getH()+ t*self.mouseSpeed)

    def _rotateCamP(self, t):
        if t > 0.0 and self.cameraGimbal.getP(render)<-15.0:
            return
        elif t < 0.0 and self.cameraGimbal.getP(render)>40.0:
            return
        self.cameraGimbal.setP(self.cameraGimbal.getP()- t*self.mouseSpeed)

    def rotate_control(self, h, p):
        LerpFunc(self._rotateCamH,fromData=0,toData=h, duration=.3).start()
        LerpFunc(self._rotateCamP,fromData=0,toData=p, duration=.3).start()

    def update(self, task):
        if base.mouseWatcherNode.hasMouse():
            x= base.mouseWatcherNode.getMouseX()
            y= base.mouseWatcherNode.getMouseY()
            deltaX = self.x-x
            deltaY = self.y-y
            self.x=x
            self.y=y
            if self.keyMap['rotate']:
                self.rotate_control(deltaX, deltaY)
        return task.cont

class PointAndClick():
    def __init__(self):
        #collision detection setup
        self.traverser = CollisionTraverser()
        #self.traverser.showCollisions(render)
        self.queue     = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        #print "mask:", self.pickerNP.getCollideMask()
        mask=BitMask32.bit(1)
        mask.setBit(2)
        self.pickerNode.setFromCollideMask(mask)
        self.pickerNode.setIntoCollideMask(BitMask32.allOff())
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.traverser.addCollider(self.pickerNP, self.queue)

    def getPos(self):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(base.camNode, mpos.getX(), mpos.getY())
            self.traverser.traverse(render)
            if self.queue.getNumEntries() > 0:
                self.queue.sortEntries()
                return self.queue.getEntry(0).getSurfacePoint(render)
        return None

class Navigator():
    def __init__(self, navmesh, seeker, actor, mass=5, force=10, max_force=10, tick=0.1):

        self.seeker=seeker
        self.actor=actor
        self.target=None

        self.seekerNode=render.attachNewNode('ai_seeker')
        self.seekerNode.setPos(seeker.getPos())
        self.seekerNode.setZ(0)

        self.AIworld = AIWorld(render)
        self.AIseeker = AICharacter("seeker",self.seekerNode, mass, force, max_force)
        self.AIworld.addAiChar(self.AIseeker)
        self.AIseeker.getAiBehaviors()
        self.AIseeker.getAiBehaviors().initPathFind(navmesh)

        taskMgr.doMethodLater(tick, self.AIUpdate,"AIUpdate")

    def moveTo(self, target):
        try:
            self.AIseeker.getAiBehaviors().pathFindTo(target, "addPath")
            self.target=target
            #print "new target"
        except:
            print "Can't get there!"

    def AIUpdate(self,task):
        try:
            self.AIworld.update()
        except:
             print "AI exception!"
             print "the AI exploded, if you can provide info on how it happend, fell free to bug rdb on IRC about it, don't tell him I send you"
        #self.AIworld.update()
        pos=self.seekerNode.getPos(render)
        pos[2]=self.seeker.getZ()
        if self.target:
            status=self.AIseeker.getAiBehaviors().behaviorStatus("pathfollow")
            if status=="active":
                if(self.actor.getCurrentAnim()!="walk"):
                    self.actor.loop("walk")
            else:
                if(self.actor.getCurrentAnim()!="idle"):
                    self.actor.loop("idle")
            hpr=self.seekerNode.getHpr(render)
            old_hpr=self.seeker.getHpr(render)
            if abs(old_hpr[0]-hpr[0])>180:
                hpr[0]=hpr[0]-360.0
            LerpPosHprInterval(self.seeker, 0.2, pos, hpr).start()
        return task.again
