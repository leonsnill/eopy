import gdal


def array_to_geotiff(inp_array, out_file, inp_gdal=None, gt=None, pj=None, compress=True, gdal_return=False):
    """
    Export numpy array to GeoTiff file by providing either a reference GDAL raster object or GeoTransform and Projection
    information.

    :param inp_array: (ndarray) Input numpy ndarray.
    :param out_file: (str) Filename of GeoTiff with extension, e.g. 'new_file.tif'.
    :param inp_gdal: (gdal raster) Reference GDAL raster object from which to take the GeoTransform and Projection.
    :param gt: (tuple) GDAL GeoTransform tuple (origin x, pixel width, pixel x rotation, origin y, pixel y rotation,
    pixel height).
    :param pj: (str) Target projection in Proj4 format.
    :param compress: (bool) Use data compression in output tiff (default to True).
    :param gdal_return: (bool) If GDAL raster object should be returned (default to False).
    :return: (bool) None (default) / GDAL raster object.
    """
    np2gdal_datatype = {
        "uint8": 1,
        "int8": 1,
        "uint16": 2,
        "int16": 3,
        "uint32": 4,
        "int32": 5,
        "float32": 6,
        "float64": 7,
        "complex64": 10,
        "complex128": 11,
    }

    if len(inp_array.shape) > 2:
        ncol = inp_array.shape[1]
        nrow = inp_array.shape[2]
        zdim = inp_array.shape[0]
    else:
        ncol = inp_array.shape[0]
        nrow = inp_array.shape[1]
        zdim = 1

    if inp_gdal is not None:
        gt = inp_gdal.GetGeoTransform()
        pj = inp_gdal.GetProjection()

    dtype = np2gdal_datatype[str(inp_array.dtype)]
    driver = gdal.GetDriverByName('GTiff')

    if compress:
        dst_dataset = driver.Create(out_file, nrow, ncol, zdim, dtype, options=['COMPRESS=DEFLATE'])
    else:
        dst_dataset = driver.Create(out_file, nrow, ncol, zdim, dtype)

    dst_dataset.SetGeoTransform(gt)
    dst_dataset.SetProjection(pj)

    if len(inp_array.shape) > 2:
        for i in range(zdim):
            w_array = inp_array[i, :, :]
            dst_dataset.GetRasterBand(i+1).WriteArray(w_array)
    else:
        dst_dataset.GetRasterBand(1).WriteArray(inp_array)

    dst_dataset = None

    if gdal_return:
        return gdal.Open(out_file)
