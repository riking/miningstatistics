import pymclevel
from pymclevel.faces import *
# faceDirections, FaceXIncreasing, FaceXDecreasing, FaceYIncreasing, FaceYDecreasing, FaceZIncreasing, FaceZDecreasing, MaxDirections
from pymclevel.box import BoundingBox, Vector

# -- Constants --
vInverse = (-1,-1,-1)


# -- Run-Once Code --
world = pymclevel.fromFile("/home/kane/projects/miningstatistics/testworld1/world/level.dat")
print world
print world.bounds
print world.chunkCount

# -- Functions --

def getChunkFromVector(world,vec):
    return world.getChunk(vec.x >> 4, vec.z >> 4)

def getChunkFromXZ(world, x, z):
    return world.getChunk(x >> 4, z >> 4)

def mineShaft(world, pStart, pDiff, pShaftSize, pStop):
    chunks = set()
    # List of blocks to check each step
    lpLook = set()
    
    pOrthSides = [i for i in range(3) if pDiff[i] == 0]
    for dx in range(pShaftSize.x):
        for dy in range(pShaftSize.y):
            for dz in range(pShaftSize.z):
                for dire in faceDirections:
                    lpLook.add(Vector(dx,dy,dz) + dire[1])
    lpLook.remove(pDiff)
    lpLook.remove(pDiff * vInverse)
    print(lpLook)
    print(len(lpLook))


pStart = Vector(50,11,100)
tupleDiff = faceDirections[FaceXIncreasing][1]
pDiff = Vector(tupleDiff[0], tupleDiff[1], tupleDiff[2])
mineShaft( world, pStart, pDiff, Vector(1,2,1), pStart + (300,0,0))
