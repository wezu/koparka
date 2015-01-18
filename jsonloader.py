from panda3d.core import *
import json
from direct.actor.Actor import Actor

def LoadScene(file, quad_tree, actors, terrain, textures, current_textures=None, flatten=False):
    json_data=None
    with open(file) as f:  
        json_data=json.load(f)
        
    for object in json_data:
        print ".",
        if 'textures' in object:
            i=0
            for tex in object['textures']:
                if tex in textures:
                    if current_textures:
                        id=textures.index(tex)                    
                        current_textures[i]=id
                    terrain.setTexture(terrain.findTextureStage('tex{0}'.format(i+1)), loader.loadTexture(tex), 1)
                    #normal texture should have the same name but should be in '/normal/' directory
                    normal_tex=tex.replace('/diffuse/','/normal/')
                    terrain.setTexture(terrain.findTextureStage('tex{0}n'.format(i+1)), loader.loadTexture(normal_tex), 1)
                else:
                    print "WARNING: texture '{0}' not found!".format(tex)
                i+=1
            continue    
        elif 'model' in object:
            model=loader.loadModel(object['model'])
            model.setPythonTag('model_file', object['model'])
        elif 'actor' in object:
            model=Actor(object['actor'], object['actor_anims'])
            collision=loader.loadModel(object['actor_collision'])            
            collision.reparentTo(model)
            actors.append(model)
            model.setPythonTag('actor_files', [object['actor'],object['actor_anims'],object['actor_collision']])            
            #default anim
            if 'default' in object['actor_anims']:
                model.loop('default')
            elif 'idle' in object['actor_anims']:
                model.loop('idle')
            else: #some random anim
                model.loop(object['actor_anims'].items()[0])
        model.reparentTo(quad_tree[object['parent_index']])
        model.setCollideMask(BitMask32.allOff())        
        model.setShader(loader.loadShader("shaders/default.cg")) 
        model.find('**/collision').setCollideMask(BitMask32.bit(2))        
        model.find('**/collision').setPythonTag('object', model)
        
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
        
def SaveScene(file, quad_tree, textures, current_textures=None):
    export_data=[]
    if current_textures:
        temp=[]
        for id in current_textures:
            temp.append(textures[id])    
        export_data.append({'textures':temp})    
    else:
        export_data.append({'textures':textures})
    for node in quad_tree:
        for child in node.getChildren():
            temp={}
            if child.hasPythonTag('model_file'):
                temp['model']=unicode(child.getPythonTag('model_file'))
            elif child.hasPythonTag('actor_files'):
                temp['actor']=unicode(child.getPythonTag('actor_files')[0])
                temp['actor_anims']=child.getPythonTag('actor_files')[1]
                temp['actor_collision']=child.getPythonTag('actor_files')[2]
            temp['rotation_h']=child.getH(render)
            temp['rotation_p']=child.getP(render)
            temp['rotation_r']=child.getR(render)            
            temp['position_x']=child.getX(render)
            temp['position_y']=child.getY(render)
            temp['position_z']=child.getZ(render)
            temp['scale']=child.getScale()[0]            
            temp['parent_name']=node.getName()
            temp['parent_index']=quad_tree.index(node)
            temp['props']=unicode(child.getPythonTag('props'))
            export_data.append(temp)
    with open(file, 'w') as outfile:
        json.dump(export_data, outfile, indent=4, separators=(',', ': '), sort_keys=True)        