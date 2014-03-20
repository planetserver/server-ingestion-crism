import os,sys,glob

def ini(filename):
    dict = {}
    inputini = open(filename,"r")
    for line in inputini:
        line = line.strip()
        if not ";" in line:
            line = line.split(" = ")
            dict[line[0]] = line[1]
    inputini.close()
    return dict

text = '''
Ingest regions of CRISM data into PlanetServer

  crismingest.py -c <region>: create
  crismingest.py -i <region>: ingest
  crismingest.py -f <region>: finalize
  
crismingest.py uses region in crismingest.ini if <region> is omitted.
'''

filecoll = []
if len(sys.argv) == 1:
    print text
    sys.exit()

if sys.argv[1] == "-c":
    do = 1
elif sys.argv[1] == "-i":
    do = 2
elif sys.argv[1] == "-f":
    do = 3
else:
    print text
    sys.exit()

region = ini("crismingest.ini")["region"]
if len(sys.argv) == 3:
    region = sys.argv[2].strip()
datafolder = ini("crismingest.ini")["datafolder"]
crs = ini("crismingest.ini")["crs"]
listfile = os.path.join(datafolder,region,"processed","crismingest.txt")

# Check regions
regions = []
for file in glob.glob("regions/*.shp"):
    file = file[:-4].replace("regions/","")
    if not file in regions:
        regions.append(file)
if region in regions:
    if do == 1:
        print "Create"
        command = 'python createcrismlist.py %s fresh' % (listfile)
        os.system(command)
    elif do == 2:
        command = 'python rasimporter.py -l %s' % (listfile)
        os.system(command)
        
        command = 'python rascheck.py -l %s' % (listfile)
        os.system(command)
    elif do == 3:
        command = 'python createcrismstats.py %s %s' % (listfile,region)
        os.system(command)
        
        command = 'python addcrismmetadata.py %s' % (listfile)
        os.system(command)

        command = 'python ingestlist.py'
        os.system(command)
else:
    print region + ".shp doesn't exist in regions folder"
    sys.exit()
