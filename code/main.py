#!/usr/bin/python
from __future__ import division;

import random
import pymclevel

from pymclevel import faceDirections, FaceXDecreasing, FaceXIncreasing, FaceYDecreasing, FaceYIncreasing, FaceZDecreasing, FaceZIncreasing, MaxDirections

from vectors import Vector

# -- Constants --
vInverse = (-1,-1,-1)
pXIncreasing = Vector(faceDirections[FaceXIncreasing][1])
pXDecreasing = Vector(faceDirections[FaceXDecreasing][1])
pYIncreasing = Vector(faceDirections[FaceYIncreasing][1])
pYDecreasing = Vector(faceDirections[FaceYDecreasing][1])
pZIncreasing = Vector(faceDirections[FaceZIncreasing][1])
pZDecreasing = Vector(faceDirections[FaceZDecreasing][1])
pFaceDirections = ( pXIncreasing, pXDecreasing, pYIncreasing, pYDecreasing, pZIncreasing, pZDecreasing )
 # mapping of block ids to costs
minetime = FreqDict()

# -- Classes --
class FreqDict(dict):
    def __missing__(self,key):
        return 0

# -- Chunk Functions --

def getChunkFromVector(world,vec):
    return world.getChunk(vec.x >> 4, vec.z >> 4)

def getChunkFromXZ(world, x, z):
    return world.getChunk(x >> 4, z >> 4)

def getSubCoords(vec):
    return Vector(vec.x & 15, vec.y, vec.z & 15)

def getBlock(world,vec):
    ch = getChunkFromVector(world,vec)
    ind = getSubCoords(vec)
    return ch.Blocks[ind] + ch.Add[ind]

def setBlock(world,vec,bId):
    ch = getChunkFromVector(world,vec)
    ind = getSubCoords(vec)
    ch.Blocks[ind] = bId & 255
    ch.Add[ind] = (bId >> 8) & 15

# -- Main Functions --

# Construct a Vector set of all the offsets that you need to look at and mine out each step of the shaft.
def constructLookLists(pDiff, pSize):
    look = set()
    shaft = set()
    for dx in range(pSize.x):
        for dy in range(pSize.y):
            for dz in range(pSize.z):
                shaft.add(Vector(dx,dy,dz))
                for dire in faceDirections:
                    look.add(Vector(dx,dy,dz) + dire[1])
    # Remove from look those that are on the axis of the mineshaft (pDiff)
    for i in range(3):
        if pDiff[i]!=0:
            look = [vec if vec[i]==0 else None for vec in look]
    # Reconvert to set, done after looped list comprehensions
    look = set(look)
    # Remove placeholder None object
    look.remove(None)
    # Remove shaft blocks
    look -= shaft
    return look, shaft

def mineShaft(final world, pStart, pDiff, pShaftSize, pStop):
    lpLook, lpShaft = constructLookLists(pDiff, pShaftSize)
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
    blocks_seen = FreqDict()
    blocks_mined = FreqDict()
    time_taken = 0
    
    def mineBlock(pBlock):
        bid = getBlock(world, pBlock)
        if bid == 0: return
        blocks_mined[bid]++
        time_taken += minetime[bid]
        setBlock(world, pBlock, 0)
        # Make sure that sand & gravel are done
        if bid in blocksFalling:
            mineBlock(pBlock + (0,1,0))
    
    def mineVeins(pBlock):
        bId = getBlock(world, pBlock)
        neighbors = []
        for pD in pFaceDirections:
            pTmp = pBlock + pD
            bId2 = getBlock(world, pTmp)
            if bId2 in blocksValuable:
                neighbors.append(pTmp)
        mineBlock(pBlock)
        # Tail recurse
        for pBlock2 in neighbors:
            mineVeins(pBlock2)
        return
    
    print("Starting mining: %s -> %s" % (str(pStart), str(pStop)))
    print("Chunk pos %s,%s -> %s,%s" % (pStart.x >> 4, pStart.z >> 4, pStop.x >> 4, pStop.z >> 4))
    while check_func():
        pCurrent += pDiff
        # Dig the shaft
        for pDelta in lpShaft:
            mineBlock(pCurrent + pDelta)
        # Check the sides, take action if necessary
        for pDelta in lpLook:
            pBlock = pCurrent + pDelta
            bId = getBlock(world,pBlock)
            blocks_seen[bId]++
            if bId in blocksValuable:
                mineVeins(pBlock)
            if bId in blocksLiquid:
                coverLiquid(pBlock)
            if bId in blocksSpecial:
                handleSpecial(world,bId,pBlock)
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

