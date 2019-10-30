import gdal


def array_to_geotiff(inp_array, out_file, inp_gdal=None, trans=None, proj=None, compress=True, gdal_return=False):
    """
    Export numpy array to GeoTiff.
    :param inp_array: (numpy array)
    :param out_file: (str)
    :param inp_gdal: (gdal raster) Optional. Reference GDAL raster object.
    :param trans: (?) __open__
    :param proj: (str) Target projection in Proj4 format.
    :param compress: (bool) Use data compression in output tiff. Default to True.
    :return: (bool) Returns output GDAL object. Default to False.
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
        trans = inp_gdal.GetGeoTransform()
        proj = inp_gdal.GetProjection()

    dtype = np2gdal_datatype[str(inp_array.dtype)]
    driver = gdal.GetDriverByName('GTiff')
    dst_dataset = driver.Create(out_file, nrow, ncol, zdim, dtype, options=['COMPRESS=DEFLATE'])
    dst_dataset.SetGeoTransform(trans)
    dst_dataset.SetProjection(proj)

    if len(inp_array.shape) > 2:
        for i in range(zdim):
            w_array = inp_array[i, :, :]
            dst_dataset.GetRasterBand(i+1).WriteArray(w_array)
    else:
        dst_dataset.GetRasterBand(1).WriteArray(inp_array)

    dst_dataset = None

    if gdal_return:
        return gdal.Open(out_file)
