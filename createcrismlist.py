from glob import glob
import os,sys

text = '''
create list of to be ingested CRISM .img data

  createcrismlist.py /path/list.txt <fresh>
  
  'list.txt' is created in the /path/ which contains .img data.
  Each line of the listfile is 'filename,collection_name', according to psproc.txt
  
  Use 'fresh' to not use inrasdaman.txt
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
elif len(sys.argv) == 2:
    listfile = sys.argv[1]
    fresh = 0
elif len(sys.argv) == 3:
    listfile = sys.argv[1]
    if sys.argv[2] == "fresh":
        fresh = 1
    else:
        print text
        sys.exit()
    
# PlanetServer processing version
v = open("psproc.txt","r")
chainversion = int(v.readline().split(",")[0])
proc = {}
for item in v:
    items = item.strip().split(",")
    proc[items[1]] = items[0]
v.close()

# Ingested data
if fresh == 0:
    ingested = []
    f = open("inrasdaman.txt","r")
    frthrlhrs = ["frt","hrl","hrs"]
    for line in f:
        line = line.strip()
        if line[:3] in frthrlhrs:
            productid = line[:-5].lower()
            if not productid in ingested:
                ingested.append(productid)

o = open(listfile, "w")
folder = os.path.dirname(listfile)
for file in glob(os.path.join(folder,"*.img")):
    filesplit = os.path.basename(file).split("_")
    productid = "_".join(filesplit[:4])
    procstring = "_".join(filesplit[4:]).replace(".img","")
    collection = productid + "_" + str(chainversion) + "_" + proc[procstring]
    if fresh == 0:
        if not productid in ingested:
            o.write("%s,%s\n" % (file,collection))
    else:
        o.write("%s,%s\n" % (file,collection))
o.close()
