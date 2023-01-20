import pandas as pd
import matplotlib.pyplot as plt
import time
import re
from bng_latlon import OSGB36toWGS84
import math
import numpy as np


# def ConvertNodesToMatrix(NodeSourceURL, LinkSourceURL, OutputURL, StreetReferencesURL):
#     Nodes = pd.read_csv(NodeSourceURL)
#     Links = pd.read_csv(LinkSourceURL)
#     References = pd.read_csv(StreetReferencesURL)
#     Matrix = np.zeros(shape=(Nodes.shape[0],Nodes.shape[0]))
#     # Look through each node in the table of nodes
#     for i in range(0,Nodes.shape[0]):
#             TempNodeID = np.zeros(Nodes.shape[0])
#             # For each node, search through the table of links until that node is found
#             for j in range(0, Links.shape[0]):
#                 coordinates = Links['Centre Line'][j].replace('[', "").replace(']', "").replace("(","").strip().split('),')
#                 StreetName = []
#                 if len(str(Links['Street Name'][j])) != 3:
#                     StreetName = np.where(References['Street Name'] == Links['Street Name'][j])
#                 else:
#                     StreetName = [[-1]] # represents no name
#                 for k in range(0, len(coordinates)):
#                     coordinate = coordinates[k].replace(")", "").split(",")
#                     if (float(coordinate[0]) == Nodes['Lat'][i]) and (float(coordinate[1]) == Nodes['Lon'][i]):
#                         # We have matched the node to its road(s). We now update the links matrix
#
#                         if k==0:
#                             Relation2x = coordinates[k + 1].replace(")", "").split(",")
#                             TempNodeID[Nodes[(float(Relation2x[0]) == Nodes['Lat']) & (float(Relation2x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
#                             #print(Nodes[float(Relation2x[0]) == Nodes['Lat']].index.to_numpy())
#                         elif k==len(coordinates) - 1:
#                             Relation1x = coordinates[k - 1].replace(")", "").split(",")
#                             TempNodeID[Nodes[(float(Relation1x[0]) == Nodes['Lat']) & (float(Relation1x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
#                         else:
#                             Relation1x = coordinates[k-1].replace(")", "").split(",")
#                             TempNodeID[Nodes[(float(Relation1x[0]) == Nodes['Lat']) & (float(Relation1x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
#                             Relation2x = coordinates[k + 1].replace(")", "").split(",")
#                             TempNodeID[Nodes[(float(Relation2x[0]) == Nodes['Lat']) & (float(Relation2x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
#             #print(TempNodeID)
#             Matrix[i, :] = TempNodeID
#
#
#
#
#
#
#     print(Matrix)
#     np.save(OutputURL,Matrix)
#
#
#
# #ConvertNodesToMatrix("HindleyGreenAllNodes.csv", "HindleyGreenLinks.csv","NodeTree", "HindleyGreenStreetReferences.csv")


def ConvertNodesToMatrix(NodeSourceURL, LinkSourceURL, OutputURL, StreetReferencesURL):
    Nodes = pd.read_csv(NodeSourceURL)
    Links = pd.read_csv(LinkSourceURL)
    References = pd.read_csv(StreetReferencesURL)
    Matrix = np.zeros(shape=(Nodes.shape[0],Nodes.shape[0]))
    # Look through each node in the table of nodes
    for i in range(0,Nodes.shape[0]):
            TempNodeID = np.zeros(Nodes.shape[0])
            # For each node, search through the table of links until that node is found
            for j in range(0, Links.shape[0]):
                coordinates = Links['Centre Line'][j].replace('[', "").replace(']', "").replace("(","").strip().split('),')
                StreetName = []
                if len(str(Links['Street Name'][j])) != 3:
                    StreetName = np.where(References['Street Name'] == Links['Street Name'][j])
                else:
                    StreetName = [[-1]] # represents no name
                for k in range(0, len(coordinates)):
                    coordinate = coordinates[k].replace(")", "").split(",")
                    if (float(coordinate[0]) == Nodes['Lat'][i]) and (float(coordinate[1]) == Nodes['Lon'][i]):
                        # We have matched the node to its road(s). We now update the links matrix

                        if k==0:
                            Relation2x = coordinates[k + 1].replace(")", "").split(",")
                            TempNodeID[Nodes[(float(Relation2x[0]) == Nodes['Lat']) & (float(Relation2x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
                            #print(Nodes[float(Relation2x[0]) == Nodes['Lat']].index.to_numpy())
                        elif k==len(coordinates) - 1:
                            Relation1x = coordinates[k - 1].replace(")", "").split(",")
                            TempNodeID[Nodes[(float(Relation1x[0]) == Nodes['Lat']) & (float(Relation1x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
                        else:
                            Relation1x = coordinates[k-1].replace(")", "").split(",")
                            TempNodeID[Nodes[(float(Relation1x[0]) == Nodes['Lat']) & (float(Relation1x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
                            Relation2x = coordinates[k + 1].replace(")", "").split(",")
                            TempNodeID[Nodes[(float(Relation2x[0]) == Nodes['Lat']) & (float(Relation2x[1]) == Nodes['Lon'])].index.to_numpy()] = StreetName[0][0] + 1
            #print(TempNodeID)
            Matrix[i, :] = TempNodeID






    print(Matrix)
    np.save(OutputURL,Matrix)



ConvertNodesToMatrix("HindleyGreenNodes.csv", "HindleyGreenLinks.csv","NodeTree", "HindleyGreenStreetReferences.csv")


def PlotFromNodeTree(SourceURL, NodeSourceURL, LinksSourceURL, SearchStreet = ""):
    Matrix = np.load(SourceURL)
    Nodes = pd.read_csv(NodeSourceURL)
    Links = pd.read_csv(LinksSourceURL)
    # print(Matrix.shape[0])


    for i in range(0,Matrix.shape[0]):
        nodeilon = Nodes['Lon'][i]
        nodeilat = Nodes['Lat'][i]
        links = np.where(Matrix[i,:] != 0)
        # print(links[0])
        # print([nodeilat,nodeilon])
        for link in links[0]:


            linklon = Nodes['Lon'][link]
            linklat = Nodes['Lat'][link]
            name = []
            linksname = []

            #print([str(Nodes['Street Name'][i]), str(Nodes['Street Name'][link])])
            if "[" in str(Nodes['Street Name'][i]):
                name = str(Nodes['Street Name'][i]).replace("[","").replace("]","").split(" ")
                name = [x != "" for x in name]
                name = [int(x) for x in name ]
            else:
                #name.append(int(Nodes['Street Name'][i]))

                c=1

            if "[" in str(Nodes['Street Name'][link]):
                linksname = str(Nodes['Street Name'][link]).replace("[", "").replace("]", "").split(" ")
                linksname = [x != "" for x in linksname]
                linksname = [int(x) for x in linksname]
            else:
                linksname.append(int(Nodes['Street Name'][link]))


            if (SearchStreet in name) and (SearchStreet in linksname):
                print(Nodes['Street Name'][i])
                print(name)
                print(linksname)
                colour = "r-"
                plt.plot([nodeilon, linklon], [nodeilat, linklat], colour, markersize=0.1)
            else:
                colour = "b-"
                plt.plot([nodeilon, linklon], [nodeilat, linklat], colour, markersize=0.1)


    plt.show()

#PlotFromNodeTree("NodeTree.npy","HindleyGreenAllNodes.csv", "HindleyGreenLinks.csv", 1)


