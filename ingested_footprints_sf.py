import os
from shapefile import shapefile

psbaseurl = "http://planetserver.jacobs-university.de/?productid="
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

outsf = shapefile("write", sfin_name[:-4] + "_planetserver.shp", insf.type, outfieldslist, insf.projection)
featurelist = insf.feats2list()

for features in featurelist:
    feature = features[0]
    table = features[1]
    pid = table['ProductId']
    if pid in ingested:
        table['PSURL'] = psbaseurl + pid
        outsf.createfeatfromlist(feature, table)
outsf.finish()
insf.finish()

os.system('ogr2ogr -select "PSURL" -f KML %s %s' % (sfin_name[:-4] + "_planetserver.kml", sfin_name[:-4] + "_planetserver.shp"))
