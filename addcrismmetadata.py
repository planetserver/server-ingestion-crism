from rasdaman import *
import os, sys
psql = PsQL()

text = '''
add CRISM .js JSON metadata to gmlcov:metadata

  addcrismmetadata.py listfile (containing lines of 'filename,collname')
'''

if len(sys.argv) == 1:
    print text
    sys.exit()
else:
    listfile = sys.argv[1]

# max = 100
f = open(listfile,"r")
for line in f:
    line = line.strip().split(",")
    filename = line[0]
    coll = line[1]
    meta = str(open(filename[:-4] + ".js","r").readline())
    # delete before add
    psql.do("DELETE FROM ps_metadata WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);" % (coll))
    # slice up in pieces
    #splitmeta = [meta[i:i+max] for i in range(0, len(meta), max)]
    # insert first piece
    psql.do("INSERT INTO ps_metadata (coverage, metadata) VALUES ((SELECT id FROM ps_coverage WHERE name=\x27%s\x27), \x27%s\x27);" % (coll, meta)) #splitmeta[0]))
    # append rest of pieces
    # for string in splitmeta[1:]:
        # psql.do("UPDATE ps_metadata SET metadata = ((SELECT metadata FROM ps_metadata WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27)) || \x27%s\x27) WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);" % (coll,string,coll))
f.close()