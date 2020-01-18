import ogr, osr


def coords_to_points(coordinates, outfile, epsg=4326, driver='ESRI Shapefile'):
    """
    Create spatial points dataset from list of xy-coordinates.

    :param target_geom:
    :return:
    """
    outDriver = ogr.GetDriverByName(driver)
    outDataSource = outDriver.CreateDataSource(outfile)

    dest_srs = osr.SpatialReference()
    dest_srs.ImportFromEPSG(epsg)

    outLayer = outDataSource.CreateLayer('Test', dest_srs, geom_type=ogr.wkbPoint)
    outLayer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    featureDefn = outLayer.GetLayerDefn()

    for i, coord in enumerate(coordinates):
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(coord[0], coord[1])

        feat = ogr.Feature(featureDefn)
        feat.SetField('id', i)
        feat.SetGeometry(point)

        outLayer.CreateFeature(feat)

        feat = point = None

    outLayer = None
    outDataSource = None

    return ogr.Open(outfile)


proj = osr.SpatialReference(wkt=landsat.GetProjection())
int(proj.GetAttrValue('AUTHORITY',1))