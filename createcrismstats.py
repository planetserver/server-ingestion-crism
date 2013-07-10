import os, sys
from osgeo import gdal, ogr
from osgeo.gdalconst import *

def betweenstring(string,a,b):
    list = []
    stringsplit = string.split(a)
    if stringsplit != []:
        for item in stringsplit[1:]:
            nr = item.find(b)
            if nr != -1:
                list.append(item.split(b)[0])
    return list

gdal.AllRegister()

text = '''
For each CRISM .img data in listfile create .js (JSON) containing metadata.

  createcrismstats.py /path/list.txt
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
else:
    filecoll = []
    listfile = sys.argv[1]

f = open(listfile,"r")
for line in f:
    line = line.strip().split(",")
    filename = line[0]
    collname = line[1]
    header = "".join(open(filename + ".hdr", "r").readlines()).replace("\n","")

    wavelength = betweenstring(header, "wavelength = {", "}")[0].replace(" ","").split(",")
    fwhm = betweenstring(header, "fwhm = {", "}")[0].replace(" ","").split(",")
    bbl = betweenstring(header, "bbl = {", "}")[0].replace(" ","").split(",")

    inDs = gdal.Open(filename, GA_ReadOnly)
    bands = inDs.RasterCount

    xmlfile = filename + ".aux.xml"
    if not os.path.exists(xmlfile):
        print "Creating metadata XML file"
        os.system("gdalinfo -stats " + filename + ">/dev/null")
    try:
        xmldata = "".join(open(xmlfile, "r").readlines()).replace("\n","")
        succesbands = betweenstring(xmldata,'band="','"')
        minimum = betweenstring(xmldata,'<MDI key="STATISTICS_MINIMUM">','</MDI>')
        maximum = betweenstring(xmldata,'<MDI key="STATISTICS_MAXIMUM">','</MDI>')
        mean = betweenstring(xmldata,'<MDI key="STATISTICS_MEAN">','</MDI>')
        stddev = betweenstring(xmldata,'<MDI key="STATISTICS_STDDEV">','</MDI>')
    except:
        print "XML stats not created!"
        sys.exit()
    
    print "Writing " + collname + ".js"
    o = open(collname + ".js","w")
    out = "{"
    gdallist = ["minimum","maximum","mean","stddev"]
    for item in gdallist:
        i = 0
        out = out + "\"" + item + "\": ["
        exec("temp = " + item)
        for value in temp:
            if str(i+1) in succesbands:
                out = out + temp[i] + ","
            else:
                out = out + "0,"
            i += 1
        out = out[:-1] + "],"
    hdrlist = ["wavelength","fwhm","bbl"]
    for item in hdrlist:
        i = 0
        out = out + "\"" + item + "\": ["
        exec("temp = " + item)
        for value in temp:
            out = out + temp[i] + ","
            i += 1
        out = out[:-1] + "],"
    out = out[:-1] + "};"
    o.write(out)
    o.close()

f.close()