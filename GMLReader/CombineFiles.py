import shutil

#combine_data("/Users/lukeglover/Downloads/full network/Junctions/Highways_Roads_RoadJunction_FULL_", ".gml", 1, "AllRoadJunctions.txt")
#combine_data("/Users/lukeglover/Downloads/full network/RoadLinks/Highways_Roads_RoadLink_FULL_", ".gml", 71, "AllRoadLinks2.txt", first_number=72)
# combine_data("/Users/lukeglover/Downloads/full network/RoadLinks/Highways_Roads_RoadLink_FULL_", ".gml", 71, "AllRoadLinks.txt")
#combine_data("/Users/lukeglover/Downloads/full network/RoadLinks/Highways_Roads_RoadLink_FULL_", ".gml", 142, "AllRoadLinks.txt", first_number=72)
#combine_data("/Volumes/HardDrive/Mapdatta/uncompressed/RoadNodes/Highways_Roads_RoadNode_FULL_", ".gml", 47, "AllRoadNodes.txt")

#print(count_lines("/Users/lukeglover/Downloads/full network/RoadNodes/Highways_Roads_RoadNode_FULL_", ".gml", 47, "AllRoadNodes.txt"))


def combine_data(base_filename, extension, num_of_files, outputname, first_number = 1):
    filenames = []
    for i in range(first_number, first_number + num_of_files):
        print(i)
        filenumber = '{0:03}'.format(i)
        filenames.append(base_filename + str(filenumber) + extension)
    with open(outputname, 'wb') as wfd:
        for f in filenames:
            with open( f, 'rb') as fd:
                shutil.copyfileobj(fd, wfd)
    return


def count_lines(base_filename, extension, num_of_files, output_filename):

    num_of_lines = 0
    for i in range(1, num_of_files + 1):
        filename = base_filename + '{0:03}'.format(i) + extension
        f = open(filename, "r")
        num_of_lines = num_of_lines + len(f.readlines())
        print(str((i / num_of_files)*100) + " percent completed!")

    f = open(output_filename, "r")
    output_num_of_lines = len(f.readlines())

    return [num_of_lines,output_num_of_lines]