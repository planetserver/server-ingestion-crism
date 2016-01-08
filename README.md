rasdaman_ingestion
==================

# 1. pdsode_updates.py
Check if there is a new release of various Mars PDS data on the PDS ODE. If so download footprint shapefile in /footprints folder.

# 2. productids_per_region.py (using arcpy)
Using inrasdaman.txt (made by ingestlist.py) and the ROI polygon shapefiles in the regions folder it will create a list of to be added CRISM data, per region, in the regions folder.

# 3. crism_urllist.py / crism_urllist_size.py
crism_urllist.py uses the LabelURL field in the CRISM TRDR footprint shapefile and goes through the .txt files in the regions folder to create wget -i list files in the download folder.

crism_urllist_size.py on the other hand uses the .CSV in the pdssizes folder as input (made by crism_pds_size.py). 

# 4. Use wget to download

# 5. crismingest.py
Ingest regions of CRISM data into PlanetServer.

```
  crismingest.py -c: create
  crismingest.py -i: ingest
  crismingest.py -f: finalize
```

Misc:
* Use -create first, to make the list (createcrismlist.py) and JSON metadata (createcrismstats.py).
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
add CRISM XML metadata PDS ODE link to gmlcov:metadata

```
addcrismmetadata.py list.txt
```

# ingestlist.py
create inrasdaman.js with all the collection names ingested in rasdaman. This .js is used by the PlanetServer client.

```
ingestlist.py
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
rasset.py -make raster_filename setname [null=1]
rasset.py -[add/update] setname.def
rasset.py -del setname.def
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

# rascheck.py
Check if rasimport went succesful

```
rascheck.py filename collname
rascheck.py -l listfile
```
  
Misc:
* creates rascheck.lst with data which has to be raserased and again rasimported.

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
rassc.py -l = List all collections and their sizes
rassc.py -i = Initialize WMS layer: <collName> <layerName>
rassc.py -f = Fill pyramids: <collName>
rassc.py -d = Drop WMS layer: <layerName>
rassc.py -u = Update all WMS to new CRS: <Crs>
rassc.py -c = Compare dataset with collection: <dataset> <collection>
```

Misc:
* For petascope WMS see: http://rasdaman.eecs.jacobs-university.de/trac/rasdaman/wiki/WmsImportTools

# ingested_footprints_sf.py
This python script reads inrasdaman.txt and /footprints/mars_mro_crism_trdr_frthrlhrs07_c0a.shp (downloaded by crism_pds_update.py). It will create a new shapefile with all the CRISM FRT/HRL/HRS data in PlanetServer. The 'PSURL' field is added which contains a URL of the PlanetServer hyperspectral analysis tool for the specific CRISM data. Also a KML file is created in the /footprints folder which only contains the PSURL link.

# crism_pds_size.py
Determines for each CRISM dataset its size, saved as .CSV in the pdssizes folder.
Needs beautifulsoup (http://www.crummy.com/software/BeautifulSoup/)