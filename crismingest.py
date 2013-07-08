import os,sys

def ini(filename):
    dict = {}
    inputini = open(filename,"r")
    for line in inputini:
        line = line.strip()
        if not ";" in line:
            line = line.split(" = ")
            dict[line[0]] = line[1]
    inputini.close()
    return dict

name = ini("crismingest.ini")["name"]
datafolder = ini("crismingest.ini")["datafolder"]
crs = ini("crismingest.ini")["crs"]
listfile = os.path.join(datafolder,name,name + "list.txt")

if sys.argv[1] == "-create":
    command = 'python createcrismlist.py %s' % (listfile)
    os.system(command)

    command = 'python createcrismstats.py %s' % (listfile)
    os.system(command)

command = 'python rasimporter.py -l %s' % (listfile)
os.system(command)

command = 'python rascrs.py %s %s' % (listfile, crs)
os.system(command)

command = 'python addcrismmetadata.py %s' % (listfile)
os.system(command)
