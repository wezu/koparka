from panda3d.core import PNMImage

def GetNeighbors(pos, map):
    nods=[] 
    if map.getRedVal(pos[0],63-pos[1])<0.5:
                nods.append({'NULL':0,
                            'NodeType':0,
                            'GridX':pos[0],
                            'GridY':pos[1],
                            'Length':8,
                            'Width':8,
                            'Height':0,      #not used
                            'PosX':int(pos[0]*8+4), #make sure it's an int,or the file will have some 200kb more of '.0'
                            'PosY':int(pos[1]*8+4),
                            'PosZ':0          #not used
                            })
    else:
        nods.append({'NULL':1,'NodeType':0,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
        return nods    
    coords=[(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1)]#counter clockwise
    for coord in coords:
        x=pos[0]+coord[0]
        y=pos[1]+coord[1]      
        map_y=63-y #map is upside down 
        if (x<64 and x>-1) and (map_y<64 and map_y>-1):
            if map.getRedVal(x,map_y)<0.5:
                nods.append({'NULL':0,
                            'NodeType':1,
                            'GridX':x,
                            'GridY':y,
                            'Length':8,
                            'Width':8,
                            'Height':0,      #not used
                            'PosX':int(x*8+4),
                            'PosY':int(y*8+4),
                            'PosZ':0          #not used
                            }) 
            else: 
                nods.append({'NULL':1,'NodeType':1,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
        else: #out of map           
            nods.append({'NULL':1,'NodeType':1,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
    return nods    
    
def GenerateNavmeshCSV(map, output): 
    #check the map, must be 64x64
    if map.getReadXSize()!=64 or map.getReadYSize()!=64:
        #print "WARNING: image resized to 64x64!"
        new_map=PNMImage(64,64)
        new_map.boxFilterFrom(0.0,map) 
        map=new_map
        
    #generate data    
    nods=[]    
    for y in range(0,64):    
        for x in range(0,64):
            nods+=GetNeighbors((x,y), map)    
    
    #write data 
    with open(output, 'w') as output_file:        
        #header
        output_file.write('Grid Size,64\n')
        output_file.write('NULL,NodeType,GridX,GridY,Length,Width,Height,PosX,PosY,PosZ\n')
        #data...
        for nod in nods:
            output_file.write('{NULL},{NodeType},{GridX},{GridY},{Length},{Width},{Height},{PosX},{PosY},{PosZ}\n'.format(**nod))
            
#test            
if __name__ == "__main__":
    map=PNMImage()
    map.read('nav1.png')  
    GenerateNavmeshCSV(map, 'from_img.csv')