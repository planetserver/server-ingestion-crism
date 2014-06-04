from BeautifulSoup import BeautifulSoup
from urllib import FancyURLopener
import os, sys
class Opener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'

if not os.path.exists("pdssizes"):
    os.makedirs("pdssizes")

out = open("pdssizes/crism_frthrshrl07_size.csv","w")
out.write("URL,SIZE\n")

opener = Opener()

# TRDR data
url = "http://pds-geosciences.wustl.edu/mro/mro-m-crism-3-rdr-targeted-v1/"
data = opener.open(url).read()
soup = BeautifulSoup(data)
href = soup.findAll('a')
totalbytes = 0
for h in href:
    url = "http://pds-geosciences.wustl.edu"
    if "mrocr" in h['href']:
        url2 = url + h['href'] + "trdr/"
        data2 = opener.open(url2).read()
        soup2 = BeautifulSoup(data2)
        href2 = soup2.findAll('a')
        for h2 in href2:
            if "trdr" in h2['href']:
                url3 = url + h2['href']
                data3 = opener.open(url3).read()
                soup3 = BeautifulSoup(data3)
                href3 = soup3.findAll('a')
                for h3 in href3:
                    if not "[To Parent Directory]" in str(h3):
                        url4 = url + h3['href']
                        data4 = opener.open(url4).read()
                        soup4 = BeautifulSoup(data4)
                        href4 = soup4.findAll('a')
                        for h4 in href4:
                            if not "[To Parent Directory]" in str(h4):
                                if h4.contents[0].encode('ascii')[:3] == "frt" or h4.contents[0].encode('ascii')[:3] == "hrl" or h4.contents[0].encode('ascii')[:3] == "hrs":
                                    url5 = url + h4['href']
                                    data5 = opener.open(url5).read()
                                    soup5 = BeautifulSoup(data5)
                                    href5 = soup5.findAll('a')
                                    for h5 in href5:
                                        if not "[To Parent Directory]" in str(h5):
                                            if ".img" in h5['href']:
                                                url6 = url + h5['href']
                                                end = str(soup5).index(str(h5))
                                                start = end - 33
                                                byte = str(soup5)[start:end].strip().split()[3]
                                                line = ",".join([url6.encode("ascii"),byte]) + "\n"
                                                if "07_if" in line:
                                                    out.write(line)
                                                    print url6.encode("ascii"),byte
                                                    totalbytes += int(byte)

# DDR data:
url = "http://pds-geosciences.wustl.edu/mro/mro-m-crism-6-ddr-v1/"
data = opener.open(url).read()
soup = BeautifulSoup(data)
href = soup.findAll('a')
for h in href:
    url = "http://pds-geosciences.wustl.edu"
    if "mrocr" in h['href']:
        url2 = url + h['href'] + "ddr/"
        data2 = opener.open(url2).read()
        soup2 = BeautifulSoup(data2)
        href2 = soup2.findAll('a')
        for h2 in href2:
            if "ddr" in h2['href']:
                url3 = url + h2['href']
                data3 = opener.open(url3).read()
                soup3 = BeautifulSoup(data3)
                href3 = soup3.findAll('a')
                for h3 in href3:
                    if not "[To Parent Directory]" in str(h3):
                        url4 = url + h3['href']
                        data4 = opener.open(url4).read()
                        soup4 = BeautifulSoup(data4)
                        href4 = soup4.findAll('a')
                        for h4 in href4:
                            if not "[To Parent Directory]" in str(h4):
                                if h4.contents[0].encode('ascii')[:3] == "frt" or h4.contents[0].encode('ascii')[:3] == "hrl" or h4.contents[0].encode('ascii')[:3] == "hrs":
                                    url5 = url + h4['href']
                                    data5 = opener.open(url5).read()
                                    soup5 = BeautifulSoup(data5)
                                    href5 = soup5.findAll('a')
                                    for h5 in href5:
                                        if not "[To Parent Directory]" in str(h5):
                                            if ".img" in h5['href']:
                                                url6 = url + h5['href']
                                                end = str(soup5).index(str(h5))
                                                start = end - 33
                                                byte = str(soup5)[start:end].strip().split()[3]
                                                line = ",".join([url6.encode("ascii"),byte]) + "\n"
                                                if "_07_" in line:
                                                    out.write(line)
                                                    print url6.encode("ascii"),byte
                                                    totalbytes += int(byte)

out.close()
print totalbytes
