import sys
from rasdaman import *

text = '''
rasdaman delete

  rasdelete.py collection_name
'''

if len(sys.argv) == 1:sys.exit()
collection_name = sys.argv[1]

rasql = RasQL()
psql = PsQL()

colls = rasql.out("select r from RAS_COLLECTIONNAMES as r")
if ": " + collection_name in colls:
    rasql.do("drop collection %s" % (collection_name))

c_id = psql.get("select id from PS_Coverage where name = \x27%s\x27" % (collection_name))

if c_id != "(0 rows)":
    x_id = psql.get("select id from PS_domain where coverage = %s and type=1" % (c_id))
    y_id = psql.get("select id from PS_domain where coverage = %s and type=2" % (c_id))
    psql.do("delete from PS_Coverage where id = %s" % (c_id))
    psql.do("delete from PS_CellDomain where coverage = %s" % (c_id))
    psql.do("delete from PS_Domain where coverage = %s" % (c_id))
    psql.do("delete from PS_Range where coverage = %s" % (c_id))
    psql.do("delete from PS_InterpolationSet where coverage = %s" % (c_id))
    psql.do("delete from PS_NullSet where coverage = %s" % (c_id))
    psql.do("delete from PS_CrsDetails where coverage = %s" % (c_id))
    if x_id != "(0 rows)":
        psql.do("delete from PS_crsset where axis = %s" % (x_id))
    if y_id != "(0 rows)":
        psql.do("delete from PS_crsset where axis = %s" % (y_id))
