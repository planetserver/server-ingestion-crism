import os,sys

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

region = ini("crismingest.ini")["region"]
datafolder = ini("crismingest.ini")["datafolder"]
crs = ini("crismingest.ini")["crs"]
listfile = os.path.join(datafolder,region,"crismingest.txt")

text = '''
Ingest regions of CRISM data into PlanetServer

  crismingest.py -c: create
  crismingest.py -i: ingest
  crismingest.py -f: finalize
  
crismingest.py uses crismingest.ini
'''

filecoll = []
if len(sys.argv) == 1:
    print text
    sys.exit()

if sys.argv[1] == "-c":
    command = 'python createcrismlist.py %s' % (listfile)
    os.system(command)

    command = 'python createcrismstats.py %s %s' % (listfile,region)
    os.system(command)
elif sys.argv[1] == "-i":
    command = 'python rasimporter.py -l %s' % (listfile)
    os.system(command)
    
    command = 'python rascheck.py -l %s' % (listfile)
    os.system(command)
    
    print "Please perform:"
    print "raseraser.py rascheck.lst"
    print "rasimporter.py -l rascheck.lst"
    
elif sys.argv[1] == "-f":
    command = 'python addcrismmetadata.py %s' % (listfile)
    os.system(command)

    command = 'python ingestlist.py'
    os.system(command)
    
    command = 'python rascrs.py %s %s' % (listfile, crs)
    os.system(command)
else:
    print text
    sys.exit()
