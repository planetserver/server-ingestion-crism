rasdaman_ingestion
==================

# crismingest.py
Run the ingestion of CRISM data according to the information in crismingest.ini

```
crismingest.py [-create]
```

Misc:
* Use -create if the list (createcrismlist.py) and JSON metadata (createcrismstats.py) have not been created yet.
* The ingestion includes:
  * rasimporter.py
  * rascrs.py
  * addcrismmetadata.py

# psproc.txt
This text file is read by createcrismlist.py to determine the collection names of the CRISM data in rasdaman.

# createcrismlist.py
create list of to be ingested CRISM .img data

```
createcrismlist.py /path/list.txt
```

Misc:
* 'list.txt' is created in the /path/ which contains .img data.
* Each line of the listfile is 'filename,collection_name', according to psproc.txt

# createcrismstats.py

For each CRISM /path/name.img in list.txt create /path/name.js (JSON) containing metadata.

```
createcrismstats.py list.txt
```

# addcrismmetadata.py
add CRISM .js JSON metadata to gmlcov:metadata

```
addcrismmetadata.py list.txt
```

# ingestlist.py
create inrasdaman.js with all the collection names ingested in rasdaman. This .js is used by the PlanetServer client.

```
ingestlist inrasdaman.js
```

# rasdaman.py
Usage:
```python
from rasdaman import *
rasql = RasQL()
psql = PsQL()
```

# rasset.py
rasdaman definitions helper Python script

```
rasset.py -make filename setname [null=1]
rasset.py -[add/update] name.def
rasset.py -del name.def
```

Misc:
* null=1 only works for rasdaman enterprise
* -make uses GDAL:

```python
from osgeo import gdal
from osgeo.gdalconst import *
```

# rasimporter.py
helper Python script for rasimport

```
rasimporter.py filename collname
rasimporter.py -l listfile
```
  
Misc:
* listfile containing lines of 'filename,collname'
  
# rascrs.py
helper Python script for ps_set_crs.sh

```
rascrs.py listfile CRSURL
```

Misc:
* listfile containing lines of 'filename,collname'
* CRSURL like http://kahlua.eecs.jacobs-university.de:8080/def/crs/PS/0/1/
  
It uses an altered version of: http://www.earthserver.eu/svn/earthserver/src/ps_set_crs.sh
```
line 33: add correct rasconnect path
lines 104-106: comment out
line 107: add ANS='y'
```

# raseraser.py
helper Python script for raserase

```
raseraser.py listfile
```

Misc:
* listfile containing lines of 'filename,collname'
 
# rassc.py
rasdaman shortcuts

```
rassc.py -l = List all collections in RASBASE
rassc.py -i = Initialize WMS layer: <collName> <layerName>
rassc.py -f = Fill pyramids: <collName>
rassc.py -d = Drop WMS layer: <layerName>
rassc.py -u = Update all WMS to new CRS: <Crs>
rassc.py -c = Compare dataset with collection: <dataset> <collection>
```

Misc:
* For petascope WMS see: http://rasdaman.eecs.jacobs-university.de/trac/rasdaman/wiki/WmsImportTools
