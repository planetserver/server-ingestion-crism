rasdaman_ingestion
==================

#### rasdaman.py ####
Usage:
'''python
from rasdaman import *
rasql = RasQL()
psql = PsQL()
'''

#### rasset.py ####
rasdaman definitions helper Python script

  Make Image/Set: rasset.py -make filename setname [null=1]
  Add/Update Image/Set: rasset.py -[add/update] name.def
  Delete Image/Set: rasset.py -del name.def

null=1 only works for rasdaman enterprise
-make uses GDAL:
'''python
from osgeo import gdal
from osgeo.gdalconst import *
'''

#### rasimporter.py ####
helper Python script for rasimport

rasimporter.py filename collname
OR
rasimporter.py -l listfile (with listfile containing lines of 'filename,collname')
  
#### rascrs.py ####
helper Python script for ps_set_crs.sh

rascrs.py listfile CRSURL
  
listfile containing lines of 'filename,collname'
CRSURL like http://kahlua.eecs.jacobs-university.de:8080/def/crs/PS/0/1/
  
It uses an altered version of: http://www.earthserver.eu/svn/earthserver/src/ps_set_crs.sh
line 33: add correct rasconnect path
lines 104-106: comment out
line 107: add ANS='y'

#### rasdelete.py ####
rasdaman delete

rasdelete.py collection_name

#### rassc.py ####
rasdaman shortcuts

rassc.py -l = List all collections in RASBASE
rassc.py -i = Initialize WMS layer: <collName> <layerName>
rassc.py -f = Fill pyramids: <collName>
rassc.py -d = Drop WMS layer: <layerName>
rassc.py -u = Update all WMS to new CRS: <Crs>
rassc.py -c = Compare dataset with collection: <dataset> <collection>

For petascope WMS see: http://rasdaman.eecs.jacobs-university.de/trac/rasdaman/wiki/WmsImportTools
