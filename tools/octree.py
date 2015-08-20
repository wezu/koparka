#!/usr/bin/python
"""
                             _                 
                            | |               
  ___  __ _  __ _  ___   ___| |_ _ __ ___  ___
 / _ \/ _` |/ _` |/ _ \ / __| __| '__/ _ \/ _ \
|  __/ (_| | (_| | (_) | (__| |_| | |  __/  __/
 \___|\__, |\__, |\___/ \___|\__|_|  \___|\___|
       __/ | __/ | by treeform, modified by lethe
      |___/ |___/                                                             
                             
This is a replacement of raytaller wonderful
Egg Octree script many people had problem using it
(I always guessed wrong about the size of cells.)
and it generated many "empty" branches which this
one does not. 
original see : http://panda3d.org/phpbb2/viewtopic.php?t=2502
This script like the original also released under the WTFPL license.
Usage: egg-octreefy [args] [-o outfile.egg] infile.egg [infile.egg...] 
-h     display this
-v     verbose
-l     list resulting egg file
-n     number of triangles per leaf (default 512, 3 if -c)
-r     maximum recursion depth (default 4, 32 if -c)
-c     prepares the output for collision use rather than rendering
if outfile is not specified "infile"-octree.egg assumed
"""

import sys, getopt
import math
from pandac.PandaModules import *


global verbose, listResultingEgg, maxNumber, maxRec, prepCollide

verbose = False
listResultingEgg = False
maxNumber = -1
maxRec = -1
prepCollide = False


def getCenter(polywrapList):
  """Given a list of PolyWrap-s this calculates their centre (mean), as their centre is the mean of their vertices this is a weighted average of the vertices. (When faces are not triangulated, un-weighted if they are.)"""
  # Loop on the PolyWrap-s to determine the meany...
  center = Point3D(0,0,0)
  for pw in polywrapList:
    center += pw.center
  
  num = len(polywrapList)
  if num>0: center /= float(num)
  
  return center


def flatten(thing):
  """ get nested tuple structure like quadrents and flatten it """
  if type(thing) == tuple:
    for element in thing:
      for thing in flatten(element):
        yield thing
  else:
    yield thing


def splitIntoQuadrants(polywrapList,center):
  """ put all poly wraps into quadrents """
  quadrants = ((([],[]),
                ([],[])),
               (([],[]),
                ([],[])))
  for pw in polywrapList:
    pwPos = pw.center
    x =  pwPos[0] > center[0]
    y =  pwPos[1] > center[1]
    z =  pwPos[2] > center[2]
    quadrants[x][y][z].append(pw)
  quadrants = flatten(quadrants)
  return quadrants


class Polywrap:
  """
  Simple wrapper for a polygon that also stores the
  polygons vertex mean, so that it does not have
  to be recomputed
  """
  polygon = None
  center = None

  def __str__(self):
    """ Some visualization to aid debugging """
    return str(self.polygon.getNumVertices())+":"+str(self.center)


def genPolyWraps(group):
  """ generate a list of polywraps from a group of polygons, which could be in sub-groups """
  for polygon in iterGroupChildren(group):
    if type(polygon) == EggPolygon:
      center = Vec3D()
      num = 0
      for vtx in iterVertexes(polygon):
        center += vtx.getPos3()
        num += 1
      if num>0: center /= float(num)
      
      pw = Polywrap()
      pw.polygon = polygon
      pw.center = center
      yield pw


def buildOctree(group):
    """ build an octree form a egg group """
    global verbose, prepCollide
    if prepCollide: group.triangulatePolygons(0xff)
    polywraps = [i for i in genPolyWraps(group)]
    if verbose: print len(polywraps),"polygons"
    
    center = getCenter(polywraps)
    quadrants = splitIntoQuadrants(polywraps,center)
    
    eg = EggGroup('octree-root')
    for node in recr(quadrants):
        eg.addChild(node)
    return eg


def recr(quadrants,indent = 1):
  """
  visit each quadrent and create octree there
  all the end consolidate all octrees into egg groups
  """
  global verbose, maxNumber, maxRec, prepCollide
  qs = [i for i in quadrants]
  if verbose: print "  "*indent,"8 quadrents have ",[len(i) for i in qs]," polygons"
  
  for i, quadrent in enumerate(qs):
    if len(quadrent) == 0:
      if verbose: print "  "*indent," no polygons in quadrent"
      continue
    elif (len(quadrent) <= maxNumber) or (indent >= maxRec):
      center = getCenter(quadrent)
      if verbose: print "  "*indent," triangle center", center, len(quadrent)
      eg = EggGroup('leaf %i-%i (%i tri)'%(indent,i,len(quadrent)))
      if prepCollide: eg.addObjectType('barrier')
      for pw in quadrent:
        eg.addChild(pw.polygon)
      if eg.getFirstChild : yield eg
    else:
      eg = EggGroup('branch-%i-%i (%i tri)'%(indent,i,len(quadrent)))
      center = getCenter(quadrent)
      for node in recr(splitIntoQuadrants(quadrent,center),indent + 1):
        eg.addChild(node)
      if eg.getFirstChild : yield eg


def iterChildren(eggNode):
  """ iterate all children of a node """
  try:
    child = eggNode.getFirstChild()
    while child:
      yield child
      child = eggNode.getNextChild()
  except:
    pass


def iterGroupChildren(eggNode):
  """ iterate all children of groups under a node that are not themselves groups"""
  for child in iterChildren(eggNode):
    if type(child) == EggGroup:
      for i in iterGroupChildren(child):
        yield i
    else:
      yield child


def iterVertexes(eggNode):
  """ iterate all vertexes of polygon or polylist """
  try:
    index = eggNode.getHighestIndex()
    for i in xrange(index+1):
      yield eggNode.getVertex(i)
  except:
    index = eggNode.getNumVertices()
    for i in xrange(index):
      yield eggNode.getVertex(i)
    pass


def eggLs(eggNode,indent=0):
  """ list whats in our egg """
  if eggNode.__class__.__name__ != "EggPolygon":
    print " "*indent+eggNode.__class__.__name__+" "+eggNode.getName()
    for eggChildren in iterChildren(eggNode):
      eggLs(eggChildren,indent+1)


def eggStripTexture(eggNode):
  """ strip textures and materials """
  if eggNode.__class__ == EggPolygon:
    eggNode.clearTexture()
    eggNode.clearMaterial()
  else:
    for eggChildren in iterChildren(eggNode):
      eggStripTexture(eggChildren)


def octreefy(infile,outfile):
  """
  octreefy infile and write to outfile
  using the buildOctree functions
  """
  global verbose, maxNumber, maxRec, prepCollide
  egg = EggData()
  egg.read(Filename(infile))
  if prepCollide: eggStripTexture(egg)
  group = egg
  vertexPool = False
  comment = None
  if verbose:
    print 'Input:'
    eggLs(egg)

  # find the fist group and find the first vertexPool
  # you might have to mess with this if your egg files
  # are in odd format
  for child in iterChildren(egg):
    if type(child) == EggVertexPool:
      vertexPool = child
    if type(child) == EggGroup:
      group = child
    if type(child) == EggComment:
      comment = child

  # if we have not found the vertexPool it must be inside
  if not vertexPool:
    for child in iterChildren(group):
      if type(child) == EggVertexPool:
        vertexPool = child

  if vertexPool and group:
    ed = EggData()

    # More the textures and materials from the old egg file if needed - this wrecks the old file...
    if not prepCollide:
      for child in iterChildren(egg):
        if type(child) in [EggMaterial,EggTexture]:
          ed.addChild(child)

    ed.setCoordinateSystem(egg.getCoordinateSystem())

    com = 'File has been octree-ed (-n %i -r %i%s)'%(maxNumber,maxRec,['',' -c'][prepCollide])
    if comment:
      ed.addChild(EggComment('',com+'; '+comment.getComment()))
    else:
      ed.addChild(EggComment('',com))
    
    ed.addChild(vertexPool)
    ed.addChild(buildOctree(group))
    if listResultingEgg: eggLs(ed)
    ed.writeEgg(Filename(outfile))
  else:
    print 'Could not find vertexPool or group'


def main():
  """ interface to our egg octreefier """
  try:
    optlist, list = getopt.getopt(sys.argv[1:], 'hlvo:n:r:c')
  except Exception,e:
    print e
    sys.exit(0)

  global verbose, listResultingEgg, maxNumber, maxRec, prepCollide
  outfile = False
  for opt in optlist:
    if opt[0] == '-h':
      print __doc__
      sys.exit(0)
    if opt[0] == '-l':
      listResultingEgg = True
    if opt[0] == '-v':
      verbose = True
    if opt[0] == '-n':
      maxNumber = int(opt[1])
    if opt[0] == '-r':
      maxRec = int(opt[1])
    if opt[0] == '-c':
      prepCollide = True
    if opt[0] == '-o':
      outfile = opt[1]
  if outfile and len(list) > 1:
        print "error can have an outfile and more then one infile"
        sys.exit(0)

  if maxNumber==-1:
    if prepCollide: maxNumber = 3
    else: maxNumber = 512
  if maxRec==-1:
    if prepCollide: maxRec = 32
    else: maxRec = 4

  for file in list:
    if '.egg' in file:
      if verbose: print "processing",file
      if outfile:
        octreefy(file,outfile)
      else:
        octreefy(file,file.replace(".egg","-octree.egg"))


if __name__ == "__main__":
  #import os
  main()
