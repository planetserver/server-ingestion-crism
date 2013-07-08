import os, sys
from rasdaman import *
rasql = RasQL()

outfile = sys.argv[1]
f = open(outfile,"w")
out = 'ingested = ["'
list = rasql.out("select r from RAS_COLLECTIONNAMES as r").strip().split("\n")
for line in list[1:]:
    try:
        line = line.split(": ")[1]
        line = line[:-1]
        out = out + line + '","'
    except:
        ""
out = out[:-2] + ']'
f.write(out)
f.close()
