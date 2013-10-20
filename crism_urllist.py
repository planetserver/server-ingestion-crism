import os, sys, glob

sizes = []
urls = []
f = open("pdssizes/crism_frthrshrl07_size.csv","r")
f.readline()
for line in f:
    line = line.strip().split(",")
    url = line[0]
    size = line[1]
    urls.append(url)
    sizes.append(int(size))
f.close()

for productidfile in glob.glob('regions/*.txt'):
    f = open(productidfile,"r")
    o = open('download/' + os.path.basename(productidfile)[:-4] + '_urllist.txt','w')
    sizecnt = 0
    for productid in f:
        productid = productid.strip().lower()[:17]
        if "_if" in productid:
            i = 0
            for url in urls:
                ddrid = productid[:-2] + "de"
                if productid in url or ddrid in url:
                    o.write("%s\n" % (url))
                    o.write("%s\n" % (url[:-4] + ".lbl"))
                    sizecnt += sizes[i]
                i += 1
    f.close()
    o.close()
    print "%s download size: %s GB" % (productidfile[:-4], sizecnt / (1024**3))
