import math
import os
from osgeo import ogr
from osgeo import osr

class shapefile():
    def __init__(self, mode, pathname, type=0, fieldslist=[], projection=None, ogr=ogr):
        # Check if no path is given, then use os.getcwd()
        self.pathname = pathname
        (dirname, filename) = os.path.split(pathname)
        if dirname == "":
            dirname = os.getcwd()
        self.filename = filename
        self.dirname = dirname
        self.ogr = ogr
        driver = self.ogr.GetDriverByName('ESRI Shapefile')
        if mode == "read" or mode == "append":
            if mode == "append":
                ds = driver.Open(pathname, 1)
            else:
                ds = driver.Open(pathname, 0)
            if not ds is None:
                layer = ds.GetLayer()
                self.name = layer.GetName()
                type = layer.GetLayerDefn().GetGeomType()
                if type == 1:
                    self.type = "point"
                elif type == 2:
                    self.type = "polyline"
                elif type == 3:
                    self.type = "polygon"
                else:
                    self.type = "unknown"
                feat = layer.GetNextFeature()
                layer.ResetReading()
                if not feat is None:
                    geom = feat.GetGeometryRef()
                    if not geom is None:
                        sr = geom.GetSpatialReference()
                        if sr is None:
                            projection = None
                        else:
                            projection = ["ESRI", sr.ExportToWkt()]
                        fieldslist = []
                        for i in range(feat.GetFieldCount()):
                            fielddefn = feat.GetFieldDefnRef(i)
                            fieldslist.append([fielddefn.GetName(),fielddefn.GetType(),fielddefn.GetWidth(),fielddefn.GetPrecision()])
                        self.fieldslist = fieldslist
                        self.projection = projection
                        del feat
                        layer.ResetReading()
                        self.layer = layer
                        self.ds = ds
                        # read featurelist:
                        feat = self.layer.GetNextFeature()
                        featurelist = []
                        while feat:
                            ##featurelist.append(feature(feat))
                            featurelist.append(feat)
                            feat = layer.GetNextFeature()
                        self.features = featurelist
                        self.layer.ResetReading()
                    else:
                        self.type = "shapefile_contains_empty_features"
                else:
                    self.type = "empty_shapefile"
            else:
                self.type = "no_shapefile"
        elif mode == "write":
            self.type = type
            self.fieldslist = fieldslist
            if os.path.exists(pathname):
                driver.DeleteDataSource(pathname)
            self.driver = driver
            ds = driver.CreateDataSource(pathname)
            if self.type == "point":
                self.geom_type = self.ogr.wkbPoint
            elif self.type == "polyline":
                self.geom_type = self.ogr.wkbLineString
            elif self.type == "polygon":
                self.geom_type = self.ogr.wkbPolygon
            else:
                # exit
                print "wrong type"
            self.name = filename[:-4]
            layer = ds.CreateLayer(self.name, None, self.geom_type)
            for field in fieldslist:
                fielddefn = self.ogr.FieldDefn(field[0], field[1])
                if field[2] != 0:
                    fielddefn.SetWidth(field[2])
                if len(field) == 4:
                    if field[3] != 0:
                        fielddefn.SetPrecision(field[3])
                layer.CreateField(fielddefn)
            self.ds = ds
            self.layer = layer
            if projection != None:
                if projection[0] == "ESRI":
                    file = open(self.dirname + "/" + self.filename[:-3] + "prj","w")
                    file.write(projection[1])
                    file.close()
            self.projection = projection
            self.mode = mode
        # field names:
        fieldnames = []
        for field in fieldslist:
            fieldnames.append(field[0])
        self.fieldnames = fieldnames
    def createfeatfromlist(self, pointslist, tabledict={}, returnfeat = 0):
        if pointslist != []:
            defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(defn)
            if self.type == "point":
                point = self.ogr.Geometry(self.geom_type)
                point.AddPoint(pointslist[0],pointslist[1])
                feature.SetGeometry(point)
                for item in tabledict.keys():
                    feature.SetField(item, tabledict[item])
                self.layer.CreateFeature(feature)
            elif self.type == "polyline":
                polyline = self.ogr.Geometry(self.geom_type)
                for point in pointslist:
                    polyline.AddPoint(point[0],point[1])
                feature.SetGeometryDirectly(polyline)
                for item in tabledict.keys():
                    if tabledict[item] == "%LENGTH%":
                        feature.SetField(item, str(round(self.length(pointslist))))
                    else:
                        feature.SetField(item, tabledict[item])
                self.layer.CreateFeature(feature)
            elif self.type == "polygon":
                ring = self.ogr.Geometry(self.ogr.wkbLinearRing)
                for point in pointslist:
                    ring.AddPoint(point[0],point[1])
                if pointslist[len(pointslist) - 1] != pointslist[0]:
                    ring.AddPoint(pointslist[0][0],pointslist[0][1])
                polygon = self.ogr.Geometry(self.geom_type)
                polygon.AddGeometry(ring)
                feature.SetGeometryDirectly(polygon)
                for item in tabledict.keys():
                    if tabledict[item] == "%AREA%":
                        feature.SetField(item, str(round(polygon.GetArea())))
                    else:
                        feature.SetField(item, tabledict[item])
                self.layer.CreateFeature(feature)
            if returnfeat == 1:
                return feature
                feature.Destroy()
            else:
                feature.Destroy()
        else:
            print "empty list with tabledict=" + str(tabledict)
    def createfeat(self, feat, tabledict={}):
##        #OLD#
##        defn = self.layer.GetLayerDefn()
##        feature = self.ogr.Feature(defn)
##        geom = feat.GetGeometryRef()
##        feature.SetGeometry(geom)
##        if tabledict != {}:
##            for item in tabledict.keys():
##                # TODO: add %LENGTH% and %AREA%
##                feature.SetField(item, tabledict[item])
##        self.layer.CreateFeature(feature)
##        feat.Destroy()
##        feature.Destroy()
        #NEW#
        if tabledict == {}:
            self.layer.CreateFeature(feat)
            feat.Destroy()
        else:
            defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(defn)
            geom = feat.GetGeometryRef()
            feature.SetGeometry(geom)
            for item in tabledict.keys():
                # TODO: add %LENGTH% and %AREA%
                feature.SetField(item, tabledict[item])
            self.layer.CreateFeature(feature)
            feat.Destroy()
            feature.Destroy()
    def createfeatfromgeom(self, geom, tabledict={}):
        defn = self.layer.GetLayerDefn()
        feature = self.ogr.Feature(defn)
        feature.SetGeometry(geom)
        if tabledict != {}:
            for item in tabledict.keys():
                # TODO: add %LENGTH% and %AREA%
                feature.SetField(item, tabledict[item])
        self.layer.CreateFeature(feature)
        feature.Destroy()
    def selectfeat(self, fieldname, value):
        #selectlayer = self.ds.ExecuteSQL("select * from " + self.name + " where " + fieldname + " = '" + value + "'")
        self.layer.ResetReading()
        feat = self.layer.GetNextFeature()
        while feat:
            if feat.GetField(fieldname) == value:
                break
            feat = self.layer.GetNextFeature()
        return feat
    def length(self, linelist):
        # calculate length from a geometry line
        length = 0
        start = 1
        for (x,y) in linelist:
            if start != 1:
                length = length + ((y - oy)*(y - oy) + (x - ox)*(x - ox))**0.5
            (ox,oy) = (x,y)
            start = 0
        return length
    def buffer(self, feat, bufsize, tabledict):
        if self.type == "polygon":
            self.defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(self.defn)
            polyline = feat.GetGeometryRef()
            polygon = polyline.Buffer(bufsize)
            feature.SetGeometryDirectly(polygon)
            for item in tabledict.keys():
                if tabledict[item] == "%AREA%":
                    feature.SetField(item, str(round(polygon.GetArea())))
                else:
                    feature.SetField(item, tabledict[item])
            self.layer.CreateFeature(feature)
    def cprj(self, projection):
        if projection[0] == "ESRI":
            file = open(self.pathname[:-3] + "prj","w")
            file.write(projection[1])
            file.close()
    def finish(self):
        self.ds.Destroy()
        del self.ds
    def delete(self):
        self.ds.Destroy()
        del self.ds
        if os.path.exists(self.pathname):
            self.driver.DeleteDataSource(self.pathname)
    def geom2list(self):
        # if geometry empty return = 0
        list = []
        self.layer.ResetReading()
        feat = self.layer.GetNextFeature()
        while feat:
            if self.type == "point":
                point = feat.GetGeometryRef()
                x = point.GetX()
                y = point.GetY()
                list.append((x, y))
            elif self.type == "polyline":
                try:
                    geom = feat.GetGeometryRef()
                    temp = []
                    for nr in range(geom.GetPointCount()):
                        point = geom.GetPoint(nr)
                        x = point[0]
                        y = point[1]
                        temp.append((x, y))
                    list.append(temp)
                except:
                    list.append(0)
            elif self.type == "polygon":
                try:
                    geom = feat.GetGeometryRef().GetGeometryRef(0)
                    temp = []
                    for nr in range(geom.GetPointCount()):
                        point = geom.GetPoint(nr)
                        x = point[0]
                        y = point[1]
                        temp.append((x, y))
                    list.append(temp)
                except:
                    list.append(0)
            feat = self.layer.GetNextFeature()
        return list
    def feat2list(self, feat, keepgeom=0):
        featitem = []
        if keepgeom == 0:
            geomlist = []
            if self.type == "point":
                point = feat.GetGeometryRef()
                x = point.GetX()
                y = point.GetY()
                geomlist.append((x, y))
            elif self.type == "polyline":
                try:
                    geom = feat.GetGeometryRef()
                    for nr in range(geom.GetPointCount()):
                        point = geom.GetPoint(nr)
                        x = point[0]
                        y = point[1]
                        geomlist.append((x, y))
                except:
                    geomlist = 0
            elif self.type == "polygon":
                try:
                    geom = feat.GetGeometryRef().GetGeometryRef(0)
                    for nr in range(geom.GetPointCount()):
                        point = geom.GetPoint(nr)
                        x = point[0]
                        y = point[1]
                        geomlist.append((x, y))
                except:
                    geomlist = 0
            featitem.append(geomlist)
        else:
            if self.type == "point":
                geom = feat.GetGeometryRef()
            elif self.type == "polyline":
                geom = feat.GetGeometryRef()
            elif self.type == "polygon":
                geom = feat.GetGeometryRef().GetGeometryRef(0)
            featitem.append(geom)
        table = {}
        for field in self.fieldslist:
            table[field[0]] = feat.GetField(field[0])
        featitem.append(table)
        return featitem
    def feats2list(self, keepgeom=0):
        list = []
        self.layer.ResetReading()
        feat = self.layer.GetNextFeature()
        while feat:
            featitem = []
            if keepgeom == 0:
                geomlist = []
                if self.type == "point":
                    point = feat.GetGeometryRef()
                    x = point.GetX()
                    y = point.GetY()
                    geomlist.append((x, y))
                elif self.type == "polyline":
                    try:
                        geom = feat.GetGeometryRef()
                        for nr in range(geom.GetPointCount()):
                            point = geom.GetPoint(nr)
                            x = point[0]
                            y = point[1]
                            geomlist.append((x, y))
                    except:
                        geomlist = 0
                elif self.type == "polygon":
                    try:
                        geom = feat.GetGeometryRef().GetGeometryRef(0)
                        for nr in range(geom.GetPointCount()):
                            point = geom.GetPoint(nr)
                            x = point[0]
                            y = point[1]
                            geomlist.append((x, y))
                    except:
                        geomlist = 0
                featitem.append(geomlist)
            else:
                if self.type == "point":
                    geom = feat.GetGeometryRef()
                elif self.type == "polyline":
                    geom = feat.GetGeometryRef()
                elif self.type == "polygon":
                    geom = feat.GetGeometryRef().GetGeometryRef(0)
                featitem.append(geom)
            table = {}
            for field in self.fieldslist:
                table[field[0]] = feat.GetField(field[0])
            featitem.append(table)
            list.append(featitem)
            feat = self.layer.GetNextFeature()
        return list
    def table2list(self):
        list = []
        self.layer.ResetReading()
        feat = self.layer.GetNextFeature()
        while feat:
            geomstring = str(feat.GetGeometryRef())
            table = {}
            for field in self.fieldslist:
                table[field[0]] = feat.GetField(field[0])
            list.append(table)
            feat = self.layer.GetNextFeature()
        return list
    def createfeatsfromlist(self, featlist):
        for item in featlist:
            self.createfeatfromlist(item[0],item[1])
    def overprint(self, string, count):
        if count == 0:
            print string,
        else:
            bs = "\b" * (len(string) + 1)
            string = bs + string
            print string,
    def nrcalcs(self, n):
        if n == 0:
            return 0
        else:
            return n + self.nrcalcs(n - 1) - 1
    def forall(self, method, fieldname=0, quiet=1, intersectgeomlist=0):
        if method in ["Intersect", "Equal", "Disjoint", "Touches", "Crosses", "Within", "Contains", "Overlaps"]:
            nrfeats = self.layer.GetFeatureCount()
            pairs = []
            done = []
            if quiet == 0:
                import sys
                sys.setrecursionlimit(10000000)
                cnt = self.nrcalcs(nrfeats)
                c = 0
            pairs = []
            self.layer.ResetReading()
            #
            if intersectgeomlist == 1:
                geomlist = []
            for i in range(nrfeats):
                for j in range(nrfeats):
                    if i != j:
                        if not j in done:
                            feat1 = self.layer.GetFeature(i)
                            feat2 = self.layer.GetFeature(j)
                            geom1 = feat1.GetGeometryRef()
                            geom2 = feat2.GetGeometryRef()
                            filllist = 0
                            exec("if geom1." + method + "(geom2):filllist = 1")
                            if filllist == 1:
                                #
                                if intersectgeomlist == 1:
                                    geom = geom1.Intersection(geom2)
                                    if fieldname == 0:
                                        geomlist.append(geom)
                                    else:
                                        geomlist.append((geom, (feat1.GetField(fieldname), feat2.GetField(fieldname))))
                                #
                                if fieldname != 0:
                                    feat1name = feat1.GetField(fieldname)
                                    feat2name = feat2.GetField(fieldname)
                                    pairs.append([feat1name,feat2name])
                                else:
                                    pairs.append([i,j])
                            if quiet == 0:
                                self.overprint("Checking " + str(c) + " of " + str(cnt) + " pairs", c)
                                c += 1
                done.append(i)
            dict = {}
            for pair in pairs:
                pair1 = pair[0]
                pair2 = pair[1]
                try:
                    temp = dict[pair1]
                    temp.append(pair2)
                    dict[pair1] = temp
                except:
                    dict[pair1] = [pair2]
                try:
                    temp = dict[pair2]
                    temp.append(pair1)
                    dict[pair2] = temp
                except:
                    dict[pair2] = [pair1]
            if intersectgeomlist == 1:
                return (dict, geomlist)
            else:
                return dict
    def createfield(self, field):
        fielddefn = self.ogr.FieldDefn(field[0], field[1])
        if field[2] != 0:
            fielddefn.SetWidth(field[2])
        if len(field) == 4:
            if field[3] != 0:
                fielddefn.SetPrecision(field[3])
        self.layer.CreateField(fielddefn)
    def updatefield(self, idfeat, fieldname, value):
        if str(idfeat).isdigit():
            feat = self.layer.GetFeature(id)
            feat.SetField(fieldname, value)
            self.layer.SetFeature(feat)
        else:
            idfeat.SetField(fieldname, value)
            self.layer.SetFeature(idfeat)
    def readfield(self, idfeat, fieldname):
        if str(idfeat).isdigit():
            feat = self.layer.GetFeature(id)
            return feat.GetField(fieldname)
        else:
            return idfeat.GetField(idfeat.GetFieldIndex(fieldname))
    def extent(self):
        return self.layer.GetExtent()

# Maybe it needs feature needs to inherit from feat
class feature:
    def __init__(self, feat):
        self.feat = feat
    def field(self,fieldname):
        return self.feat.GetField(self.feat.GetFieldIndex(fieldname))
    def geometry(self):
        return self.feat.GetGeometryRef()
    # def distance(self,feature):
        # geom1 = self.feat.GetGeometryRef()
        # geom2 = feature.feat.GetGeometryRef()
        # return geom1.Distance(geom2)

def pointsf2list(sfname):
    shp = shapefile("read", sfname)
    points = shp.features
    list = []
    for point in points:
        pointx = point.geometry().GetX()
        pointy = point.geometry().GetY()
        list.append([pointx,pointy])
    return list
