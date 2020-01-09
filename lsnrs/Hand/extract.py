import gdal, ogr, osr


def extract(img, points, field=None):
    """

    Parameters
    ----------
    img
    points

    Returns
    -------

    """

    if isinstance(img, str):
        img = gdal.Open(img)

    gt = img.GetGeoTransform()

    values = []

    if isinstance(points, list):
        for point in points:
            mx, my = point[0], point[1]
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel
            values.append(img.ReadAsArray(px, py, 1, 1).flatten())

    else:
        if isinstance(points, str):
            points = ogr.Open(points)

        elif isinstance(points, ogr.DataSource):
            lyr_points = points.GetLayer()

        elif isinstance(points, ogr.Layer):
            lyr_points = points

        else:
            print('points not provided in supported format/type, i.e. string, ogr.DataSource or ogr.Layer')

        # Check Spatial Reference System
        img_crs = img.GetSpatialRef()
        point_crs = lyr_points.GetSpatialRef()

        if img_crs.IsSame(point_crs):
            gtransformer = None
        else:
            gtransformer = osr.CoordinateTransformation(point_crs, img_crs)

        for feat in lyr_points:
            geom = feat.GetGeometryRef().Clone()

            if gtransformer:
                geom.Transform(gtransformer)

            mx, my = geom.GetX(), geom.GetY()
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel

            if field:
                field_val = feat.GetField(field)
                values.append([field_val] + img.ReadAsArray(px, py, 1, 1).flatten().tolist())
            else:
                values.append(img.ReadAsArray(px, py, 1, 1).flatten().tolist())

        points = None
        lyr_points.ResetReading()

    return values

