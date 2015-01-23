from panda3d.core import PNMImage
import os, sys

def GenerateCollisionEgg(heightmap, output, input='data/collision3k.egg', scale=100.0):
    #heightmap=PNMImage()
    #heightmap.read(image)
    input_egg=file(input, 'r')
    output_egg=file(output, 'w')
    isVertexPos=False    
    print "Generating mesh, this may take a while..."
    for line in input_egg.readlines():
        if isVertexPos:
            vertex=line.split()
            x= int(float(vertex[0]))
            y= int(float(vertex[1]))
            if x==512:
                x=511
            if x==0:
                x=1    
            if y==512:
                y=511
            if y==0:
                y=1     
            vertex[2]=heightmap.getBright(x,512-y)*scale
            output_egg.write('    '+vertex[0]+' '+vertex[1]+' '+str(vertex[2])+'\n')
            isVertexPos=False
        else:
            if line.strip().startswith('<Vertex>'): 
                isVertexPos=True
                output_egg.write(line)
            else:
                output_egg.write(line)
    output_egg.close()   
    input_egg.close()