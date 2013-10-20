import os
import glob
import arcpy


inrasdaman = []
try:
    f = open("inrasdaman.txt","r")
    for line in f:
        line = line.strip()
        inrasdaman.append(line[:-5])
    f.close()
except:
    "no ingest yet"

arcpy.env.workspace = os.getcwd()
arcpy.env.overwriteOutput = True
selection_type = 'intersect'

footprintfile = 'footprints/mars_mro_crism_trdr_frthrlhrs07_c0a.shp'
arcpy.MakeFeatureLayer_management(footprintfile, 'footprints')

for regionfile in glob.glob('regions/*.shp'):
    region = os.path.basename(regionfile)[:-4]
    print region
    o = open('regions/' + region + '.txt','w')
    arcpy.MakeFeatureLayer_management(regionfile, region)
    arcpy.SelectLayerByAttribute_management(region, 'NEW_SELECTION', '"FID" = 0')
    arcpy.SelectLayerByLocation_management('footprints', selection_type, region)
    selected = arcpy.SearchCursor('footprints')
    for select in selected:
        if not select.ProductId.lower() in inrasdaman:
            o.write('%s\n' % (select.ProductId))
    o.close()

