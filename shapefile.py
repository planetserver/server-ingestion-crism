import math
import os, sys
try:
    from osgeo import ogr
    from osgeo import osr
    from osgeo import gdal
except:
    try:
        import ogr
        import osr
        import gdal
    except:
        print "No GDAL/OGR available, please install or use f.e. within OSGeo4W Shell"
        sys.exit()

def mean(numbers):
    try:
        summing = float(sum(numbers))
        length = float(len(numbers))
        m = summing / length
    except:
        m = 0
    return m
        
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
        if mode == "read" or mode == "update":
            if mode == "update":
                ds = driver.Open(pathname, 1)
            else:
                ds = driver.Open(pathname, 0)
            if not ds is None:
                layer = ds.GetLayer()
                self.name = layer.GetName()
                type = layer.GetLayerDefn().GetGeomType()
                if type == ogr.wkbPoint:
                    self.type = "point"
                elif type == ogr.wkbPoint25D:
                    self.type = "pointz"
                elif type == ogr.wkbLineString:
                    self.type = "polyline"
                elif type == ogr.wkbLineString25D:
                    self.type = "polylinez"
                elif type == ogr.wkbPolygon:
                    self.type = "polygon"
                elif type == ogr.wkbPolygon25D:
                    self.type = "polygonz"
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
            elif self.type == "pointz":
                self.geom_type = self.ogr.wkbPoint25D
            elif self.type == "polyline":
                self.geom_type = self.ogr.wkbLineString
            elif self.type == "polylinez":
                self.geom_type = self.ogr.wkbLineString25D
            elif self.type == "polygon":
                self.geom_type = self.ogr.wkbPolygon
            elif self.type == "polygonz":
                self.geom_type = self.ogr.wkbPolygon25D
            else:
                # exit
                print "wrong type:", self.type
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
                # http://www.gis.usu.edu/~chrisg/python/2009/lectures/ospy_slides2.pdf#page=27
                if projection[0] == "ESRI":
                    proj_text = projection[1]
                elif projection[0] == "PROJ4":
                    srs = osr.SpatialReference()
                    srs.ImportFromProj4(projection[1])
                    proj_text = srs.ExportToWkt()
                elif projection[0] == "EPSG":
                    srs = osr.SpatialReference()
                    srs.ImportFromEPSG(projection[1])
                    proj_text = srs.ExportToWkt()
                else:
                    print "This projection type is currently not supported"
                    sys.exit()
                file = open(self.dirname + "/" + self.filename[:-3] + "prj","w")
                file.write(proj_text)
                file.close()
                self.projection = ["ESRI", proj_text]
            else:
                self.projection = None
            self.mode = mode
        # field names:
        fieldnames = []
        for field in fieldslist:
            fieldnames.append(field[0])
        self.fieldnames = fieldnames
    def fieldvaluelist(self, fieldname, doubles=1):
        nrfeats = self.layer.GetFeatureCount()
        values = []
        for i in range(nrfeats):
            feat = self.layer.GetFeature(i)
            value = feat.GetField(fieldname)
            if doubles == 1:
                values.append(value)
            else:
                if not value in values:
                    values.append(value)
        return values
    def createfeatfromlist(self, pointslist, attr_dict={}, returnfeat = 0):
        if pointslist != []:
            defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(defn)
            if self.type == "point":
                point = self.ogr.Geometry(self.geom_type)
                point.AddPoint(pointslist[0],pointslist[1])
                feature.SetGeometry(point)
                for item in attr_dict.keys():
                    feature.SetField(item, attr_dict[item])
                self.layer.CreateFeature(feature)
            elif self.type == "polyline":
                polyline = self.ogr.Geometry(self.geom_type)
                for point in pointslist:
                    polyline.AddPoint(point[0],point[1])
                feature.SetGeometryDirectly(polyline)
                for item in attr_dict.keys():
                    if attr_dict[item] == "%LENGTH%":
                        feature.SetField(item, str(round(self.length(pointslist))))
                    else:
                        feature.SetField(item, attr_dict[item])
                self.layer.CreateFeature(feature)
            elif self.type == "polygon":
                ring = self.ogr.Geometry(self.ogr.wkbLinearRing)
                for point in pointslist:
                    ring.AddPoint(point[0],point[1])
                if pointslist[-1] != pointslist[0]:
                    ring.AddPoint(pointslist[0][0],pointslist[0][1])
                polygon = self.ogr.Geometry(self.geom_type)
                polygon.AddGeometry(ring)
                feature.SetGeometryDirectly(polygon)
                for item in attr_dict.keys():
                    if attr_dict[item] == "%AREA%":
                        feature.SetField(item, str(round(polygon.GetArea())))
                    else:
                        feature.SetField(item, attr_dict[item])
                self.layer.CreateFeature(feature)
            if returnfeat == 1:
                return feature
                feature.Destroy()
            else:
                feature.Destroy()
        else:
            print "empty list with attr_dict=" + str(attr_dict)
    def createfeat(self, feat, attr_dict={}):
##        #OLD#
##        defn = self.layer.GetLayerDefn()
##        feature = self.ogr.Feature(defn)
##        geom = feat.GetGeometryRef()
##        feature.SetGeometry(geom)
##        if attr_dict != {}:
##            for item in attr_dict.keys():
##                # TODO: add %LENGTH% and %AREA%
##                feature.SetField(item, attr_dict[item])
##        self.layer.CreateFeature(feature)
##        feat.Destroy()
##        feature.Destroy()
        #NEW#
        if attr_dict == {}:
            self.layer.CreateFeature(feat)
            feat.Destroy()
        else:
            defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(defn)
            geom = feat.GetGeometryRef()
            feature.SetGeometry(geom)
            for item in attr_dict.keys():
                # TODO: add %LENGTH% and %AREA%
                feature.SetField(item, attr_dict[item])
            self.layer.CreateFeature(feature)
            feat.Destroy()
            feature.Destroy()
    def createfeatfromgeom(self, geom, attr_dict={}):
        defn = self.layer.GetLayerDefn()
        feature = self.ogr.Feature(defn)
        feature.SetGeometry(geom)
        if attr_dict != {}:
            for item in attr_dict.keys():
                # TODO: add %LENGTH% and %AREA%
                feature.SetField(item, attr_dict[item])
        self.layer.CreateFeature(feature)
        feature.Destroy()
    def selectfeats(self, fieldname, value):
        self.layer.ResetReading()
        sqlstring = 'SELECT * FROM %s WHERE "%s" = "%s"' % (self.layer.GetName(), fieldname, value)
        layer_select = self.ds.ExecuteSQL(sqlstring)
        return layer_select
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
        attr_dict = {}
        for field in self.fieldslist:
            attr_dict[field[0]] = feat.GetField(field[0])
        featitem.append(attr_dict)
        return featitem
    def attr_dict(self, feat):
        attr_dict = {}
        for field in self.fieldslist:
            attr_dict[field[0]] = feat.GetField(field[0])
        return attr_dict
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
            attr_dict = {}
            for field in self.fieldslist:
                attr_dict[field[0]] = feat.GetField(field[0])
            featitem.append(attr_dict)
            list.append(featitem)
            feat = self.layer.GetNextFeature()
        return list
    def attr2list(self):
        list = []
        self.layer.ResetReading()
        feat = self.layer.GetNextFeature()
        while feat:
            geomstring = str(feat.GetGeometryRef())
            attr_dict = {}
            for field in self.fieldslist:
                attr_dict[field[0]] = feat.GetField(field[0])
            list.append(attr_dict)
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
    def overlaps(self, res, mincount, fieldname=0, quiet=1, intersectgeomlist=0):
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
                        if geom1.Overlaps(geom2):
                            #
                            geom = geom1.Intersection(geom2)
                            STOP = 1
                            drv = ogr.GetDriverByName('Memory')
                            wktds = drv.CreateDataSource('out')
                            wktlyr = wktds.CreateLayer('', None, ogr.wkbPolygon)
                            defn = wktlyr.GetLayerDefn()
                            feature = ogr.Feature(defn)
                            feature.SetGeometry(geom)
                            wktlyr.CreateFeature(feature)
                            (xmin,xmax,ymin,ymax) = wktlyr.GetExtent()
                            nrows = int(abs((ymax - ymin) / res)) + 10
                            ncols = int(abs((xmax - xmin) / res)) + 10
                            geotransform = (xmin,res,0,ymax,0,-res)
                            driver = gdal.GetDriverByName( 'MEM' )  
                            dst_ds = driver.Create( '', ncols, nrows, 1, gdal.GDT_Byte)
                            dst_rb = dst_ds.GetRasterBand(1)
                            dst_rb.Fill(0)
                            dst_rb.SetNoDataValue(0)
                            dst_ds.SetGeoTransform(geotransform)
                            maskvalue = 1
                            gdal.PushErrorHandler( 'CPLQuietErrorHandler' ) ###########
                            err = gdal.RasterizeLayer(dst_ds, [maskvalue], wktlyr)
                            (min, max, buckets, hist) = dst_rb.GetDefaultHistogram()
                            overlapsize = hist[len(hist) - 1]
                            if overlapsize >= mincount:
                                STOP = 0
                            dst_ds.FlushCache()
                            dst_ds = None
                            
                            if STOP == 0:
                                if intersectgeomlist == 1:
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
    def fieldexist(self, fieldname):
        index = self.layer.FindFieldIndex(fieldname, True)
        if index == -1:
            return False
        else:
            return True
    def deletefeat(self, feat_or_id):
        if str(feat_or_id).isdigit():
            self.layer.DeleteFeature(feat_or_id)
        else:
            id = feat_or_id.GetFID()
            self.layer.DeleteFeature(id)
    def extent(self):
        return self.layer.GetExtent()
    #################### CHECK ####################
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
    def buffer(self, feat, bufsize, attr_dict):
        if self.type == "polygon":
            self.defn = self.layer.GetLayerDefn()
            feature = self.ogr.Feature(self.defn)
            polyline = feat.GetGeometryRef()
            polygon = polyline.Buffer(bufsize)
            feature.SetGeometryDirectly(polygon)
            for item in attr_dict.keys():
                if attr_dict[item] == "%AREA%":
                    feature.SetField(item, str(round(polygon.GetArea())))
                else:
                    feature.SetField(item, attr_dict[item])
            self.layer.CreateFeature(feature)
    def cprj(self, projection):
        if projection[0] == "ESRI":
            file = open(self.pathname[:-3] + "prj","w")
            file.write(projection[1])
            file.close()
        
class feature:
    def __init__(self, feat):
        self.feat = feat
    def field(self, fieldname):
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

def poly2linesegments(shp, filename, fid=False):
    if shp.type[-1:] == "z":
        type = "polylinez"
    else:
        type = "polyline"
    if fid != False:
        fieldslist = []
        for item in shp.fieldslist:
            fieldslist.append(item)
        fieldslist.append([fid,0,0,0])
    else:
        fieldslist = shp.fieldslist
        
    shpout = shapefile("write", filename, type, fieldslist, shp.projection)
    for feat in shp.features:
        attr_dict = shp.attr_dict(feat)
        geom = feat.GetGeometryRef()
        if fid != False:
            attr_dict[fid] = feat.GetFID()
        
        if shp.type == "polyline" or shp.type == "polylinez":
            points = geom.GetPointCount()
            for p in range(points)[:-1]:
                x1, y1, z1 = geom.GetPoint(p)
                x2, y2, z2 = geom.GetPoint(p+1)
                polyline = ogr.Geometry(shpout.geom_type)
                polyline.AddPoint(x1, y1, z1)
                polyline.AddPoint(x2, y2, z2)
                shpout.createfeatfromgeom(polyline, attr_dict)
        elif shp.type == "polygon" or shp.type == "polygonz":
            rings = geom.GetGeometryCount()
            for r in range(rings):
                ring = geom.GetGeometryRef(r)
                points = ring.GetPointCount()
                for p in range(points)[:-1]:
                    x1, y1, z1 = ring.GetPoint(p)
                    x2, y2, z2 = ring.GetPoint(p+1)
                    polyline = ogr.Geometry(shpout.geom_type)
                    polyline.AddPoint(x1, y1, z1)
                    polyline.AddPoint(x2, y2, z2)
                    shpout.createfeatfromgeom(polyline, attr_dict)
    shpout.finish()
    print "Saved: " + filename

def EqualSegments(geom1, geom2):
    x1, y1, z1 = geom1.GetPoint(0)
    x2, y2, z2 = geom1.GetPoint(1)
    if geom1.GetGeometryType() == ogr.wkbLineString:
        polyline1 = ogr.Geometry(ogr.wkbLineString)
    else:
        polyline1 = ogr.Geometry(ogr.wkbLineString25D)
    polyline1.AddPoint(x1, y1, z1)
    polyline1.AddPoint(x2, y2, z2)

    x1, y1, z1 = geom2.GetPoint(0)
    x2, y2, z2 = geom2.GetPoint(1)
    if geom2.GetGeometryType() == ogr.wkbLineString:
        polyline2 = ogr.Geometry(ogr.wkbLineString)
    else:
        polyline2 = ogr.Geometry(ogr.wkbLineString25D)
    polyline2.AddPoint(x1, y1, z1)
    polyline2.AddPoint(x2, y2, z2)

    if polyline1.Equal(polyline2):
        return True
    else:
        x1, y1, z1 = geom2.GetPoint(1)
        x2, y2, z2 = geom2.GetPoint(0)
        if geom2.GetGeometryType() == ogr.wkbLineString:
            polyline3 = ogr.Geometry(ogr.wkbLineString)
        else:
            polyline3 = ogr.Geometry(ogr.wkbLineString25D)
        polyline3.AddPoint(x1, y1, z1)
        polyline3.AddPoint(x2, y2, z2)
        if polyline1.Equal(polyline3):
            return True
        else:
            return False
            
def fieldz2geometryz(inshpfile, outshpfile, fieldname):
    shpin = shapefile("read", inshpfile)
    try:
        if not "z" in shpin.type:
            shpout_type = shpin.type + "z"
        else:
            shpout_type = shpin.type
        shpout = shapefile("write", outshpfile, shpout_type, shpin.fieldslist, projection=shpin.projection)
        
        for feat in shpin.features:
            z = feat.GetField(feat.GetFieldIndex(fieldname))
            attr_dict = shpin.attr_dict(feat)
            
            defn = shpout.layer.GetLayerDefn()
            newfeat = ogr.Feature(defn)
            if shpout.type == "pointz":
                geom = feat.GetGeometryRef()
                x = geom.GetX()
                y = geom.GetY()
                
                newpoint = ogr.Geometry(shpout.geom_type)
                newpoint.AddPoint(x, y, z)
                newfeat.SetGeometry(newpoint)
            elif shpout.type == "polylinez":
                polyline = ogr.Geometry(shpout.geom_type)

                geom = feat.GetGeometryRef()
                points = geom.GetPointCount()
                for p in range(points):
                    x, y, zero = geom.GetPoint(p)
                    polyline.AddPoint(x, y, z)
                newfeat.SetGeometryDirectly(polyline)
            elif shpout.type == "polygonz":
                polygon = ogr.Geometry(shpout.geom_type)
                
                geom = feat.GetGeometryRef()
                rings = geom.GetGeometryCount()
                for r in range(rings):
                    ring = geom.GetGeometryRef(r)
                    newring = ogr.Geometry(ogr.wkbLinearRing)
                    points = ring.GetPointCount()
                    for p in range(points):
                        x, y, zero = ring.GetPoint(p)
                        newring.AddPoint(x, y, z)
                    polygon.AddGeometry(newring)
                newfeat.SetGeometryDirectly(polygon)
            shpout.createfeat(newfeat, attr_dict)
        shpin.finish()
        shpout.finish()
    except:
        print "An error occured"
        
def geometryz2fieldz(inshpfile, outshpfile):
    shpin = shapefile("read", inshpfile)
    fieldslist = []
    for i in range(len(shpin.fieldslist)):
        fieldslist.append(shpin.fieldslist[i])
    
    if shpin.type == "pointz":
        fieldname = 'Z'
        fieldslist.append([fieldname, 2, 10, 5])
    else:
        fieldname1 = 'MIN_Z'
        fieldname2 = 'MAX_Z'
        fieldname3 = 'MEAN_Z'

        fieldslist.append([fieldname1, 2, 10, 5])
        fieldslist.append([fieldname2, 2, 10, 5])
        fieldslist.append([fieldname3, 2, 10, 5])

    shpout = shapefile("write", outshpfile, shpin.type, fieldslist, projection=shpin.projection)
        
    for feat in shpin.features:
        zlist = []
        attr_dict = shpin.attr_dict(feat)
        geom = feat.GetGeometryRef()
        if shpout.type == "pointz":
            z = geom.GetZ()
            attr_dict[fieldname] = z
        else:
            if shpout.type == "polylinez":
                points = geom.GetPointCount()
                for p in range(points):
                    x, y, z = geom.GetPoint(p)
                    zlist.append(z)
            elif shpout.type == "polygonz":
                rings = geom.GetGeometryCount()
                for r in range(rings):
                    ring = geom.GetGeometryRef(r)
                    points = ring.GetPointCount()
                    for p in range(points):
                        x, y, z = ring.GetPoint(p)
                        zlist.append(z)
            if not zlist == []:
                attr_dict[fieldname1] = min(zlist)
                attr_dict[fieldname2] = max(zlist)
                attr_dict[fieldname3] = mean(zlist)
            else:
                attr_dict[fieldname1] = 0
                attr_dict[fieldname2] = 0
                attr_dict[fieldname3] = 0
        shpout.createfeat(feat, attr_dict)
    shpin.finish()
    shpout.finish()

def poly2point(inshpfile, outshpfile):
    shpin = shapefile("read", inshpfile)
    
    if shpin.type == "polyline" or shpin.type == "polylinez":
        if shpin.type == "polyline":
            outtype = "point"
        else:
            outtype = "pointz"
        shpout = shapefile("write", outshpfile, outtype, shpin.fieldslist, shpin.projection)
        for feat in shpin.features:
            attr_dict = shpin.attr_dict(feat)
            geom = feat.GetGeometryRef()
            points = geom.GetPointCount()
            for p in range(points):
                x, y, z = geom.GetPoint(p)
                point = ogr.Geometry(shpout.geom_type)
                point.AddPoint(x, y, z)
                defn = shpout.layer.GetLayerDefn()
                feature = ogr.Feature(defn)
                feature.SetGeometry(point)
                shpout.createfeat(feature, attr_dict)
        shpout.finish()
    elif shpin.type == "polygon" or shpin.type == "polygonz":
        if shpin.type == "polygon":
            outtype = "point"
        else:
            outtype = "pointz"
        shpout = shapefile("write", outshpfile, outtype, shpin.fieldslist, shpin.projection)
        for feat in shpin.features:
            attr_dict = shpin.attr_dict(feat)
            geom = feat.GetGeometryRef()
            rings = geom.GetGeometryCount()
            for r in range(rings):
                ring = geom.GetGeometryRef(r)
                points = ring.GetPointCount()
                for p in range(points)[:-1]:
                    x, y, z = ring.GetPoint(p)
                    point = ogr.Geometry(shpout.geom_type)
                    point.AddPoint(x, y, z)
                    defn = shpout.layer.GetLayerDefn()
                    feature = ogr.Feature(defn)
                    feature.SetGeometry(point)
                    shpout.createfeat(feature, attr_dict)
        shpout.finish()
    shpin.finish()
    
def multipoly2poly(inshpfile, outshpfile):
    # http://lists.osgeo.org/pipermail/gdal-dev/2010-December/027041.html
    shpin = shapefile("read", inshpfile)
    shpout = shapefile("write", outshpfile, shpin.type, shpin.fieldslist, shpin.projection)
    
    for feat in shpin.features:
        attr_dict = shpin.attr_dict(feat)
        geom = feat.GetGeometryRef()
        if geom != None:
            if geom.GetGeometryName() == 'MULTIPOLYGON':
                for geom_part in geom:
                    shpout.createfeatfromgeom(geom_part, attr_dict)
            else:
                shpout.createfeatfromgeom(geom, attr_dict)
        else:
            print "Wrong geometry: ", feat.GetFID()
