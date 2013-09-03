from rasdaman import *
import os, sys
psql = PsQL()

text = '''
add CRISM XML metadata from PDS ODE to gmlcov:metadata

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
    collname = line[1]
    #meta = open(os.path.join(os.path.dirname, collname + ".js","r").readline().strip()
    meta = '''&lt;PlanetServerPDSMetadata xmlns:xlink=&quot;http://www.w3.org/1999/xlink&quot; xlink:href=&quot;http://oderest.rsl.wustl.edu/mars/?query=product&amp;results=m&amp;output=XML&amp;pdsid=%s&quot; xlink:type=&quot;simple&quot;/&gt;''' % (collname[:-5].lower())
    # delete before add
    psql.do("DELETE FROM ps_metadata WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);" % (collname))
    # slice up in pieces
    #splitmeta = [meta[i:i+max] for i in range(0, len(meta), max)]
    # insert first piece
    psql.do("INSERT INTO ps_metadata (coverage, metadata) VALUES ((SELECT id FROM ps_coverage WHERE name=\x27%s\x27), \x27%s\x27);" % (collname, meta)) #splitmeta[0]))
    # append rest of pieces
    # for string in splitmeta[1:]:
        # psql.do("UPDATE ps_metadata SET metadata = ((SELECT metadata FROM ps_metadata WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27)) || \x27%s\x27) WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);" % (coll,string,coll))
f.close()