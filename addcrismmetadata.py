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
    print "Adding: " + collname
    #meta = open(os.path.join(os.path.dirname, collname + ".js","r").readline().strip()
    #meta = '''&lt;gmlcov:Extension&gt;&lt;PlanetServerPDSMetadata xmlns:xlink=&quot;http://www.w3.org/1999/xlink&quot; xlink:href=&quot;http://oderest.rsl.wustl.edu/live/?query=product&amp;results=m&amp;output=XML&amp;pdsid=%s&quot; xlink:type=&quot;simple&quot;/&gt;&lt;/gmlcov:Extension&gt;''' % (collname[:-5].lower())
    meta = '<gmlcov:Extension><PlanetServerPDSMetadata xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="http://oderest.rsl.wustl.edu/live/?query=product&amp;results=m&amp;output=XML&amp;pdsid=%s" xlink:type="simple"/></gmlcov:Extension>' % (collname[:-5].lower())
    meta = meta.replace('"', '\\"')
    # delete before add
    psql.do('''DELETE FROM ps_extra_metadata WHERE coverage_id=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);''' % (collname))
    # slice up in pieces
    #splitmeta = [meta[i:i+max] for i in range(0, len(meta), max)]
    # insert first piece
    psql.do('''INSERT INTO ps_extra_metadata (coverage_id, metadata_type_id, value) VALUES (
               (SELECT id FROM ps_coverage WHERE name = \'%s\'), 
               (SELECT id FROM ps_extra_metadata_type WHERE type=\'gmlcov\'),
               \'%s\');''' % (collname, meta))
    #psql.do("INSERT INTO ps_metadata (coverage, metadata) VALUES ((SELECT id FROM ps_coverage WHERE name=\x27%s\x27), \x27%s\x27);" % (collname, meta)) #splitmeta[0]))
    # append rest of pieces
    # for string in splitmeta[1:]:
        # psql.do("UPDATE ps_metadata SET metadata = ((SELECT metadata FROM ps_metadata WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27)) || \x27%s\x27) WHERE coverage=(SELECT id FROM ps_coverage WHERE name=\x27%s\x27);" % (coll,string,coll))
f.close()