import aioshutil as shutil
import re
import time
import pandas as pd
from bng_latlon import OSGB36toWGS84
from CombineFiles import combine_data,count_lines
import math
import matplotlib.pyplot as plt
# start = time.process_time()
#
# #  --------------------------- SAVE RELEVANT DATA TO CSV FILE!!!!!
#
# #data = "/Users/lukeglover/Downloads/crouch-end/Highways_Roads_Street_FULL_001.gml"
#
#
# data = "./test.txt"  # Contains 97458197 lines
# numofroads = 0
# f = open(data, "r")
#
# lines = f.readlines()
# current_road = 0
# data = []
# street_id = ""
# street_name = ""
# authority_name = ""
# administrative_area = ""
# highway_town = ""
# highway_coordinates = ""
# nodes = []
# links = []
# count = 0
# for i, x in enumerate(lines):
#     if i%1949163 == 0:
#         # We are 1/50 of the way through
#         print(str((i/97458197)*100) + "% done!")
#     if "<os:featureMember>" in str(x):
#         #Set new road
#         numofroads +=1
#         current_road = numofroads
#
#     elif "</os:featureMember>" in str(x):
#         #Update the road
#         if highway_town == "LONDON":
#             data.append([numofroads, street_id, street_name, authority_name, administrative_area, highway_town, count,nodes])
#         nodes = []
#     else:
#         if "<highway:Street" in str(x):
#             street_id = str(x).replace("<highway:Street gml:id=\"","").replace("\">","").strip()
#         elif "<highway:name>" in str(x):
#             street_name = str(x).replace("<highway:name>","").replace("</highway:name>","").strip()
#         elif "<highway:authorityName>"in str(x):
#             authority_name = str(x).replace("<highway:authorityName>", "").replace("</highway:authorityName>", "").strip()
#         elif "<highway:administrativeArea>"in str(x):
#             administrative_area = str(x).replace("<highway:administrativeArea>", "").replace("</highway:administrativeArea>", "").strip()
#         elif "<highway:town>"in str(x):
#             highway_town = str(x).replace("<highway:town>", "").replace("</highway:town>", "").strip()
#         elif "<net:link xlink" in str(x):
#             links.append(str(x).replace("<net:link xlink:href=\"#", "").replace("\"/>", ""))
#
#
#         elif "<gml:posList srsDimension=\"2\"" in str(x):
#             if "LONDON" in highway_town:
#                 highway_coordinates = str(x).replace("<gml:posList srsDimension=\"2\"", "").replace("</gml:posList>", "").strip()
#                 count_str = str(re.findall(r'(count=[\"]\d+)',highway_coordinates)).replace("[\'","").replace("\']","")
#                 count = int(count_str.replace("count=\"","").replace("\'",""))
#                 highway_coordinates = highway_coordinates.replace(str(count_str + "\">") ,"")
#                 highway_coordinates = highway_coordinates.split(' ')
#                 lons = []
#                 lats = []
#                 for i in range(0,int(count)):
#                     lon = float(highway_coordinates[2*i])
#                     lat = float(highway_coordinates[(2 * i)+1])
#                     nodes.append(OSGB36toWGS84(lat, lon))
#
#
# # num_lines = sum(1 for line in f)
#
#
# pd.set_option('display.max_columns', None)
# column_names = ["row number","USRN ID","Street Name","Authority Name","Administrative area","Town","Node count", "Node Locations"]
# dataframe = pd.DataFrame(data,columns = column_names)
# print("Finished processing data. It took this many seconds: ")
# print(time.process_time() - start)
# print(dataframe.head(5))
# print("there are " + str(numofroads) + " roads")
# dataframe.to_csv('test.csv', index=False)
# #
# # print("Finished saving data. It took this many seconds (total): ")
#
#
# #
# # print(time.process_time() - start)
# # #print(OSGB36toWGS84(454224.365,1203078.804))
# # print(OSGB36toWGS84(431178.000,581381.000))
#
#
# StreetData = pd.read_csv("test.csv")
# a = StreetData['Node Locations'][0]
# print(a)
# #a = "529879.604 187801.355 529882.738 187826.865 529883.000 187829.000 529884.257 187835.760 529887.000 187848.000 529894.000 187868.000 529900.730 187889.356 529904.744 187902.093 529918.000 187944.000 529921.000 187956.000 529921.871 187958.365 529928.000 187975.000 529929.263 187978.157 529938.000 188000.000 529941.151 188007.388 529951.719 188032.168 529961.000 188052.000 529963.349 188056.698 529970.500 188070.000 529975.000 188078.000 529999.000 188122.000"
# highway_coordinates = a.split(' ')
# lons = []
# lats = []
# coordinates = a.replace("[","").replace("]","").split("), ")
#
# processed_coordinates_x = []
# processed_coordinates_y = []
#
# for coordinate in coordinates:
#     coordinate = str(coordinate).replace("(","").replace(")","").split(",")
#     processed_coordinates_x.append(float(coordinate[0]))
#     processed_coordinates_y.append(float(coordinate[1]))
# ranges = [0,6,6,21,6,6,10,5]
# index = 2
# plt.xlim([54.619,54.6218])
# plt.ylim([-5.289, -5.280])
# for i in range(1,61):
#     if i == sum(ranges[0:index]):
#
#         plt.plot(processed_coordinates_x[sum(ranges[0:index-1]):sum(ranges[0:index])],processed_coordinates_y[sum(ranges[0:index-1]):sum(ranges[0:index])])
#         plt.show()
#         plt.xlim([54.619, 54.6218])
#         plt.ylim([-5.289, -5.280])
#         index += 1



# plt.plot(processed_coordinates_x, processed_coordinates_y)
# plt.show()

# print(OSGB36toWGS84(529918.000,187944.000))
# print(OSGB36toWGS84(529951.719,188032.168))
# print(OSGB36toWGS84(530025.000,188169.000))
# print(OSGB36toWGS84(530007.427,188137.615))
# print(OSGB36toWGS84(529884.257,187835.760))
# print(OSGB36toWGS84(529904.744,187902.093))
# print(OSGB36toWGS84(529879.604,187801.355))
# print(OSGB36toWGS84(529882.738,187826.865))
# print(OSGB36toWGS84(529975.000,188078.000))
# print(OSGB36toWGS84(529999.000, 188122.000 ))
#
# print(OSGB36toWGS84(364291.000,402889.000))
# print(OSGB36toWGS84(364201.000,402891.000))

#xlink: href = "#osgb1000000219788942" / >
f = "53.5217487 -2.5429600 53.5211492 -2.5414373 53.5208970 -2.5414075 53.5207113 -2.5413145 53.5206813 -2.5410071 53.5206872 -2.5407413 53.5210397 -2.5401369 53.5214474 -2.5400692"

a = "364291.000 402889.000 364287.000 402848.000 364285.000 402842.000 364246.000 402806.000 364244.000 402805.000 364240.000 402804.000 364211.000 402806.000 364210.000 402807.000 364206.000 402811.000 364204.000 402818.000 364201.000 402833.000 364201.000 402853.000 364201.000 402891.000"
highway_coordinates = f.split(' ')
processed_coordinates_x = []
processed_coordinates_y = []
for i in range(0,math.floor(len(highway_coordinates)/2)):
    processed_coordinates_x.append(float(highway_coordinates[2*i]))
    processed_coordinates_y.append(-float(highway_coordinates[(2*i)+1]))


plt.plot(processed_coordinates_y,processed_coordinates_x)
plt.show()
# ranges = [0,6,6,21,6,6,10,5]
# index = 2
# plt.xlim([54.619,54.6218])
# plt.ylim([-5.289, -5.280])
# for i in range(1,61):
#     if i == sum(ranges[0:index]):
#
#         plt.plot(processed_coordinates_x[sum(ranges[0:index-1]):sum(ranges[0:index])],processed_coordinates_y[sum(ranges[0:index-1]):sum(ranges[0:index])])
#         plt.show()
#         plt.xlim([54.619, 54.6218])
#         plt.ylim([-5.289, -5.280])
#         index += 1


