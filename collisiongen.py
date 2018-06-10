from __future__ import print_function
from panda3d.core import LPoint3d, CS_default
from panda3d.egg import EggData
#from math import floor

def GenerateCollisionEgg(heightmap, output, input='data/collision3k.egg', scale=100.0):
    input_egg = EggData()
    input_egg.read(input)
    output_egg = EggData()
    output_egg.setCoordinateSystem(CS_default)
    output_egg.stealChildren(input_egg)
    VertexPool = output_egg.getChildren()[1]
    print("Generating mesh, this may take a while...", end="")
    for i in range(VertexPool.getHighestIndex()):
        if i%20000 == 0:
            try:
                base.graphicsEngine.renderFrame()
                print('.', end="")
            except:
                pass
        vert = VertexPool.getVertex(i)
        x0, y0, _ = vert.getPos3()
        #x, y = int(floor(x0+0.5)), int(floor(y0+0.5))
        x, y = int(x0), int(y0)
        if x==512: x=511
        elif x==0: x=1
        if y==512: y=511
        elif y==0: y=1
        vert.setPos(LPoint3d(x0, y0, heightmap.getBright(x,512-y)*scale))

    output_egg.writeEgg(output)
