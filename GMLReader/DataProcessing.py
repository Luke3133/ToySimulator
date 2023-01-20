import pandas as pd
import matplotlib.pyplot as plt
import time
import re
from bng_latlon import OSGB36toWGS84
import math
import numpy as np
from bs4 import BeautifulSoup as bs
import os
import subprocess
import pathlib
import sumolib

start = time.process_time()

# Limit file to a specific region
def FilterDataByRegion(SourceUrl, Region, OutputUrl="0"):
    dataframe = pd.read_csv(SourceUrl)
    FilterIndex = dataframe['Administrative area'] == Region
    FilteredData = dataframe[FilterIndex]
    if OutputUrl == "0":
        OutputUrl = Region + ".csv"
    FilteredData.to_csv(OutputUrl)

#FilterDataByRegion("LondonStreets.csv","HARINGEY", "HARINGEY.csv")

def DataToCSV(SourceURl, OutputURL, Town):
    # For a specific area!
    # Contains 97458197 lines
    start = time.process_time()
    numofroads = 0
    f = open(SourceURl, "r")
    lines = f.readlines()
    data = []
    street_id = ""
    street_name = ""
    authority_name = ""
    administrative_area = ""
    highway_town = ""
    highway_coordinates = ""
    nodes = []
    links = []
    count = 0
    for i, x in enumerate(lines):
        if i % 1949163 == 0:
            # We are 1/50 of the way through
            print(str((i / 97458197) * 100) + "% done!")
        if "<os:featureMember>" in str(x):
            # Set new road
            numofroads += 1

        elif "</os:featureMember>" in str(x):
            # Update the road
            if highway_town == str(Town):
                data.append(
                    [numofroads, street_id, street_name, authority_name, administrative_area, highway_town, count,
                     nodes, links])
            nodes = []
            links = []
            street_name = ""
            street_id = ""
            authority_name = ""
            administrative_area = ""
            highway_town = ""
            count = 0
        else:
            if "<highway:Street" in str(x):
                street_id = str(x).replace("<highway:Street gml:id=\"", "").replace("\">", "").strip()
            elif "<highway:name>" in str(x):
                street_name = str(x).replace("<highway:name>", "").replace("</highway:name>", "").strip()
            elif "<highway:authorityName>" in str(x):
                authority_name = str(x).replace("<highway:authorityName>", "").replace("</highway:authorityName>",
                                                                                       "").strip()
            elif "<highway:administrativeArea>" in str(x):
                administrative_area = str(x).replace("<highway:administrativeArea>", "").replace(
                    "</highway:administrativeArea>", "").strip()
            elif "<highway:town>" in str(x):
                highway_town = str(x).replace("<highway:town>", "").replace("</highway:town>", "").strip()
            elif "<net:link xlink" in str(x):
                links.append(str(x).replace("<net:link xlink:href=\"#", "").replace("\"/>", "").strip())
            elif "<gml:posList srsDimension=\"2\"" in str(x):
                if str(Town) in highway_town:
                    highway_coordinates = str(x).replace("<gml:posList srsDimension=\"2\"", "").replace(
                        "</gml:posList>", "").strip()
                    count_str = str(re.findall(r'(count=[\"]\d+)', highway_coordinates)).replace("[\'", "").replace(
                        "\']", "")
                    count = int(count_str.replace("count=\"", "").replace("\'", ""))
                    highway_coordinates = highway_coordinates.replace(str(count_str + "\">"), "")
                    highway_coordinates = highway_coordinates.split(' ')
                    for i in range(0, int(count)):
                        lon = float(highway_coordinates[2 * i])
                        lat = float(highway_coordinates[(2 * i) + 1])
                        nodes.append(OSGB36toWGS84(lat, lon))

    pd.set_option('display.max_columns', None)
    column_names = ["row number", "USRN ID", "Street Name", "Authority Name", "Administrative area", "Town",
                    "NodeCount", "Node Locations", "Links"]
    dataframe = pd.DataFrame(data, columns=column_names)
    print("Finished processing data. It took this many seconds: ")
    print(time.process_time() - start)
    print(dataframe.head(5))
    print("there are " + str(numofroads) + " roads")
    dataframe.to_csv(OutputURL, index=False)


#DataToCSV("AllStreets.txt",'HaringeyStreets.csv', 'LONDON')


def RoadLinksToCSV(SourceURL, OutputURL):
    # TODO: Add road classification to link file
    # TODO: Merge for loops
    # SourceURL - Street csv
    # Assume we have 2 road link files
    start = time.process_time()
    # Get road links
    links = []
    StreetData = pd.read_csv(SourceURL)
    for i in range(0, StreetData.shape[0]):
        row = StreetData['Links'][i].replace("\"", "").replace("'", "").split(",")
        for j in range(0, len(row)):
            links.append(row[j].replace("[", "").replace("]", "").replace("\\n", "").strip())

        # links = row[6]
    print(links)
    numoflinks = len(links)
    counter = 0
    print(numoflinks)
    file1name = "AllRoadLinks.txt"
    file2name = "AllRoadLinks2.txt"
    # f = open(file1name, "r")
    # lines = f.readlines()
    linkcount = 0
    UsefulLink = False
    data = []
    link_id = ""
    StartNode = ""
    EndNode = ""
    RoadName = ""
    SegmentLength = 0
    RoadWidth = [0, 0]
    CentreLine = []
    print("Starting scan")

    with open(file1name) as infile:
        print("File Opened")
        for line in infile:
            if "<highway:RoadLink" in str(line):
                # Check if its useful to us

                if str(str(line).replace("<highway:RoadLink gml:id=\"", "").replace("\">", "").strip()) in links:
                    # Set new road

                    link_id = str(str(line).replace("<highway:RoadLink gml:id=\"", "").replace("\">", "").strip())
                    UsefulLink = True
                    links.remove(link_id)
                    counter += 1
                    if counter%math.floor(numoflinks/100) == 0:
                        print(str((counter/numoflinks)*100) + "% complete")
                else:
                    UsefulLink = False
                    continue

            elif ("</highway:RoadLink>" in str(line)) and (UsefulLink == True):
                UsefulLink = False
                # Update the road
                row = [link_id, StartNode, EndNode, RoadName, SegmentLength, RoadWidth, CentreLine]
                #print(row)
                data.append(row)

                link_id = ""
                StartNode = ""
                EndNode = ""
                RoadName = ""
                SegmentLength = 0
                RoadWidth = [0, 0]
                CentreLine = []
            elif UsefulLink == True:
                if "<net:endNode" in str(line):
                    EndNode = str(line).replace("<net:endNode xlink:href=\"", "").replace("\">", "").strip()
                    print(EndNode)

                elif "<net:startNode" in str(line):
                    StartNode = str(line).replace("<net:startNode xlink:href=\"", "").replace("\">", "").strip()

                elif "<highway:roadName>" in str(line):
                    RoadName = str(line).replace("<highway:roadName>", "").replace("</highway:roadName>", "").strip()

                elif "<highway:length uom=\"m\">" in str(line):
                    SegmentLength = float(str(line).replace("<highway:length uom=\"m\">", "")
                                          .replace("</highway:length>", "").strip())

                elif "<highway:averageWidth uom=\"m\">" in str(line):
                    RoadWidth[0] = float(str(line).replace("<highway:averageWidth uom=\"m\">", "")
                                         .replace("</highway:averageWidth>", "").strip())

                elif "<highway:minimumWidth uom=\"m\">" in str(line):
                    RoadWidth[1] = float(str(line).replace("<highway:minimumWidth uom=\"m\">", "")
                                         .replace("</highway:minimumWidth>", "").strip())

                elif "<gml:posList srsDimension=\"3\"" in str(line):

                    highway_coordinates = str(line).replace("<gml:posList srsDimension=\"3\"", "").replace(
                        "</gml:posList>", "").strip()
                    count_str = str(re.findall(r'(count=[\"]\d+)', highway_coordinates)).replace("[\'", "").replace(
                        "\']", "")

                    count = int(count_str.replace("count=\"", "").replace("\'", ""))
                    highway_coordinates = highway_coordinates.replace(str(count_str + "\">"), "")
                    highway_coordinates = highway_coordinates.split(' ')

                    for i in range(0, int(count)):
                        lat = float(highway_coordinates[3 * i])
                        lon = float(highway_coordinates[(3 * i) + 1])
                        CentreLine.append(OSGB36toWGS84(lat, lon))


    print("Links cleared = " + str(numoflinks - len(links)))
    print("Remaining links = " + str(len(links)))
    print(str(time.process_time() - start) + " seconds since start!")

    with open(file2name) as infile:
        print("File Opened")
        for line in infile:
            if "<highway:RoadLink" in str(line):
                # Check if its useful to us
                if str(str(line).replace("<highway:RoadLink gml:id=\"", "").replace("\">", "").strip()) in links:
                    # Set new road
                    link_id = str(str(line).replace("<highway:RoadLink gml:id=\"", "").replace("\">", "").strip())
                    UsefulLink = True
                    links.remove(link_id)
                    counter += 1
                    if counter % math.floor(numoflinks / 100) == 0:
                        print(str((counter / numoflinks) * 100) + "% complete")
                else:
                    UsefulLink = False
                    continue

            elif ("</highway:RoadLink>" in str(line)) and (UsefulLink == True):
                UsefulLink = False
                # Update the road
                row = [link_id, StartNode, EndNode, RoadName, SegmentLength, RoadWidth, CentreLine]
                #print(row)
                data.append(row)

                link_id = ""
                StartNode = ""
                EndNode = ""
                RoadName = ""
                SegmentLength = 0
                RoadWidth = [0, 0]
                CentreLine = []
            elif UsefulLink == True:
                if "<net:endNode" in str(line):
                    EndNode = str(line).replace("<net:endNode xlink:href=\"", "").replace("\">", "").strip()

                elif "<net:startNode" in str(line):
                    StartNode = str(line).replace("<net:startNode xlink:href=\"", "").replace("\">", "").strip()

                elif "<highway:roadName>" in str(line):
                    RoadName = str(line).replace("<highway:roadName>", "").replace("</highway:roadName>", "").strip()

                elif "<highway:length uom=\"m\">" in str(line):
                    SegmentLength = float(str(line).replace("<highway:length uom=\"m\">", "")
                                          .replace("</highway:length>", "").strip())

                elif "<highway:averageWidth uom=\"m\">" in str(line):
                    RoadWidth[0] = float(str(line).replace("<highway:averageWidth uom=\"m\">", "")
                                         .replace("</highway:averageWidth>", "").strip())

                elif "<highway:minimumWidth uom=\"m\">" in str(line):
                    RoadWidth[1] = float(str(line).replace("<highway:minimumWidth uom=\"m\">", "")
                                         .replace("</highway:minimumWidth>", "").strip())

                elif "<gml:posList srsDimension=\"3\"" in str(line):

                    highway_coordinates = str(line).replace("<gml:posList srsDimension=\"3\"", "").replace(
                        "</gml:posList>", "").strip()
                    count_str = str(re.findall(r'(count=[\"]\d+)', highway_coordinates)).replace("[\'", "").replace(
                        "\']", "")

                    count = int(count_str.replace("count=\"", "").replace("\'", ""))
                    highway_coordinates = highway_coordinates.replace(str(count_str + "\">"), "")
                    highway_coordinates = highway_coordinates.split(' ')

                    for i in range(0, int(count)):
                        lat = float(highway_coordinates[3 * i])
                        lon = float(highway_coordinates[(3 * i) + 1])
                        CentreLine.append(OSGB36toWGS84(lat, lon))


    column_names = ["Link ID", "Start Node", "End Node","Street Name", "Segment Length", "Road width", "Centre Line"]
    dataframe = pd.DataFrame(data, columns=column_names)
    print("Finished processing data. It took this many seconds: ")
    print(time.process_time() - start)
    dataframe.to_csv(OutputURL, index=False)

#RoadLinksToCSV("LondonStreets.csv", "LondonStreetLinks.csv")

#RoadLinksToCSV("AllHindleyGreenStreets.csv", "HindleyGreenLinks.csv")
#RoadLinksToCSV("Haringey.csv", "HaringeyStreetLinks.csv")

def PlotRoadLinksFromCentreLine(SourceURL):
    #[link_id, StartNode, EndNode, RoadName, SegmentLength, RoadWidth, CentreLine]
    RoadLinks = pd.read_csv(SourceURL)
    for i in range(0, RoadLinks.shape[0]):
        coordinates = RoadLinks['Centre Line'][i].replace('[',"").replace(']',"").replace("(","").strip().split('),')
        processed_coordinates_x = []
        processed_coordinates_y = []
        for j in range(0,len(coordinates)):
            coordinate = coordinates[j].replace(")","").split(",")
            processed_coordinates_x.append(float(coordinate[1]))
            processed_coordinates_y.append(float(coordinate[0]))
        colour_variable = "b"
        width = RoadLinks['Road width'][i].replace("[","").replace("]","").split(",")
        if float(width[0]) >= 9.5:
            colour_variable = "b"
        else:
            colour_variable = "b"
        plt.plot(processed_coordinates_x,processed_coordinates_y, markersize=0.1,color = colour_variable)
    plt.xlim([-0.14,-0.1])
    plt.ylim([51.57, 51.59])
    plt.show()

#PlotRoadLinksFromCentreLine("HindleyGreenLinks.csv")
#PlotRoadLinksFromCentreLine("HaringeyStreetLinks.csv")
#PlotRoadLinksFromCentreLine("test2.csv")

def ConvertLinksToNodes(SourceURL, OutputURL, StreetReferenceURL):
    Links = pd.read_csv(SourceURL)
    Nodes = np.zeros(shape=(1, 5), dtype=object)
    Nodes[0, 4] = np.array([0])
    SecondaryNodeCounter = 0
    StreetIDCounter = 1
    Df = []
    for i in range(0, Links.shape[0]):
        # For each link
        StartNode = Links['Start Node'][i].strip("\"/>")
        EndNode = Links['End Node'][i].strip("\"/>")
        PathNodes = Links['Centre Line'][i].split("),")

        StreetName = StreetIDCounter
        StreetData = np.array([StreetName, str(Links['Street Name'][i]).strip()])
        # Check if we have seen this street before and if not, add it to the StreetReferences table/assign it a StreetID
        # Produce a table Df with nrows = number of unique streets and columns ["Street ID", "Street Name"]
        if StreetIDCounter == 1:
            # Its the first street so just add it to the Df
            Df = np.append(Df, StreetData)
            StreetIDCounter += 1
        else:
            if StreetIDCounter == 2:
                # Its the second street so first check if its a new street then convert the Df to a table
                if Df[1] != str(Links['Street Name'][i]):
                    Df = np.vstack((Df, StreetData))
                    StreetIDCounter += 1
            else:
                #
                search = np.where(Df[:, 1] == str(Links['Street Name'][i]).strip())
                if np.any(search):
                    # Street already in StreetReferences table
                    StreetName = int(search[0][0]) + 1
                else:
                    # Not found in current table so its a new street, add it to new row
                    Df = np.vstack((Df, StreetData))
                    StreetIDCounter += 1

        # For this particular Road link, search through each set of centre line coordinates and convert the end points
        # To primary nodes and any midpoints (halfway down a simple street with no junctions) to secondary nodes.
        # Table columns = [NodeID, Lat, Lon, Type, StreetName]
        for j in range(0, len(PathNodes)):
            Coordinates = PathNodes[j].replace("[", "").replace("]", "").replace("(", "").replace(")", "").split(",")
            if j == 0:
                # This is the first set of coordinates and is a Primary node (Junction between other roads)
                match = -1
                # Check if this node is already in the list under a different street name (For example, did we already
                # add the node when working with the other street in this intersection)
                for k in range(0, np.shape(Nodes)[0]):
                    if str(Nodes[k, 0]) == StartNode and float(Nodes[k, 1]) == float(Coordinates[0]) and float(
                            Nodes[k, 2]) == float(Coordinates[1]) and int(Nodes[k, 3]) == 0:
                        # We found a match on row k i.e. Node k.
                        match = k
                if match == -1:
                    # There are no matches to this node in the current list of nodes so we can just append to the table
                    Nodes = np.vstack(
                        [Nodes, np.array([StartNode, float(Coordinates[0]), float(Coordinates[1]), 0, [StreetName]])])
                else:
                    # The node already exists in the table i.e. Table columns = [NodeID, Lat, Lon, Type] match. We need
                    # to see if [StreetName] also matches i.e. is it a fully duplicate node
                    if StreetName not in Nodes[match, 4]:
                        Nodes[match, 4] = np.append(Nodes[match, 4], StreetName)

            elif j == len(PathNodes) - 1:
                # This is the last set of coordinates and is a Primary node (Junction between other roads)
                match = -1
                for k in range(0, np.shape(Nodes)[0]):
                    if str(Nodes[k, 0]) == EndNode and float(Nodes[k, 1]) == float(Coordinates[0]) and float(
                            Nodes[k, 2]) == float(Coordinates[1]) and int(Nodes[k, 3]) == 0:
                        match = k
                if match == -1:
                    # Not in there so we can just add it
                    Nodes = np.vstack(
                        [Nodes, np.array([EndNode, float(Coordinates[0]), float(Coordinates[1]), 0, [StreetName]])])
                else:
                    if StreetName not in Nodes[match, 4]:
                        Nodes[match, 4] = np.append(Nodes[match, 4], StreetName)

            else:
                # This is a secondary node and is only used to allow for bends in existing roads
                # print("New end node")

                if [Links['Link ID'][i], StartNode + str(SecondaryNodeCounter), Coordinates[0], Coordinates[1], 1] in Nodes[:, 0:4].tolist():
                    # Same street id
                    if [Links['Link ID'][i], StartNode + str(SecondaryNodeCounter), float(Coordinates[0]), float(Coordinates[1]), 1, StreetName] not in Nodes[:, 0:5]:
                        # We have the same node with a different street ID
                        print(np.where(Nodes[:, 0:4] == [EndNode, float(Coordinates[0]), float(Coordinates[1]), 0]))

                else:
                    Nodes = np.vstack(
                        [Nodes, np.array(
                            ["#oseg" + StartNode[5:-len(str(SecondaryNodeCounter))] + str(SecondaryNodeCounter),
                             float(Coordinates[0]), float(Coordinates[1]), 1, StreetName])])
                    # print(Nodes)
                    SecondaryNodeCounter += 1

    Columns = ["NodeID", "Lat", "Lon", "Type", "Street Name"]
    Nodes = np.delete(Nodes, 0, axis=0)
    NodesList = pd.DataFrame(Nodes, columns=Columns, dtype=object)
    # print(pd.to_numeric(NodesList['Lon']))
    plt.plot(pd.to_numeric(NodesList['Lon']), pd.to_numeric(NodesList['Lat']), "s", markersize=2)
    plt.show()

    NodesList.to_csv(OutputURL, index=False)
    Df = pd.DataFrame(Df, columns=['ID', 'Street Name'])
    print(Df.head(5))
    Df.to_csv(StreetReferenceURL, index=False)

#ConvertLinksToNodes("HaringeyStreetLinks.csv", "HaringeyNodes.csv", "HaringeyStreetReferences.csv")
#ConvertLinksToNodes("HindleyGreenLinks.csv", "HindleyGreenAllNodes.csv", "HindleyGreenStreetReferences.csv")
# print("Finished processing data. It took this many seconds: ")
# print(time.process_time() - start)

def ConvertNodesToMatrix(NodeSourceURL, LinkSourceURL, OutputURL, StreetReferenceURL):
    # Uses the list of nodes and list of links (with centre lines) to create a matrix which denotes which nodes join.
    # The value of a matrix at join = id of the street and 0 otherwise.
    Nodes = pd.read_csv(NodeSourceURL)
    Links = pd.read_csv(LinkSourceURL)
    StreetReferences = pd.read_csv(StreetReferenceURL)
    Matrix = np.zeros(shape=(Nodes.shape[0],Nodes.shape[0]))
    for i in range(0, Links.shape[0]):
        # For every link in the links file iterate through its coordinates
        coordinates = Links['Centre Line'][i].replace('[', "").replace(']', "").replace("(", "").strip().split('),')

        # Get Street Name (reference to it)
        Streetnamelocation = np.where(StreetReferences['Street Name'] == str(Links['Street Name'][i]))
        StreetID = np.zeros(shape=(1,1))
        if not np.any(Streetnamelocation):
            StreetID[0][0] = -5
        else:
            StreetID = StreetReferences['ID'][Streetnamelocation[0][0]]
        for j in range(0, len(coordinates)):
            # For each coordinate in the centre line, add the link to the links matrix.
            coordinate = coordinates[j].replace(")", "").split(",")
            location = np.where((float(coordinate[0]) == Nodes['Lat']) & (float(coordinate[1]) == Nodes['Lon']))

            if j == 0:
                # We have the first coordinate
                # i.e. link only to next coordinate and not previous
                NextCoordinate = coordinates[j + 1].replace(")", "").split(",")
                NextCoordinateLocation = np.where((float(NextCoordinate[0]) == Nodes['Lat']) & (float(NextCoordinate[1]) == Nodes['Lon']))
                Matrix[location[0][0],NextCoordinateLocation[0][0]] = StreetID

            elif j == len(coordinates) - 1:
                # We have the last coordinate
                # i.e. link only to previous coordinate and not next
                PreviousCoordinate = coordinates[j - 1].replace(")", "").split(",")
                PreviousCoordinateLocation = np.where((float(PreviousCoordinate[0]) == Nodes['Lat']) & (float(PreviousCoordinate[1]) == Nodes['Lon']))
                Matrix[location[0][0], PreviousCoordinateLocation[0][0]] = -StreetID

            else:
                # We have a middle coordinate
                # i.e. link only to previous and next coordinate
                PreviousCoordinate = coordinates[j - 1].replace(")", "").split(",")
                PreviousCoordinateLocation = np.where((float(PreviousCoordinate[0]) == Nodes['Lat']) & (float(PreviousCoordinate[1]) == Nodes['Lon']))
                NextCoordinate = coordinates[j + 1].replace(")", "").split(",")
                NextCoordinateLocation = np.where((float(NextCoordinate[0]) == Nodes['Lat']) & (float(NextCoordinate[1]) == Nodes['Lon']))
                Matrix[location[0][0], NextCoordinateLocation[0][0]] = StreetID
                Matrix[location[0][0], PreviousCoordinateLocation[0][0]] = StreetID

    print(Matrix)
    np.save(OutputURL,Matrix)



ConvertNodesToMatrix("HindleyGreenAllNodes.csv", "HindleyGreenLinks.csv","NodeTree","HindleyGreenStreetReferences.csv")
#ConvertNodesToMatrix("HaringeyNodes.csv", "HaringeyStreetLinks.csv","HaringeyNodeTree","HaringeyStreetReferences.csv")

# print("Finished processing data. It took this many seconds: ")
# print(time.process_time() - start)

def PlotFromNodeTree(SourceURL, NodeSourceURL, LinksSourceURL, SearchStreet = -5):
    # Plot each node and its connections
    Matrix = np.load(SourceURL)
    Nodes = pd.read_csv(NodeSourceURL)
    #Links = pd.read_csv(LinksSourceURL)
    # print(Matrix.shape[0])

    for i in range(0,Matrix.shape[0]):
        nodeilon = Nodes['Lon'][i]
        nodeilat = Nodes['Lat'][i]
        links = np.where(Matrix[i,:] != 0)
        for link in links[0]:
            linklon = Nodes['Lon'][link]
            linklat = Nodes['Lat'][link]
            if Matrix[i,link] == SearchStreet:

            #if ((Nodes['Street Name'][i] == SearchStreet) and (Nodes['Street Name'][link] == SearchStreet)):
                colour = "r-"
                plt.plot([nodeilon, linklon], [nodeilat, linklat], colour, markersize=0.1)
            else:
                colour = "b-"
                plt.plot([nodeilon, linklon], [nodeilat, linklat], colour, markersize=0.1)


    plt.show()

#PlotFromNodeTree("NodeTree.npy","HindleyGreenAllNodes.csv", "HindleyGreenLinks.csv", 24)
#PlotFromNodeTree("HaringeyNodeTree.npy","HaringeyNodes.csv", "HaringeyStreetLinks.csv", 504)


def convertMatrixToSUMO(InputMatrix, InputNodesSource, OutputName):
    # First we create the SUMO nodes file
    FileContent = ""
    FileContent = FileContent + "<nodes> \n"

    Nodes = pd.read_csv(InputNodesSource)
    min_x = np.min(Nodes['Lon'])
    max_x = np.max(Nodes['Lon'])
    min_y = np.min(Nodes['Lat'])
    max_y = np.max(Nodes['Lat'])


    i = 0
    for row in Nodes.iterrows():
        x = (row[1][2] - min_x) * 50000
        y = (row[1][1] - min_y) * 50000
        FileContent = FileContent + "<node id=\"" + str(i) + "\" x=\"" + str(x) + "\" y=\"" + str(y) + "\" />\n"
        i+=1
    print(FileContent)
    FileContent = FileContent + "</nodes>"
    NodesOutputName = OutputName + ".nod.xml"
    with open(NodesOutputName,'w') as f:
        f.write(FileContent)

    # Next, we create the sumo edg file

    FileContent = ""
    FileContent = FileContent + "<edges> \n"
    networkMatrix = np.load(InputMatrix)
    print(networkMatrix)
    k=0
    for i in range(0,networkMatrix.shape[0]):
        # For each row
        for j in range(0,networkMatrix.shape[1]):
            # scan through each column until we find a 1
            if networkMatrix[i,j] != 0:
                # We have an edge here
                FileContent = FileContent + "<edge from=\"" + str(i) + "\" id=\"" + str(k) + "\" to=\"" + str(j) + "\" />\n"
                k+=1

    FileContent = FileContent + "</edges>"
    EdgesOutputName = OutputName + ".edg.xml"
    with open(EdgesOutputName,'w') as f:
        f.write(FileContent)

#convertMatrixToSUMO("./NodeTree.npy", "./HindleyGreenAllNodes.csv", "HindleyNetwork")


def CreateSumoNetworkFromFiles(NodesFile,EdgesFile,OutputFile):
    print("Creating .net.xml file at " + OutputFile + " using " + NodesFile + " and " + EdgesFile)
    subprocess.run(["netconvert", "--node-files=" + NodesFile,"--edge-files=" + EdgesFile, "--output-file=" + OutputFile + ".net.xml"])
    print("done")
    print("Creating trips file")
    subprocess.call(["randomTrips.py", "--net-file=" + OutputFile + ".net.xml", "-e 600", "--output-trip-file=" + OutputFile + ".trips.xml"], shell=True)
    print("done")
    print("Creating Routes file")
    subprocess.call(["duarouter", "--net-file=" + OutputFile + ".net.xml", "--route-files=" + OutputFile + ".trips.xml", "--output-file=" + OutputFile + ".rou.xml"], shell=True)
    print("done")
    print("Creating Configuration file")
    ConfigFile = "<?xml version=\"1.0\" encoding=\"iso-8859-1\"?>\n"
    ConfigFile = ConfigFile + "\n"
    ConfigFile = ConfigFile + "<configuration xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=\"http://sumo.sf.net/xsd/sumoConfiguration.xsd\">\n"
    ConfigFile = ConfigFile + "\n"
    ConfigFile = ConfigFile + "<input>\n"
    ConfigFile = ConfigFile + "<net-file value=\"" + OutputFile + ".net.xml\"/>\n"
    ConfigFile = ConfigFile + "<route-files value=\"" + OutputFile + ".rou.xml\"/>\n"
    ConfigFile = ConfigFile + "</input>\n"
    ConfigFile = ConfigFile + "\n"
    ConfigFile = ConfigFile + "<time>\n"
    ConfigFile = ConfigFile + "<begin value=\"0\"/>\n"
    ConfigFile = ConfigFile + "<end value=\"1000\"/>\n"
    ConfigFile = ConfigFile + "</time>\n"
    ConfigFile = ConfigFile + "\n"
    ConfigFile = ConfigFile + "</configuration>"

    with open(OutputFile + ".sumocfg",'w') as f:
        f.write(ConfigFile)
    print("done")

#CreateSumoNetworkFromFiles("./HindleyNetwork.nod.xml", "./HindleyNetwork.edg.xml", "HindleyNetwork")
print("Finished processing data. It took this many seconds: ")
print(time.process_time() - start)
