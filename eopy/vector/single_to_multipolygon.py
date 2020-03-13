import ogr


def single_to_multi(lyr):
    multipolygon = ogr.Geometry(ogr.wkbMultiPolygon)

    for feat in lyr:
        geom = feat.GetGeometryRef()
        multipolygon.AddGeometry(geom)

    return multipolygon

