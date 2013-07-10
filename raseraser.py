import os
import sys

text = '''
helper Python script for raserase

  raseraser.py listfile (with listfile containing lines of 'filename,collname')
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
else:
    listfile = sys.argv[1]

f = open(listfile,"r")
for line in f:
    line = line.strip().split(",")
    coll_name = line[1]
    print "Deleting " + coll_name
    os.system("raserase -coll " + coll_name)       
