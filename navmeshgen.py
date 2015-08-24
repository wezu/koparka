from panda3d.core import PNMImage
from direct.stdpy.file import open

def GetNeighbors(pos, map, map_size, world_map_size=512.0):   
    node_size=world_map_size/map_size
    nods=[] 
    if map.getRedVal(pos[0],(map_size-1)-pos[1])<0.5:
                nods.append({'NULL':0,
                            'NodeType':0,
                            'GridX':pos[0],
                            'GridY':pos[1],
                            'Length':8,
                            'Width':8,
                            'Height':0,      #not used
                            'PosX':pos[0]*node_size+node_size/2,
                            'PosY':pos[1]*node_size+node_size/2,
                            'PosZ':0          #not used
                            })
    else:
        nods.append({'NULL':1,'NodeType':0,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
        return nods    
    coords=[(-1,1),(-1,0),(-1,-1),(0,-1),(1,-1),(1,0),(1,1),(0,1)]#counter clockwise
    for coord in coords:
        x=pos[0]+coord[0]
        y=pos[1]+coord[1]      
        map_y=(map_size-1)-y #map is upside down 
        if (x<map_size and x>-1) and (map_y<map_size and map_y>-1):
            if map.getRedVal(x,map_y)<0.5:
                nods.append({'NULL':0,
                            'NodeType':1,
                            'GridX':x,
                            'GridY':y,
                            'Length':8,
                            'Width':8,
                            'Height':0,      #not used
                            'PosX':x*node_size+node_size/2,
                            'PosY':y*node_size+node_size/2,
                            'PosZ':0          #not used
                            }) 
            else: 
                nods.append({'NULL':1,'NodeType':1,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
        else: #out of map           
            nods.append({'NULL':1,'NodeType':1,'GridX':0,'GridY':0,'Length':0,'Width':0,'Height':0,'PosX':0,'PosY':0,'PosZ':0})
    return nods    
    
def GenerateNavmeshCSV(map, output): 
    #check the map size
    map_size=map.getReadXSize()    
    #make it square
    if map.getReadYSize()!=map_size:
        new_map=PNMImage(map_size,map_size)
        new_map.boxFilterFrom(0.0,map) 
        map=new_map       
  
    #generate data    
    nods=[]    
    for y in range(0,map_size):    
        for x in range(0,map_size):
            nods+=GetNeighbors((x,y), map, map_size)    
    
    #write data 
    with open(output, 'w') as output_file:        
        #header
        output_file.write('Grid Size,'+str(map_size)+'\n')
        output_file.write('NULL,NodeType,GridX,GridY,Length,Width,Height,PosX,PosY,PosZ\n')
        #data...
        for nod in nods:
            output_file.write('{NULL},{NodeType},{GridX},{GridY},{Length},{Width},{Height},{PosX},{PosY},{PosZ}\n'.format(**nod))
            
#test            
if __name__ == "__main__":
    map=PNMImage()
    map.read('nav1.png')  
    GenerateNavmeshCSV(map, 'from_img.csv')
