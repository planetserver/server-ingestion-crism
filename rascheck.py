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

# Get latest list of ingested collections
list = rasql.out("select r from RAS_COLLECTIONNAMES as r").strip().split("\n")
ingested = []
for line in list[1:]:
    try:
        line = line.split(": ")[1]
        line = line[:-1]
        ingested.append(line)
    except:
        ""

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

ingest = 0
reingest = 0
for item in filecoll:
    file_to_insert = item[0]
    coll_name = item[1]
    if not coll_name in ingested:
        if ingest == 0:
            f = open("rascheck_ingest.lst","w")
            ingest = 1
        print "Collection has not been ingested yet: %s" % (coll_name)
        f.write("%s,%s\n" % (file_to_insert, coll_name))
    else:
        # gdal
        inDs = gdal.Open(file_to_insert, GA_ReadOnly)

        # --- insert image data --
        error = rasql.checkcoll(coll_name, inDs.RasterXSize, inDs.RasterYSize)
        if error != 1:
            if reingest == 0:
                g = open("rascheck_reingest.lst","w")
                reingest = 1
            print "Collection was ingested wrongly (%s): %s" % (error, coll_name)
            g.write("%s,%s\n" % (file_to_insert, coll_name))

if ingest == 1:
    print "Something went wrong, please perform:"
    print "  python rasimporter.py -l rascheck_ingest.lst"
    f.close()
if reingest == 1:
    print "Something went wrong, please perform:"
    print "  python raseraser.py rascheck_reingest.lst"
    print "  python rasimporter.py -l rascheck_reingest.lst"
    g.close()
