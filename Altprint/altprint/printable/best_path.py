import shapely as sp
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

    min_distance = 999  # Initilize as a number bigger enough to fit the next 'if' statement

    for perimeterCoord in RawList_points:

        # Cast to 'Point' Object
        perimeterCoord = sp.Point(perimeterCoord)

        # Calculate the distance
        dist = perimeterCoord.distance(sp.Point(point))

        # Storage only the min. distance
        if dist <= min_distance:
            min_distance = dist
            closestCoord = perimeterCoord

    return closestCoord # POINT object


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
    

#def bestPath_angle_Perimeter2Infill(listAngles)