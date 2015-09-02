import sys, os

def egg2pz(directory):
    dirList=os.listdir(directory)
    print directory
    for fname in dirList:        
        if os.path.isdir(directory+'/'+fname):  
            egg2pz(directory+'/'+fname)
        if fname[-4:]=='.egg':            
            os.system('pzip '+directory+'/'+fname)
    
egg2pz('../models')

