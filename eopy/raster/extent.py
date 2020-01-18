import gdal


def extent(inp_raster):
    """
    Retrieves the coordinates of the extent of a raster file or finds the common extent of multiple raster files.

    :param inp_raster: (list) List of raster file path(s).
    :return: (list) List of upper left and lower right coordinates.
    """
    ext_ulx, ext_uly = float('-inf'), float('inf')
    ext_lrx, ext_lry = float('inf'), float('-inf')

    for raster in inp_raster:
        raster = gdal.Open(raster, gdal.GA_ReadOnly)
        gt = raster.GetGeoTransform()
        ulx = gt[0]  # upper left x coordinate
        uly = gt[3]  # upper left y coordinate
        lrx = ulx + (gt[1] * raster.RasterXSize)  # upper left x coordinate + number of pixels * pixel size
        lry = uly + (gt[5] * raster.RasterYSize)  # upper left y coordinate + number of pixels * pixel size

        if ulx > ext_ulx:
            ext_ulx = ulx
        if uly < ext_uly:
            ext_uly = uly
        if lrx < ext_lrx:
            ext_lrx = lrx
        if lry > ext_lry:
            ext_lry = lry

    return [ext_ulx, ext_uly, ext_lrx, ext_lry]