import gdal, ogr, osr
from .extent import extent
from .extent_to_geom import extent_to_geom


def extract(img, points, attributes=None):
    """
    Extracts values from raster image at point locations.

    Args:
        img: Input image. Either path to file or gdal raster object.
        points: Spatial points. Either as path to file, ogr data source or layer object.
        attributes: (optional) Include attribute field(s) from points.

    Returns: List of lists of extracted values.

    """

    # check img for type and open as gdal dataset if provided as string
    if isinstance(img, str):
        img = gdal.Open(img)

    gt = img.GetGeoTransform()  # retrieve geo-transform
    band_names = [img.GetRasterBand(i).GetDescription() for i in range(1, img.RasterCount + 1)]  # band names

    if isinstance(points, list):
        values = []
        for point in points:
            mx, my = point[0], point[1]
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel
            values.append([mx, my] + img.ReadAsArray(px, py, 1, 1).flatten().tolist())

    else:
        # read points
        if isinstance(points, str):
            ds = ogr.Open(points)
            lyr = ds.GetLayer()
            ds = None

        elif isinstance(points, ogr.DataSource):
            lyr = points.GetLayer()

        else:
            lyr = points
            points = None

        # layer and raster crs
        lyr_crs = lyr.GetSpatialRef()
        img_crs = osr.SpatialReference(wkt=img.GetProjection())

        # check crs
        if img_crs.GetAuthorityCode(None) == lyr_crs.GetAuthorityCode(None):
            lyr_to_img = False  # crs are identical
        else:
            lyr_to_img = osr.CoordinateTransformation(lyr_crs, img_crs)  # crs transform object
            img_to_lyr = osr.CoordinateTransformation(img_crs, lyr_crs)

        # spatial filter
        ext = extent(img)  # image extent
        ext_geom = extent_to_geom(ext)  # image extent to geometry
        if lyr_to_img:  # transform geometry if crs not identical
            ext_geom.Transform(img_to_lyr)
        lyr.SetSpatialFilter(ext_geom)  # set filter

        # cast attributes to list if necessary
        if attributes:
            if not isinstance(attributes, list):
                attributes = [attributes]
            values = [['x', 'y'] + attributes + band_names]  # initialise return
        else:
            values = [['x', 'y'] + band_names]  # initialise return

        # iterate over point features
        for feat in lyr:

            # retrieve geometry and check if input feature is of type multipoint
            if feat.GetGeometryRef().GetGeometryName() == 'MULTIPOINT':
                geom_ = feat.GetGeometryRef().Clone()
                geom = geom_.GetGeometryRef(0)
            else:
                geom = feat.GetGeometryRef().Clone()

            # apply geo-transform if crs are different
            if lyr_to_img:
                geom.Transform(lyr_to_img)

            # retrieve map coordinates and translate into image offsets
            mx, my = geom.GetX(), geom.GetY()
            px = int((mx - gt[0]) / gt[1])  # x pixel
            py = int((my - gt[3]) / gt[5])  # y pixel

            mx, my = round(mx, 4), round(my, 4)  # round to 4 digits for data frame

            # check if values from attribute fields should be included
            if attributes:
                field_val = [mx, my] + [feat.GetField(a) for a in attributes]
                values.append(field_val + img.ReadAsArray(px, py, 1, 1).flatten().tolist())
            else:
                values.append([mx, my] + img.ReadAsArray(px, py, 1, 1).flatten().tolist())

        # reset layer
        lyr.ResetReading()
        geom = geom_ = None

    return values
