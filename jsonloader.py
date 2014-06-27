from panda3d.core import *
import json

def LoadScene(file, quad_tree, flatten=False):
    json_data=None
    with open(file) as f:  
        json_data=json.load(f)
        
    for object in json_data:
        print ".",
        model=loader.loadModel(object['model'])
        model.reparentTo(quad_tree[object['parent_index']])
        model.setCollideMask(BitMask32.allOff())
        model.setShaderAuto()
        model.find('**/collision').setCollideMask(BitMask32.bit(2))        
        model.find('**/collision').setPythonTag('object', model)
        model.setPythonTag('model_file', object['model'])
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
        
def SaveScene(file, quad_tree):
    export_data=[]
    for node in quad_tree:
        for child in node.getChildren():
            temp={}
            temp['model']=str(child.getPythonTag('model_file'))
            temp['rotation_h']=child.getH(render)
            temp['rotation_p']=child.getP(render)
            temp['rotation_r']=child.getR(render)            
            temp['position_x']=child.getX(render)
            temp['position_y']=child.getY(render)
            temp['position_z']=child.getZ(render)
            temp['scale']=child.getScale()[0]            
            temp['parent_name']=node.getName()
            temp['parent_index']=quad_tree.index(node)
            temp['props']=str(child.getPythonTag('props'))
            export_data.append(temp)
    with open(file, 'w') as outfile:
        json.dump(export_data, outfile, indent=4, separators=(',', ': '), sort_keys=True)        