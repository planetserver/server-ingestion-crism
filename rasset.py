import os
import sys

text = '''
rasdaman definitions helper Python script

  Make Image/Set: rasset.py -make filename setname [null=1]
  Add/Update Image/Set: rasset.py -[add/update] name.def
  Delete Image/Set: rasset.py -del name.def
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
if sys.argv[1] == "-make":
    try:
        from osgeo import gdal
        from osgeo.gdalconst import *
    except:
        print "Please install GDAL and the GDAL python bindings!"
        sys.exit()
    
    file_to_insert = sys.argv[2]
    setname = sys.argv[3]
    try:
        null = sys.argv[4]
    except:
        null = "0"

    inDs = gdal.Open(file_to_insert, GA_ReadOnly)
    nrbands = inDs.RasterCount
    datatype = inDs.GetRasterBand(1).DataType
    if null == "1":
        nodata_value = int(inDs.GetRasterBand(1).GetNoDataValue()) # NODATA only supported by Rasdaman Enterprise
    inDs = None

    if datatype == 1:
        data_type = "char"
    elif datatype == 3:
        data_type = "short"
    elif datatype == 6:
        data_type = "float"
    else:
        print "data type: " + str(datatype)
        sys.exit()

    bands = ""
    for i in range(1,nrbands + 1):
       bands = bands + "band" + str(i) + ","
    bands = bands[:-1]
    f = open(setname.lower() + ".def", "w")
    if null == "1":
        f.write("struct " + setname + "Pixel { " + data_type + " " + bands + "; };")
        f.write("typedef marray <" + setname + "Pixel,2> " + setname + "Image;")
        f.write("typedef set<" + setname + "Image> ")
        f.write("null values [" + str(nodata_value) + "] ") # NODATA only supported by Rasdaman Enterprise
        f.write(setname + "Set;")
    else:
        f.write("struct " + setname + "Pixel { " + data_type + " " + bands + "; };")
        f.write("typedef marray <" + setname + "Pixel,2> " + setname + "Image;")
        f.write("typedef set<" + setname + "Image> " + setname + "Set;")
    f.close()
elif sys.argv[1] == "-add":
    deffile = sys.argv[2]
    setname = deffile[:-4]
    check = os.popen("rasdl --print | grep " + setname).readlines()
    if not setname in check:
        print "Adding .def"
        os.system("rasdl -r " + setname.lower() + ".def -i --connect RASBASE")
    else:
        print "Already there, please use -update"
elif sys.argv[1] == "-update":
    deffile = sys.argv[2]
    setname = deffile[:-4]
    check = os.popen("rasdl --print | grep " + setname).readlines()
    if not setname in check:
        print "Adding .def"
        os.system("rasdl -r " + setname.lower() + ".def -i --connect RASBASE")
    else:
        print "Updating .def"
        os.system("rasdl --delmddtype " + setname.strip() + "Image --connect RASBASE")
        os.system("rasdl --delsettype " + setname.strip() + "Set --connect RASBASE")
        os.system("rasdl --delbasetype " + setname.strip() + "Pixel --connect RASBASE")
        os.system("rasdl -r " + setname.lower() + ".def -i --connect RASBASE")
elif sys.argv[1] == "-del":
    setname = sys.argv[2]
    os.system("rasdl --delmddtype " + setname.strip() + "Image --connect RASBASE")
    os.system("rasdl --delsettype " + setname.strip() + "Set --connect RASBASE")
    os.system("rasdl --delbasetype " + setname.strip() + "Pixel --connect RASBASE")
else:
    print text
