import gdal


def extent(inp_raster):
    """
    Retrieves the coordinates of the extent of a raster file or finds the common extent of multiple raster files.
    Images must be in the same coordinate system.

    Args:
        inp_raster: List of either path to image file(s) or gdal image object(s).

    Returns: List of upper left and lower right coordinates [xmin, ymax, xmax, ymin]

    """
    # initialise return
    ext_ulx, ext_uly = float('-inf'), float('inf')
    ext_lrx, ext_lry = float('inf'), float('-inf')

    # cast to list if necessary
    if not isinstance(inp_raster, list):
        inp_raster = [inp_raster]

    # iterate over list
    for raster in inp_raster:
        # if provided as image path
        if isinstance(inp_raster, str):
            raster = gdal.Open(raster, gdal.GA_ReadOnly)

        gt = raster.GetGeoTransform()
        ulx = gt[0]  # upper left x coordinate
        uly = gt[3]  # upper left y coordinate
        lrx = ulx + (gt[1] * raster.RasterXSize)  # upper left x coordinate + number of pixels * pixel size
        lry = uly + (gt[5] * raster.RasterYSize)  # upper left y coordinate + number of pixels * pixel size

        # update corner coordinates if needed
        if ulx > ext_ulx:
            ext_ulx = ulx
        if uly < ext_uly:
            ext_uly = uly
        if lrx < ext_lrx:
            ext_lrx = lrx
        if lry > ext_lry:
            ext_lry = lry

    return [ext_ulx, ext_uly, ext_lrx, ext_lry]
