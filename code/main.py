#!/usr/bin/python
from __future__ import division;

import random
import pymclevel

from pymclevel import faceDirections, FaceXDecreasing, FaceXIncreasing, FaceYDecreasing, FaceYIncreasing, FaceZDecreasing, FaceZIncreasing, MaxDirections

from vectors import Vector

# -- Constants --
vInverse = (-1,-1,-1)
pXIncreasing = faceDirections[FaceXIncreasing][1]
pXDecreasing = faceDirections[FaceXDecreasing][1]
pYIncreasing = faceDirections[FaceYIncreasing][1]
pYDecreasing = faceDirections[FaceYDecreasing][1]
pZIncreasing = faceDirections[FaceZIncreasing][1]
pZDecreasing = faceDirections[FaceZDecreasing][1]

# -- Classes --
class FreqDict(dict):
    def __missing__(self,key):
        return 0

# -- Functions --

def getChunkFromVector(world,vec):
    return world.getChunk(vec.x >> 4, vec.z >> 4)

def getChunkFromXZ(world, x, z):
    return world.getChunk(x >> 4, z >> 4)

def getSubCoords(vec):
    return Vector(vec.x & 15, vec.y, vec.z & 15)

def getBlock(world,vec):
    return getChunkFromVector(world,vec).Blocks[getSubCoords(vec)]
    
def constructLookList(pDiff, pSize):
    ret = set()
    for dx in range(pSize.x):
        for dy in range(pSize.y):
            for dz in range(pSize.z):
                for dire in faceDirections:
                    ret.add(Vector(dx,dy,dz) + dire[1])
    # Remove squares from consideration that are on the axis of pDiff
    for i in range(3):
        if pDiff[i]!=0:
            ret = [vec if vec[i]==0 else None for vec in ret]
    ret = set(ret)
    ret.remove(None)
    return ret

def mineShaft(world, pStart, pDiff, pShaftSize, pStop):
    lpLook = constructLookList(pDiff, pShaftSize)
    pCurrent = Vector(pStart.x, pStart.y, pStart.z)
    
    # Dynamically reduced while-loop condition
    def check_1x():
        return pCurrent.x != pStop.x
    def check_1z():
        return pCurrent.z != pStop.z
    def check_all():
        if (pDiff.x > 0 and pCurrent.x > pStop.x) or (pDiff.x < 0 and pCurrent.x < pStop.x) \
        or (pDiff.y > 0 and pCurrent.y > pStop.y) or (pDiff.y < 0 and pCurrent.y < pStop.y) \
        or (pDiff.z > 0 and pCurrent.z > pStop.z) or (pDiff.z < 0 and pCurrent.z < pStop.z):
            return False
        return True
    check_func = check_all
    if pDiff == pXIncreasing or pDiff == pXDecreasing:
        check_func = check_1x
    if pDiff == pZIncreasing or pDiff == pZDecreasing:
        check_func = check_1z
    
    print("Starting mining: %s -> %s" % (str(pStart), str(pStop)))
    print("Chunk pos %s,%s -> %s,%s" % (pStart.x >> 4, pStart.z >> 4, pStop.x >> 4, pStop.z >> 4))
    blocks_seen = FreqDict()
    while check_func():
        pCurrent += pDiff
        for pDelta in lpLook:
            blocks_seen[getBlock(world,pCurrent + pDelta)] += 1
    print(pCurrent)
    print(blocks_seen)
        

def startTesting(world):
    # TODO: Assign starting based on world bbox
    bounds = world.bounds
    for cx in range(bounds.mincx-1, bounds.maxcx+1):
        print(cx)
        s = ""
        for cz in range(bounds.mincz-1, bounds.maxcz+1):
            if world.containsChunk(cx,cz):
                s += "+"
            else:
                s += "."
        print(s)
    selBounds = bounds.expand(bounds.width // -4, 0, bounds.length // -4)
    pStart = None
    bDir = random.random() < 0.5
    if bDir:
        # Mine along X-Axis
        pStart = Vector(selBounds.minx, 10, random.randint(selBounds.minz+2, selBounds.maxz-2))
        pStop = Vector(selBounds.maxx, pStart.y, pStart.z)
        print(pStart,pStop)
        mineShaft( world, pStart, pXIncreasing, Vector(1,2,1), pStop)
    else:
        # Mine along Z-Axis
        pStart = Vector(random.randint(selBounds.minz+2, selBounds.maxz-2), 10, selBounds.minz)
        pStop = Vector(pStart.x, pStart.y, selBounds.maxz)
        print(pStart,pStop)
        mineShaft( world, pStart, pZIncreasing, Vector(1,2,1), pStop)

def main():
    world = pymclevel.fromFile("/home/kane/projects/miningstatistics/testworld1/world/level.dat", readonly = True)
    print world
    print world.bounds
    startTesting(world)
    
if __name__ == "__main__":
    main()

