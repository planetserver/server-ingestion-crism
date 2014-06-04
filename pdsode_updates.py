import urllib2
import os,sys
import glob
import zipfile

filename = 'pdsode_updates.csv'
f = open(filename, 'r')
datasets = []
for line in f:
    line = line.strip().split(",")
    datasets.append(line)
f.close()

if not os.path.exists("footprints"):
    os.makedirs("footprints")

updated = []
path = os.path.join(os.getcwd(), 'footprints')
for dataset in datasets:
    url = dataset[0]
    size = int(dataset[1])
    zip = os.path.join(path, os.path.basename(url))
    
    print "downloading: " + os.path.basename(url)
    req = urllib2.urlopen(url)
    CHUNK = 16 * 1024
    with open(zip, 'wb') as fp:
        while True:
            chunk = req.read(CHUNK)
            if not chunk: break
            fp.write(chunk)

    newsize = os.stat(zip).st_size
    if newsize > size:
        print "  New release!"
        print "  Updating: " + os.path.basename(url)[:-4]
        for ext in ["dbf","prj","shp","shp.xml","shx"]:
            if os.path.exists(zip[:-3] + ext):
                os.unlink(zip[:-3] + ext)
        z = zipfile.ZipFile(zip)
        z.extractall(path)
        z.close()
        os.unlink(zip)
    else:
        os.unlink(zip)
    updated.append("%s,%s\n" % (url,newsize))
    
f = open(filename, 'w')
for line in updated:
    f.write(line)
f.close()