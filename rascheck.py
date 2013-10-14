from osgeo import gdal
from osgeo.gdalconst import *
import os
import sys
from rasdaman import *
rasql = RasQL()

text = '''
Check if rasimport went succesfully

  rascheck.py filename collname
  OR
  rascheck.py -l listfile (with listfile containing lines of 'filename,collname')
'''

filecoll = []
if len(sys.argv) == 1:
    print text
    sys.exit()
elif sys.argv[1] == "-l":
    try:
        listfile = sys.argv[2]
        f = open(listfile, "r")
        for line in f:
            line = line.strip().split(",")
            filecoll.append([line[0],line[1]])
        f.close()
    except:
        print text
        sys.exit()
else:
    try:
        filecoll.append([sys.argv[1],sys.argv[2]])
    except:
        print text
        sys.exit()

f = open("rascheck.lst","w")        
for item in filecoll:
    file_to_insert = item[0]
    coll_name = item[1]
      
    # gdal
    inDs = gdal.Open(file_to_insert, GA_ReadOnly)

    # --- insert image data --
    error = rasql.checkcoll(coll_name, inDs.RasterXSize, inDs.RasterYSize)
    if error != 1:
        print "Error occured (%s), writing to rascheck.lst: %s,%s" % (error, file_to_insert, coll_name)
        f.write("%s,%s\n" % (file_to_insert, coll_name))
    else:
        print "Collection %s has correct size." % (coll_name)

f.close()
