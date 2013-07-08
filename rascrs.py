import os
import sys

text = '''
helper Python script for ps_set_crs.sh

  rascrs.py listfile CRSURL
  
  listfile containing lines of 'filename,collname'
  CRSURL like http://kahlua.eecs.jacobs-university.de:8080/def/crs/PS/0/1/
'''

filecoll = []
try:
    listfile = sys.argv[1]
    crsurl = sys.argv[2]
    f = open(listfile, "r")
    for line in f:
        line = line.strip().split(",")
        filecoll.append([line[0],line[1]])
    f.close()
except:
    print text
    sys.exit()

for item in filecoll:
    file_to_insert = item[0]
    coll_name = item[1]
    os.system("ps_set_crs.sh " + crsurl + " " + coll_name)
