import os, sys
from rasdaman import *
rasql = RasQL()

f = open("inrasdaman.js","w")
g = open("inrasdaman.txt","w")
out = 'inrasdaman = ["'
list = rasql.out("select r from RAS_COLLECTIONNAMES as r").strip().split("\n")
for line in list[1:]:
    try:
        line = line.split(": ")[1]
        line = line[:-1]
        out = out + line + '","'
        g.write("%s\n" % (line))
    except:
        ""
out = out[:-2] + ']'
f.write(out)
g.close()
f.close()
