from osgeo import gdal
from osgeo.gdalconst import *
import os,sys
import subprocess
from rasdaman import *
rasql = RasQL()

text = '''
helper Python script for rasimport

  rasimporter.py filename collname
  OR
  rasimporter.py -l listfile (with listfile containing lines of 'filename,collname')
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

ingested = []
f = open("inrasdaman.txt","r")
for line in f:
    coll_name = line.strip()
    if not coll_name in ingested:
        ingested.append(coll_name)

for item in filecoll:
    file_to_insert = item[0]
    coll_name = item[1]
      
    if not coll_name in ingested:
        # gdal
        inDs = gdal.Open(file_to_insert, GA_ReadOnly)

        if inDs.RasterCount == 3:
            # assuming 3 x 8-bit rasters
            datatype = "RGBImage:RGBSet"
        elif inDs.RasterCount == 1:
            if inDs.GetRasterBand(1).DataType == 1:
                datatype = "GreyImage:GreySet"
            elif inDs.GetRasterBand(1).DataType == 3:
                datatype = "ShortImage:ShortSet"
            elif inDs.GetRasterBand(1).DataType == 6:
                datatype = "FloatImage:FloatSet"
            else:
                print "Unsupported data type: " + str(inDs.GetRasterBand(1).DataType)
                print "Please use rasset.py to add data type"
                sys.exit()
        else:
            if inDs.RasterCount == 107:
                datatype = "CRISMVNIRImage:CRISMVNIRSet"
            elif inDs.RasterCount == 438:
                datatype = "CRISMhhhIRImage:CRISMIRSet"
            elif inDs.RasterCount == 72:
                datatype = "CRISMMRDRImage:CRISMMRDRSet"
            else:
                print "Unsupported data type, please use rasset.py to add data type"
                sys.exit()
        
        print "Using: " + datatype
        print "Adding " + file_to_insert + " to rasdaman as " + coll_name
        command = "rasimport -f %s -t %s -coll %s -conn /home/earthserver/rasconnect>/dev/null" % (file_to_insert, datatype, coll_name)
        #output = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()[0]
        os.system(command)
        #if "ERROR - rimport::main, l. 1467: RasManager Error: Write transaction in progress, please retry again later." in output or "ERROR - rimport::main, l. 1467: RasManager Error: System overloaded, please try again later" in output:
        #    print "Please wait a few minutes and start again"
        #    sys.exit()
    else:
        print "%s already exists." % (coll_name)

