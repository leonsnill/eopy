import ogr, osr


def coords_to_points(coordinates, epsg=4326):
    """
    Create spatial points dataset from list of xy-coordinates.

    :param target_geom:
    :return:
    """
    outDataSource = ogr.GetDriverByName('Memory').CreateDataSource('')

    dest_srs = osr.SpatialReference()
    dest_srs.ImportFromEPSG(epsg)

    outLayer = outDataSource.CreateLayer('', dest_srs, geom_type=ogr.wkbPoint)
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

    return outDataSource
