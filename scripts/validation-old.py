#
# This script make a validation using Fowlkes and Mallow Index
# to verify the clustering algorithm
#
# It compares clusters selecting pair of points
#
# We need a Ground Truth where each point has its classification (A real partition)
#
# In the partition generated by algorithm is the second partition
import os
import sys
import itertools


def showHeader():
    print("Grid Clustering algorithm - Script to validate results")
    print("Developed by Ricardo Brandao: https://github.com/programonauta/grid-clustering")
    print("------------------------------------------------------------------------------")


def showError(msgErr):
    print("Error on script")
    print("---------------")
    print(msgErr)
    exit(1)


def showHelp():
    print("\tOptions\t\tDescription")
    print("\t-h\t\tShow this help")
    print("\t-d <dir>\tDirectory of files")
    print("\t-m <file>\tFile with map of indexes")
    print("\t-t <opt>\t<opt> = c or p (for cells or points respectively)")
    print("\t-pr <pre>\tPrefix of files")
    print("\t\t\t if gGluster pr = (e<epsilon (3 digits)>f<force (with 4 decimals)> - Ex. e014f0.1500)")
    print("\t\t\t if DBSCAN pr = (e<epsilon (4 decimals)>m<minPts (with 3 digits)> - Ex. e0.1100m003)")
    print("\t-b\t\tUse this if you'll validate DBSCAN")
    return

def parseOpt(opt, hasArgument):
    # verify if option is on the arg list
    mat = [i for i, x in enumerate(sys.argv) if x == opt]
    q = len(mat)

    if q == 0:
        return False, ""
    elif q > 1:
        showError("there is more than one " + opt + " option")
    else:
        ind = mat[0]
        arg = ""
        if hasArgument:
            if len(sys.argv) == ind + 1:
                arg = ""
            else:
                arg = sys.argv[ind + 1]
        return True, arg


# Print the header of script
showHeader()

# verify if have any -h option
hasHelp, opt = parseOpt("-h", False)

if (hasHelp > 0):
    showHelp()
    exit(1)

hasPrefix, prefix = parseOpt("-pr", True)

if prefix == "":
    print("--------------------------------")
    print("Prefix of file was not informed!")
    print("Have any doubt? Run this with -h")
    print("--------------------------------")
else:
    prefix = prefix + "-"

isDBSCAN, opt = parseOpt("-b", False)

# verify if directory is defined
hasDir, nameDir = parseOpt("-d", True)

hasMap, mapFile = parseOpt("-m", True)

# replace "\\" by "/". In windows machines uses "\" for subdirectories. Python could handle with / in all OSs.
nameDir = nameDir.replace("\\", "/")

if hasDir:
    if nameDir == "":
        showError("Directory is not informed")
    if not os.path.isdir(nameDir):
        showError(nameDir + " is not a Directory")
    if isDBSCAN:
        dirInput = nameDir + "/central/DBSCAN"
    else:
        dirInput = nameDir + "/central/results"
    if not os.path.isdir(dirInput):
        showError(dirInput + " subdirectory not found")
else:
    showHelp()
    showError("-d option not found")

nameDirAux = nameDir.split('/')
nameSingleDir = nameDirAux[len(nameDirAux) - 1]

hasType, fileType = parseOpt("-t", True)

if hasType:
    if fileType == "":
        showError("File type not informed")
    if fileType != "c" and fileType != "p":
        showError("File type (" + fileType + ") wrong. Enter c or p (cell or point)")
else:
    showError("File type not informed. Please use -t <c> or <p> option")

if prefix[-2:] == "--":
    prefix = prefix[:-1]

if fileType == "c":
    prefix += "cells-"
else:
    prefix += "points-"

if isDBSCAN:
    if (mapFile == ""):
        mapFile = nameDir + "/config/" + prefix + "map-DBSCAN-" + nameSingleDir + ".csv"
    inputFile = dirInput + "/" + prefix + "DBSCAN-" + nameSingleDir + ".csv"
else:
    if (mapFile == ""):
        mapFile = nameDir + "/config/" + prefix + "map-" + nameSingleDir + ".csv"
    inputFile = dirInput + "/" + prefix + "result-" + nameSingleDir + ".csv"

# Create matMap list where there is the correspondence btw cluster number found and the ground truth
fInd = open(mapFile, "r")
matMap = []
for line in fInd:
    CSVLine = line.split(",")
    for i in range(len(CSVLine)):
        CSVLine[i] = int(CSVLine[i])
    matMap.append(CSVLine)

fInd.close()

if isDBSCAN:
    pre = "DBSCAN "
    type = " DBSCAN "
else:
    pre = ""
    type = "gCluster"

print(pre + "Map File read  :" + mapFile)
print(pre + "Input File read:" + inputFile)
print("-----------------------")
print("labels")
print(type+" | Ground Truth")
print("-----------------------")

for l in matMap:
    print("    %4d | %4d" %(l[0],l[1]))


print()
print(pre + "Map File with ", len(matMap), "registers")
input("Please confirm map file")

print("Reading file", inputFile)

fInd = open(inputFile, "r")
#
# matClusters is a list of points
#    and each point has a list that defines the cluster label it belongs on Ground Truth partition (position 0) and
#    gCluster partition (position 1)
#
matClusters = []
first = True
minCells = 0
for line in fInd:
    CSVLine = line.split(",")
    if first:
        if not isDBSCAN and fileType == "c":  # Get the minCells on the header
            headerMinCell = CSVLine[-3].split("-")
            minCells = int(headerMinCell[-1])
        first = False
        continue

    # If reading cells and not DBSCAN, must ignore lines with cells cluster < min cells
    # if not isDBSCAN and fileType == "c":  # Get the minCells on the header
    #     qtyCells = int(CSVLine[-3])
    #     if qtyCells < minCells:
    #         continue

    aux = [int(CSVLine[-2]), int(CSVLine[-1])]
    # Search cluster number int map matrix
    for i in matMap:
        if aux[0] == i[0]:
            aux[0] = i[1]
            break
    matClusters.append(aux)

#
# Process to calculate index
#
# First create a combination of all points in matClusters
#
# for each pair of points, compare the cluster label of point in Ground Truth (position 0) and
#          cluster label of point
#
# Calculate the classification of each pair of points
#
print()
print("ss = same/same = the two points belong in the same cluster on both GT and gCluster")
print("sd = same/different = the points belong in the same cluster on gCluster and diff on GT")
print("ds = different/same = Belong in diff clusters on gCluster and in the same on GT")
print("dd = different/different = the points belong in different clusters on both partitions")

print()

ss = 0
sd = 0
ds = 0
dd = 0

# Now iterate a combination of matClusters

for pairs in itertools.combinations(matClusters, 2):
    # compare clusters on GT
    clGT = (pairs[0][1] == pairs[1][1])  # test clusters on GT
    clgC = (pairs[0][0] == pairs[1][0])  # test clusters no gCluster

    if (clgC and clGT):  # same cluster on gCluster and GT
        ss += 1
    elif (clgC and not clGT):  # same on gCluster and diff on GT
        sd += 1
    elif (not clgC and clGT):  # diff on gCluster and same on GT
        ds += 1
    else:  # diff clusters on both partitions
        dd += 1

m1 = ss + sd
m2 = ss + ds
m = ss + sd + ds + dd

# calculate FM index: ss over the square root of m1 x m2
fm = ss / ( (m1 * m2) ** 0.5 )
rand = (ss + sd) / m
jac = (ss) /  (ss + sd + ds)


print("ss:", ss)
print("sd:", sd)
print("ds:", ds)
print("dd:", dd)
print("-------------")
print("FM:", fm)
print("Rand:", rand)
print("Jaccard:", jac)