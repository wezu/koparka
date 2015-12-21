import sys, os

def removeTagFromEgg(file_name, tags_to_remove=['<Tangent>', '<Binormal>', '<RGBA>']):
    f = open(file_name,"r+")
    d = f.readlines()
    f.seek(0)
    for i in d:
        tag=i.split()
        if len(tag)>0:
            tag=tag[0]
            if not tag in tags_to_remove:          
                f.write(i)
    f.truncate()
    f.close()        
    

def cookEggs(directory):
    dirList=os.listdir(directory)
    print directory
    for fname in dirList:        
        if os.path.isdir(directory+'/'+fname):  
            cookEggs(directory+'/'+fname)
        if fname[-4:]=='.egg':    
            print fname
            removeTagFromEgg(directory+'/'+fname)                    
    
cookEggs('../models')



