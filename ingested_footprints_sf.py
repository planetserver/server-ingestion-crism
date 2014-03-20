import os
import json
import glob
from shapefile import shapefile

psbaseurl = "http://planetserver.jacobs-university.de/classic/?productid="
sfin_name = "footprints/mars_mro_crism_trdr_frthrlhrs07_c0a.shp"
insf = shapefile("read", sfin_name)

ingested = []
f = open("inrasdaman.txt","r")
frthrlhrs = ["frt","hrl","hrs"]
for line in f:
    line = line.strip()
    if line[:3] in frthrlhrs:
        productid = line[:-5].upper()
        if not productid in ingested:
            ingested.append(productid)

outfieldslist = []
for line in insf.fieldslist:
    outfieldslist.append(line)
outfieldslist.append(['PSURL',4,254,0])
outfieldslist.append(['XMIN',4,20,0])
outfieldslist.append(['XMAX',4,20,0])
outfieldslist.append(['YMIN',4,20,0])
outfieldslist.append(['YMAX',4,20,0])
outfieldslist.append(['WIDTH',4,20,0])
outfieldslist.append(['HEIGHT',4,20,0])

outsf = shapefile("write", sfin_name[:-4] + "_planetserver.shp", insf.type, outfieldslist, insf.projection)
featurelist = insf.feats2list()

for features in featurelist:
    feature = features[0]
    table = features[1]
    pid = table['ProductId']
    if pid in ingested:
        table['PSURL'] = psbaseurl + pid
        metadatajs = glob.glob("metadata/" + pid.lower() + "*.js")[0]
        print pid.lower()
        f = open(metadatajs,"r")
        j = json.load(f)
        table['XMIN'] = j["xmin"]
        table['XMAX'] = j["xmax"]
        table['YMIN'] = j["ymin"]
        table['YMAX'] = j["ymax"]
        table['WIDTH'] = j["width"]
        table['HEIGHT'] = j["height"]
        f.close()
        outsf.createfeatfromlist(feature, table)
outsf.finish()
insf.finish()

os.system('ogr2ogr -select "PSURL" -f KML %s %s' % (sfin_name[:-4] + "_planetserver.kml", sfin_name[:-4] + "_planetserver.shp"))


