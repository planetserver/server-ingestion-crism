import os
import sys
from rasdaman import *
rasql = RasQL()
psql = PsQL()

text = '''
helper Python script for raserase

  raseraser.py collection
  OR
  raseraser.py -l listfile (with listfile containing lines of 'filename,collname')
'''

filecoll = []
if len(sys.argv) == 1:
    print text
    sys.exit()
elif sys.argv[1] == "-l":
    try:
        listfile = sys.argv[2]
        f = open(listfile, "r")
        for line in f:
            line = line.strip().split(",")
            filecoll.append([line[0],line[1]])
        f.close()
    except:
        print text
        sys.exit()
else:
    try:
        filecoll.append(["",sys.argv[1]])
    except:
        print text
        sys.exit()

for line in filecoll:
    coll_name = line[1]
    print "Deleting " + coll_name
    #os.system("raserase --coll %s --coverage %s --conn /home/earthserver/.rasdaman/rasconnect" % (coll_name, coll_name))       
    rasql.do('drop collection ' + coll_name)
    psql.do("delete from ps_coverage where name = '%s'" % (coll_name))


