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
        model.setHpr(render,object['hpr'][0],object['hpr'][1],object['hpr'][2])
        model.setPos(render,object['pos'][0],object['pos'][1],object['pos'][2])
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
            temp['hpr']=(child.getH(render), child.getP(render),child.getR(render))
            temp['pos']=(child.getX(render), child.getY(render),child.getZ(render))
            temp['scale']=child.getScale()[0]            
            temp['parent_name']=node.getName()
            temp['parent_index']=quad_tree.index(node)
            temp['props']=str(child.getPythonTag('props'))
            export_data.append(temp)
    with open(file, 'w') as outfile:
        json.dump(export_data, outfile, indent=4, separators=(',', ': '))        