import sys, os, time

class RasQL():
    def __init__(self):
        self.rasdaman_port=7001
        self.rasdaman_database="RASBASE"
        self.rasdaman_user="rasadmin"
        self.rasdaman_password="rasadmin"
        self.rasdamanlogin = "-p %s -d %s --user %s --passwd %s" %(self.rasdaman_port, self.rasdaman_database, self.rasdaman_user, self.rasdaman_password)
        self.writelog("############## " + time.ctime() + " ##############\n")
    def do(self, query):
        command = "rasql -q '%s' %s" %(query, self.rasdamanlogin)
        self.writelog("LINE: " + command)
        p = os.popen(command)
        out = "".join(p.readlines())
        self.writelog(out)
        p.close()
        if "Exception" in out:
            sys.exit()
    def image(self, query, imagename):
        command = "rasql -q '%s' --file %s %s" %(query, imagename, self.rasdamanlogin)
        self.writelog("LINE: " + command)
        p = os.popen(command)
        out = "".join(p.readlines())
        self.writelog(out)
        p.close()
        if "Exception" in out:
            sys.exit()
    def out(self, query):
        command = "rasql -q '%s' --out string %s" %(query, self.rasdamanlogin)
        self.writelog("LINE: " + command)
        p = os.popen(command)
        out = "".join(p.readlines())
        self.writelog(out)
        p.close()
        if "Exception" in out:
            sys.exit()
        else:
            return out
    def writelog(self, text):
        output = open("rasql.log","a")
        output.write(text + "\n")
        output.close()
    def checkcoll(self, coll_name, width, height):
        try:
            # First time running the following line shows an error, then 2 is returned. Then rasdelete.py shows an error...
            collsize = self.out("select sdom(r) from %s as r" %(coll_name))
            b = collsize.index("Query result collection has ") + len("Query result collection has ")
            a = collsize.index(" element(s)")
            if collsize[b:a] == "1":
                b = collsize.index("[") + 1
                a = collsize.index("]")
                collsize = collsize[b:a]
                x,y = collsize.split(",")
                x = int(x.split(":")[1]) + 1
                y = int(y.split(":")[1]) + 1
                if x == width and y == height:
                    return 1
            else:
                return 2
        except:
            return 0

class PsQL():
    def __init__(self):
        self.wcps_db="petascopedb"
        self.wcps_host="localhost"
        self.wcps_port=5432
        self.wcps_user="earthserver"
        self.psqllogin = "-d %s --port %s -U %s -h %s" % (self.wcps_db, self.wcps_port, self.wcps_user, self.wcps_host)
        self.writelog("############## " + time.ctime() + " ##############\n")
    def do(self, query):
        command = 'psql %s -c "%s"' % (self.psqllogin, query)
        self.writelog("LINE: " + command)
        p = os.popen(command)
        out = "".join(p.readlines())
        p.close()
        self.writelog(out)
        if "ERROR" in out:
            sys.exit()
    def get(self, query):
        command = 'psql %s -c "%s" | head -3 | tail -1' % (self.psqllogin, query)
        self.writelog("LINE: " + command)
        p = os.popen(command)
        out = "".join(p.readlines())
        p.close()
        self.writelog(out)
        if "ERROR" in out:
            sys.exit()
        else:
            return out.strip()
    def writelog(self, text):
        output = open("psql.log","a")
        output.write(text + "\n")
        output.close()

