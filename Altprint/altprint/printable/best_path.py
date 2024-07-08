import shapely as sp
from itertools import permutations
#import matplotlib.pyplot as plt
#import geopandas as gpd


def text2Linestring(file):

    fileLines = file.split("\n")

    FirstFileLine = fileLines[0]
    FirstFileLine = FirstFileLine.split("),")
    FirstFileLine = list(map(lambda x: x[2:], FirstFileLine))

    FirstFileLine[0] = FirstFileLine[0][16:]
    FirstFileLine[-1] = FirstFileLine[-1][:-2]

    resultListMultilinestring = []

    for element in FirstFileLine:

        bufferList = []

        for j in range(len(element.split(","))):

            # Print for vizualize each tuple(xy duo) element
            # print(element.split(",")[j].strip())

            # Creating xy point
            p = sp.Point(float(element.split(",")[j].strip().split(" ")[0]), float(
                element.split(",")[j].strip().split(" ")[1]))

            # Insert xy point into bufferlist
            bufferList.append(p)

        # Insert xy point list into linestring list
        resultListMultilinestring.append(sp.LineString(bufferList))

        # Separate by region
        # print("---------")

    SecondFileLine = fileLines[2]
    SecondFileLine = SecondFileLine.split(">, ")
    SecondFileLine = list(map(lambda x: x[13:-1], SecondFileLine))

    SecondFileLine[0] = SecondFileLine[0][1:]
    SecondFileLine[-1] = SecondFileLine[-1][:-2]

    resultListLinestring = []

    for element in SecondFileLine:

        bufferList = []

        for j in range(len(element.split(","))):

            # Print for vizualize each tuple(xy duo) element
            # print(element.split(",")[j].strip())

            # Creating xy point
            p = sp.Point(float(element.split(",")[j].strip().split(" ")[0]), float(
                element.split(",")[j].strip().split(" ")[1]))

            # Insert xy point into bufferlist
            bufferList.append(p)

        # Insert xy point list into linestring list
        resultListLinestring.append(sp.LineString(bufferList))

        # Separate by region
        # print("---------")

    return (resultListMultilinestring, resultListLinestring)


def closestPoint(point, RawList_points):
    #Search for the closest point of Point from the RawList
    #agg_info: agregated info, such as angle for each RawPoint

    min_distance = 999  # Initilize as a number bigger enough to fit the next 'if' statement

    for i in range(len(RawList_points)):


        perimeterCoord = RawList_points[i]
        
        # Cast to 'Point' Object
        perimeterCoord = sp.Point(perimeterCoord)

        # Calculate the distance
        dist = perimeterCoord.distance(sp.Point(point))

        # Storage only the min. distance
        if dist <= min_distance:
            min_distance = dist
            closestCoord = perimeterCoord

    return closestCoord



def RawList_Points(linestring, makeTuple=False):
    # Only if the list is a list of linestrings

    listRaw_Points = []

    for linestr in linestring.coords:
        list_linestr = list(linestr)
        if makeTuple == True:
            listRaw_Points.append(linestr)
    
    if makeTuple == False:
        for coord in list_linestr:
            listRaw_Points.append(coord)

    return listRaw_Points


def RawList_MultiPoints(multilinestring, makeTuple=False):
    # Only if the list is a multilinestring objects

    listRaw_MultiPoints = []
    for i in range(multilinestring.length):
        listRaw_MultiPoints.append(RawList_Points(multilinestring[i], makeTuple=makeTuple))
    
    return listRaw_MultiPoints

def perimeterPath_byPoint(startPoint, rawList_perimeterPoints, clockwise=True):
    #startPoint is a POINT object

    # Get the parimeter path by using the starting point, orientation and perimeter RawList_Points

    # Set index of start point and slice the rawList untill the end of process(firstHalf). Then get the coord. of the end, to search the
    # initial point(SecondHalf) and continue untill reach the startPoint of firstHalf.

    bestPath = []

    if clockwise == True:

        # It needs to be that type of slice because of the existence of the 'skirt' in front of the 'perimeter' coords list.

        startIndex1 = rawList_perimeterPoints.index(list(startPoint.coords)[0])
        firstHalf = rawList_perimeterPoints[startIndex1:]

        startIndex2 = rawList_perimeterPoints.index(firstHalf[-1])
        secondHalf = rawList_perimeterPoints[startIndex2+1:startIndex1+1]

        bestPath = firstHalf + secondHalf

    return bestPath


def bestPath_Infill2Perimeter(list_nextPerimeter, list_infill):
    # Function that returns the best starting point in Perimeter Path, after finish the infill

    # Extracting the last point
    last_pointInfill = sp.Point(list_infill[-1])


    # Algorith to calculate all distances(reference by last infill point) and storage the minimun distance, and the points related.
    closestCoord = closestPoint(last_pointInfill, list_nextPerimeter)

    bestPath = perimeterPath_byPoint(closestCoord, list_nextPerimeter)


    return bestPath


def split_PerimeterPath(PathList, numPerimeters):
    #Split a Path list into a list of lists (each path, e.g perimeter 0, perimeter 1, etc.) (Input: list of tuples (coords.))
    perimeter_byNumber = []
    temp_list = []

    count_2 = 1

    firstCoord = PathList[0]

    for n in range(len(PathList)):
        temp_list.append(PathList[n])
        count_2 += 1

        if (firstCoord == PathList[n]) and (n != 0) and (count_2 > 2):

            perimeter_byNumber.append(temp_list.copy())
            temp_list = []

            count_2 = 1
        
            if n != (len(PathList)-1): #Não esta no final
                firstCoord = PathList[n+1]
    
    if numPerimeters != len(perimeter_byNumber):
        print("Error, numPerimeters != len(perimeter_byNumber) ")
        print("numPerimeters: ", numPerimeters)
        print("lenPathlist: ", len(perimeter_byNumber))
        return -1

    else:
        return perimeter_byNumber


def bestPath_Perimeter2Infill(listPerimeter, listInfill):
    # Search the best startPoint to initiate the Infill.
    # Calculate the distance from the lastPointPerimeter and the pointAlfa_Infill and pointBeta_Infill

    # Then the closestPoint get the priority to start the list of the infill path

    pointAlfa_Infill = sp.Point(listInfill[0])
    pointBeta_Infill = sp.Point(listInfill[-1])

    lastPoint_perimeter = sp.Point(listPerimeter[-1])

    distAlfa = lastPoint_perimeter.distance(pointAlfa_Infill)
    distBeta = lastPoint_perimeter.distance(pointBeta_Infill)

    if distAlfa <= distBeta:
        return listInfill

    else:
        return listInfill[::-1] # Reversed
    
def bestPath_Perimeter2Infill_rotate(List_infill, perimeter_path, List_angles):

    min_dist = 999
    infill_index = 0.5 #just initialize the variable, if its not used it will crash the code

    #Pick the best infill rotation
    for i in range(len(List_infill)):
        infillPath_Rotation = bestPath_Perimeter2Infill(perimeter_path, List_infill[i])

        #Calculate distance for each closest point (by angle rotation)
        startPoint = sp.Point(infillPath_Rotation[0])
        dist = startPoint.distance(sp.Point(perimeter_path[-1]))

        if dist < min_dist:
            min_dist = dist
            infill_index = i

    #Pick the best path from the 2 points(start, end)
    bestInfill = bestPath_Perimeter2Infill(perimeter_path, List_infill[infill_index])

    return bestInfill, i

def searchAndSplit(raw_lists, raw_point):
    #->function that split list by the closest 'reference point', them create 2 lists(main list splitted)

    RefPoint = sp.Point(raw_point)
    min_dist = 9999999
    closest_point = 0
    mainList = []
    Index_counter = 0
    Index_list = 0

    for raw_list in raw_lists: #Find the closest point in a list of lists
        for pt in raw_list:

            pt = sp.Point(pt)

            if pt.distance(RefPoint) <= min_dist:
                min_dist = pt.distance(RefPoint)
                closest_point = pt
                mainList = raw_list
                Index_list = Index_counter
        
        Index_counter += 1
            

    closest_point = list(closest_point.coords)[0]

    list1 = mainList[:mainList.index(closest_point)]
    list2 = mainList[mainList.index(closest_point):]

    raw_lists.pop(Index_list) #Delete the old list that was splitted

    if len(list1) == 1:
        list2.append(list1.pop())
    
    if len(list2) == 1:
        list1.append(list2.pop())


    if list1 != []:
        raw_lists.insert(0, list1)  #Add the splitted vesions in the beggining of the array
    
    if list2 != []:
        raw_lists.insert(0, list2)

    return raw_lists



