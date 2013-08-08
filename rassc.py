from osgeo import gdal
from osgeo.gdalconst import *
import os
import sys
from rasdaman import *

wmsutilpath = '/home/earthserver/rasdaman/applications/rasgeo/wms-import/utilities/'
crs = "EPSG:4326"

text = '''
rasdaman shortcuts

  rassc.py -l = List all collections in RASBASE
  rassc.py -i = Initialize WMS layer: <collName> <layerName>
  rassc.py -f = Fill pyramids: <collName>
  rassc.py -d = Drop WMS layer: <layerName>
  rassc.py -u = Update all WMS to new CRS: <Crs>
  rassc.py -c = Compare dataset with collection: <dataset> <collection>
'''
        
if len(sys.argv) == 1:
    print text
    sys.exit()
choice = sys.argv[1]

# initiate rasdaman and petascope
rasql = RasQL()
psql = PsQL()

if choice == "-l":
    out = rasql.out("select r from RAS_COLLECTIONNAMES as r")
    colls = []
    out = out.split('  Result object ')
    for line in out[1:]:
        try:
            line = line.split(':')[1]
            line = line.split('\n')[0]
            colls.append(line.strip()[:-1])
        except:
            ""
    for coll in colls:
        query = 'select dbinfo(c) from %s as c' % (coll)
        size = rasql.out(query)
        size = size.split('totalSize": "')[1].split('",')[0]
        print coll,size
if choice == "-i":
    collname = sys.argv[2]
    layername = sys.argv[3]
    command = "%sinit_wms.sh %s %s %s" %(wmsutilpath, layername, collname, crs)
    print command
    os.system(command)
if choice == "-f":
    collname = sys.argv[2]
    command = "%sfill_pyramid.sh %s" %(wmsutilpath, collname)
    print command
    os.system(command)
if choice == "-d":
    layername = sys.argv[2]
    command = "%sdrop_wms.sh %s" %(wmsutilpath, layername)
    print command
    os.system(command)
if choice == "-u":
    crscode = sys.argv[2]
    psql.do("UPDATE ps_layers SET srs=\x27%s\x27;" % (crscode))
if choice == "-c":
    dataset = sys.argv[2]
    collection = sys.argv[3]
    inDs = gdal.Open(dataset, GA_ReadOnly)
    print rasql.checkcoll(collection, inDs.RasterXSize, inDs.RasterYSize)