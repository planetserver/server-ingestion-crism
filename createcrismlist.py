from glob import glob
import os,sys

text = '''
create list of to be ingested CRISM .img data

  createcrismlist.py /path/list.txt
  
  'list.txt' is created in the /path/ which contains .img data.
  Each line of the listfile is 'filename,collection_name', according to psproc.txt
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
else:
    listfile = sys.argv[1]

v = open("psproc.txt","r")
chainversion = int(v.readline().split(",")[0])
proc = {}
for item in v:
    items = item.strip().split(",")
    proc[items[1]] = items[0]
v.close()

o = open(listfile, "w")
folder = os.path.dirname(listfile)
for file in glob(os.path.join(folder,"*.img")):
    filesplit = os.path.basename(file).split("_")
    productid = "_".join(filesplit[:4])
    procstring = "_".join(filesplit[4:]).replace(".img","")
    collection = productid + "_" + str(chainversion) + "_" + proc[procstring]
    o.write("%s,%s\n" % (file,collection))
o.close()
