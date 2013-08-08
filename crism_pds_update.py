import urllib2
import os,sys
import glob
import zipfile

filename = 'crism_pds_update.csv'
f = open(filename, 'r')
line = f.readline().strip().split(",")
url = line[0]
path = os.path.join(os.getcwd(),line[1])
size = int(line[2])
f.close()

req = urllib2.urlopen(url)
CHUNK = 16 * 1024
with open(path, 'wb') as fp:
    while True:
        chunk = req.read(CHUNK)
        if not chunk: break
        fp.write(chunk)

newsize = os.stat(path).st_size
if newsize > size:
    print "new version!"
    for ext in ["dbf","prj","shp","shp.xml","shx"]:
        if os.path.exists(path[:-3] + ext):
            os.unlink(path[:-3] + ext)
    zip = zipfile.ZipFile(path)
    zip.extractall(os.path.dirname(path))
    zip.close()
    os.unlink(path)
    f = open(filename, 'w')
    f.write("%s,%s,%s\n" % (line[0],line[1],newsize))
    f.close()
else:
    os.unlink(path)
